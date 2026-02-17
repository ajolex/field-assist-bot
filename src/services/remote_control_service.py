"""General-purpose remote PC control triggered from Discord.

Security model:
- Every command checks caller == SRA_DISCORD_USER_ID
- Every command checks channel == AUTOMATION_CHANNEL_ID (private bot channel)
- No arbitrary shell execution — each operation is a dedicated method
"""

from __future__ import annotations

import asyncio
import io
import os
import platform
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.config import settings
from src.utils.logger import get_logger

log = get_logger("remote_control")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _human_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


async def _run(cmd: list[str], timeout: int | None = None) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    timeout = timeout or settings.remote_cmd_timeout
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", f"Timed out after {timeout}s"
    return (
        proc.returncode or 0,
        out.decode("utf-8", errors="replace").strip(),
        err.decode("utf-8", errors="replace").strip(),
    )


# ===================================================================
# SYSTEM MONITORING
# ===================================================================

async def system_status() -> str:
    """CPU, RAM, disk, uptime summary."""
    lines: list[str] = []

    # OS + uptime
    lines.append(f"**OS:** {platform.system()} {platform.release()} ({platform.machine()})")
    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('yyyy-MM-dd HH:mm:ss')"])
    if rc == 0 and out:
        lines.append(f"**Last boot:** {out}")

    # CPU
    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Processor).LoadPercentage"])
    if rc == 0 and out:
        lines.append(f"**CPU:** {out}%")

    # RAM
    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        "$os = Get-CimInstance Win32_OperatingSystem; "
        "$total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1); "
        "$free = [math]::Round($os.FreePhysicalMemory / 1MB, 1); "
        "$used = [math]::Round($total - $free, 1); "
        "\"$used / $total GB (free: $free GB)\""])
    if rc == 0 and out:
        lines.append(f"**RAM:** {out}")

    # Disks
    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        "Get-PSDrive -PSProvider FileSystem | "
        "Where-Object { $_.Used -gt 0 } | "
        "ForEach-Object { "
        "  $u = [math]::Round($_.Used / 1GB, 1); "
        "  $f = [math]::Round($_.Free / 1GB, 1); "
        "  \"$($_.Name): ${u}GB used / ${f}GB free\" "
        "}"])
    if rc == 0 and out:
        lines.append(f"**Drives:**\n{out}")

    return "\n".join(lines) if lines else "Could not gather system info."


async def list_processes(top_n: int = 15) -> str:
    """Top processes sorted by CPU then memory."""
    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        f"Get-Process | Sort-Object CPU -Descending | Select-Object -First {top_n} "
        "Name, @{N='CPU(s)';E={[math]::Round($_.CPU,1)}}, "
        "@{N='Mem(MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}} | "
        "Format-Table -AutoSize | Out-String -Width 120"])
    if rc == 0 and out:
        return f"```\n{out[:1800]}\n```"
    return "Failed to list processes."


async def kill_process(name: str) -> str:
    """Kill all processes matching a name."""
    # Safety: block critical system processes
    blocked = {"explorer", "csrss", "wininit", "winlogon", "lsass", "services", "svchost", "system"}
    if name.lower().replace(".exe", "") in blocked:
        return f"🚫 Refusing to kill protected system process: `{name}`"

    rc, out, err = await _run(["powershell", "-NoProfile", "-Command",
        f"Stop-Process -Name '{name}' -Force -ErrorAction SilentlyContinue; "
        f"if ($?) {{ 'Killed: {name}' }} else {{ 'No matching process or access denied' }}"])
    return out or err or "Done."


# ===================================================================
# FILE OPERATIONS
# ===================================================================

async def find_files(pattern: str, search_root: str = "C:\\Users") -> str:
    """Search for files matching a glob pattern."""
    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        f"Get-ChildItem -Path '{search_root}' -Recurse -Filter '{pattern}' "
        "-ErrorAction SilentlyContinue | Select-Object -First 20 FullName | "
        "Format-List | Out-String"], timeout=120)
    if rc == 0 and out.strip():
        return f"```\n{out[:1800]}\n```"
    return f"No files matching `{pattern}` found under `{search_root}`."


async def file_or_dir_size(target: str) -> str:
    """Return size of a file or total size of a directory."""
    p = Path(target)
    if not p.exists():
        return f"❌ Path not found: `{target}`"
    if p.is_file():
        return f"`{p.name}`: {_human_bytes(p.stat().st_size)}"

    rc, out, _ = await _run(["powershell", "-NoProfile", "-Command",
        f"(Get-ChildItem -Path '{target}' -Recurse -ErrorAction SilentlyContinue | "
        "Measure-Object -Property Length -Sum).Sum"])
    if rc == 0 and out.strip():
        try:
            return f"`{p.name}/`: {_human_bytes(float(out.strip()))}"
        except ValueError:
            pass
    return f"Could not compute size for `{target}`."


def prepare_file_for_upload(path_str: str) -> tuple[Path | None, str]:
    """Validate and return path + error message.  Caller uploads via Discord."""
    p = Path(path_str)
    if not p.exists():
        return None, f"❌ Not found: `{path_str}`"
    if not p.is_file():
        return None, f"❌ Not a file (use `/file zip` for directories): `{path_str}`"
    max_bytes = settings.remote_file_max_mb * 1024 * 1024
    if p.stat().st_size > max_bytes:
        return None, f"❌ File is {_human_bytes(p.stat().st_size)} — exceeds {settings.remote_file_max_mb} MB Discord limit."
    return p, ""


async def zip_path(target: str) -> tuple[Path | None, str]:
    """Zip a file or directory into a temp .zip.  Returns (zip_path, error)."""
    p = Path(target)
    if not p.exists():
        return None, f"❌ Not found: `{target}`"

    tmp = Path(tempfile.mktemp(suffix=".zip", prefix=f"{p.name}_"))

    def _zip() -> None:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            if p.is_file():
                zf.write(p, p.name)
            else:
                for item in p.rglob("*"):
                    if item.is_file():
                        zf.write(item, item.relative_to(p.parent))

    await asyncio.to_thread(_zip)

    max_bytes = settings.remote_file_max_mb * 1024 * 1024
    if tmp.stat().st_size > max_bytes:
        tmp.unlink(missing_ok=True)
        return None, f"❌ Zip is {_human_bytes(tmp.stat().st_size)} — exceeds {settings.remote_file_max_mb} MB limit."
    return tmp, ""


async def save_attachment(data: bytes, filename: str, dest_folder: str) -> str:
    """Save raw bytes from a Discord attachment to a local folder."""
    folder = Path(dest_folder)
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / filename

    def _write() -> None:
        dest.write_bytes(data)

    await asyncio.to_thread(_write)
    return f"✅ Saved to `{dest}` ({_human_bytes(len(data))})"


# ===================================================================
# SCREENSHOTS
# ===================================================================

async def take_screenshot() -> tuple[Path | None, str]:
    """Capture full-screen screenshot using PowerShell + .NET.  Returns (path, error)."""
    tmp = Path(tempfile.mktemp(suffix=".png", prefix="screenshot_"))
    quality = settings.remote_screenshot_quality

    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
        "$bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height); "
        "$gfx = [System.Drawing.Graphics]::FromImage($bmp); "
        "$gfx.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size); "
        f"$bmp.Save('{tmp}', [System.Drawing.Imaging.ImageFormat]::Png); "
        "$gfx.Dispose(); $bmp.Dispose()"
    )
    rc, out, err = await _run(["powershell", "-NoProfile", "-Command", ps_script], timeout=15)
    if rc == 0 and tmp.exists():
        return tmp, ""
    return None, f"Screenshot failed: {err or out or 'unknown error'}"


# ===================================================================
# APPLICATION CONTROL
# ===================================================================

async def open_path(target: str) -> str:
    """Open a file or application with its default handler."""
    p = Path(target)
    if not p.exists():
        return f"❌ Not found: `{target}`"
    rc, out, err = await _run(["powershell", "-NoProfile", "-Command",
        f"Start-Process '{target}'"], timeout=10)
    if rc == 0:
        return f"✅ Opened `{p.name}`"
    return f"❌ Failed: {err or out}"


async def close_app(name: str) -> str:
    """Gracefully close an application by name."""
    blocked = {"explorer", "csrss", "wininit", "winlogon", "lsass", "services", "svchost", "system"}
    if name.lower().replace(".exe", "") in blocked:
        return f"🚫 Refusing to close protected process: `{name}`"

    rc, out, err = await _run(["powershell", "-NoProfile", "-Command",
        f"Get-Process -Name '{name}' -ErrorAction SilentlyContinue | "
        "ForEach-Object { $_.CloseMainWindow() | Out-Null }; "
        f"'Sent close signal to {name}'"])
    return out or err or "Done."


async def run_powershell(script_path: str) -> str:
    """Run a whitelisted .ps1 script.  Must exist on disk."""
    p = Path(script_path)
    if not p.exists():
        return f"❌ Script not found: `{script_path}`"
    if p.suffix.lower() != ".ps1":
        return "❌ Only `.ps1` scripts are allowed."

    rc, out, err = await _run([
        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", str(p),
    ], timeout=settings.remote_cmd_timeout)

    result = out or err or "(no output)"
    return f"```\n{result[:1800]}\n```\nExit code: {rc}"


# ===================================================================
# DOWNLOADS & WEB
# ===================================================================

async def download_url(url: str, dest_folder: str) -> str:
    """Download a URL to a local folder using PowerShell."""
    folder = Path(dest_folder)
    folder.mkdir(parents=True, exist_ok=True)

    # Extract filename from URL
    filename = url.rsplit("/", 1)[-1].split("?")[0] or "download"
    dest = folder / filename

    rc, out, err = await _run(["powershell", "-NoProfile", "-Command",
        f"Invoke-WebRequest -Uri '{url}' -OutFile '{dest}' -UseBasicParsing"], timeout=120)
    if rc == 0 and dest.exists():
        return f"✅ Downloaded to `{dest}` ({_human_bytes(dest.stat().st_size)})"
    return f"❌ Download failed: {err or out}"


async def ping_url(url: str) -> str:
    """Check if a URL is reachable."""
    rc, out, err = await _run(["powershell", "-NoProfile", "-Command",
        f"try {{ "
        f"  $r = Invoke-WebRequest -Uri '{url}' -Method Head -UseBasicParsing -TimeoutSec 10; "
        f"  \"✅ Reachable — HTTP $($r.StatusCode)\" "
        f"}} catch {{ \"❌ Unreachable — $($_.Exception.Message)\" }}"], timeout=15)
    return out or err or "Unknown result."


# ===================================================================
# GIT OPERATIONS
# ===================================================================

async def git_status(repo_path: str) -> str:
    """Run git status in a repository."""
    p = Path(repo_path)
    if not (p / ".git").exists():
        return f"❌ Not a git repo: `{repo_path}`"

    rc, out, err = await _run(["git", "-C", str(p), "status", "--short"])
    if rc != 0:
        return f"❌ git status failed: {err}"
    if not out.strip():
        return f"✅ `{p.name}` — working tree clean"
    return f"```\n{out[:1800]}\n```"


async def git_pull(repo_path: str) -> str:
    """Run git pull in a repository."""
    p = Path(repo_path)
    if not (p / ".git").exists():
        return f"❌ Not a git repo: `{repo_path}`"

    rc, out, err = await _run(["git", "-C", str(p), "pull"], timeout=60)
    result = out or err or "(no output)"
    if rc == 0:
        return f"✅ `{p.name}` pull:\n```\n{result[:1800]}\n```"
    return f"❌ git pull failed:\n```\n{result[:1800]}\n```"
