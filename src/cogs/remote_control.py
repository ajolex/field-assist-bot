"""Remote PC control commands — locked to the private Automations channel.

Security:
- Channel lock: AUTOMATION_CHANNEL_ID (1473271873352499273)
- User lock: SRA_DISCORD_USER_ID (only Aubrey can invoke)
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.config import settings
from src.services import remote_control_service as rc
from src.utils.logger import get_logger

log = get_logger("remote_control_cog")

AUTOMATION_CHANNEL = 1473271873352499273  # fallback if env not set


# ---------------------------------------------------------------------------
# Guard: channel + user check
# ---------------------------------------------------------------------------

def _allowed_channel_id() -> int:
    return settings.automation_channel_id or AUTOMATION_CHANNEL


def _is_authorised(interaction: discord.Interaction) -> str | None:
    """Return an error message if the caller is not authorised, else None."""
    required_channel = _allowed_channel_id()
    if interaction.channel_id != required_channel:
        return f"🔒 This command can only be used in <#{required_channel}>."
    if settings.sra_discord_user_id and interaction.user.id != settings.sra_discord_user_id:
        return "🔒 Only Aubrey can run remote-control commands."
    return None


async def _guard(interaction: discord.Interaction) -> bool:
    """Send ephemeral rejection if not authorised.  Returns True if blocked."""
    msg = _is_authorised(interaction)
    if msg:
        await interaction.response.send_message(msg, ephemeral=True)
        return True
    return False


# ===================================================================
# COG definition with command groups
# ===================================================================

class RemoteControlCog(commands.Cog, name="Remote Control"):
    """Control your PC remotely from Discord."""

    def __init__(self, bot: FieldAssistBot) -> None:
        self.bot = bot

    # ---------------------------------------------------------------
    # /sys status | /sys processes | /sys kill
    # ---------------------------------------------------------------
    sys_group = app_commands.Group(name="sys", description="System monitoring & health")

    @sys_group.command(name="status", description="CPU, RAM, disk usage, uptime")
    async def sys_status(self, interaction: discord.Interaction) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.system_status()
        await interaction.followup.send(result)

    @sys_group.command(name="processes", description="Top processes by CPU usage")
    @app_commands.describe(top_n="Number of processes to show (default 15)")
    async def sys_processes(self, interaction: discord.Interaction, top_n: int = 15) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.list_processes(min(top_n, 50))
        await interaction.followup.send(result)

    @sys_group.command(name="kill", description="Kill a process by name")
    @app_commands.describe(name="Process name (without .exe)")
    async def sys_kill(self, interaction: discord.Interaction, name: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.kill_process(name)
        await interaction.followup.send(result)

    # ---------------------------------------------------------------
    # /file find | /file send | /file save | /file size | /file zip
    # ---------------------------------------------------------------
    file_group = app_commands.Group(name="file", description="File operations")

    @file_group.command(name="find", description="Search for files by name pattern")
    @app_commands.describe(pattern="Filename pattern (e.g. *.do, report*.xlsx)", search_root="Starting folder (default C:\\Users)")
    async def file_find(self, interaction: discord.Interaction, pattern: str, search_root: str = "C:\\Users") -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.find_files(pattern, search_root)
        await interaction.followup.send(result)

    @file_group.command(name="send", description="Upload a file from your PC to Discord")
    @app_commands.describe(path="Full file path on your PC")
    async def file_send(self, interaction: discord.Interaction, path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        file_path, error = rc.prepare_file_for_upload(path)
        if error:
            await interaction.followup.send(error)
            return
        await interaction.followup.send(
            f"📎 `{file_path.name}`",
            file=discord.File(str(file_path)),
        )

    @file_group.command(name="save", description="Save a Discord attachment to your PC")
    @app_commands.describe(url="Attachment URL (right-click → Copy Link)", dest_folder="Destination folder on PC")
    async def file_save(self, interaction: discord.Interaction, url: str, dest_folder: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        # Download the attachment via the URL
        import httpx
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(url)
                resp.raise_for_status()
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to download attachment: {e}")
            return
        filename = url.rsplit("/", 1)[-1].split("?")[0] or "file"
        result = await rc.save_attachment(resp.content, filename, dest_folder)
        await interaction.followup.send(result)

    @file_group.command(name="size", description="Check file or folder size")
    @app_commands.describe(path="File or folder path")
    async def file_size(self, interaction: discord.Interaction, path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.file_or_dir_size(path)
        await interaction.followup.send(result)

    @file_group.command(name="zip", description="Zip a file/folder and send to Discord")
    @app_commands.describe(path="File or folder path to zip")
    async def file_zip(self, interaction: discord.Interaction, path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        zip_path, error = await rc.zip_path(path)
        if error:
            await interaction.followup.send(error)
            return
        try:
            await interaction.followup.send(
                f"📦 `{zip_path.name}`",
                file=discord.File(str(zip_path)),
            )
        finally:
            zip_path.unlink(missing_ok=True)

    # ---------------------------------------------------------------
    # /screenshot
    # ---------------------------------------------------------------
    @app_commands.command(name="screenshot", description="Take and send a screenshot of your PC")
    async def screenshot(self, interaction: discord.Interaction) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        img_path, error = await rc.take_screenshot()
        if error:
            await interaction.followup.send(error)
            return
        try:
            await interaction.followup.send(
                "🖥️ Current screen:",
                file=discord.File(str(img_path)),
            )
        finally:
            img_path.unlink(missing_ok=True)

    # ---------------------------------------------------------------
    # /app open | /app close | /app run
    # ---------------------------------------------------------------
    app_group = app_commands.Group(name="app", description="Application control")

    @app_group.command(name="open", description="Open a file or application")
    @app_commands.describe(path="File or .exe path to open")
    async def app_open(self, interaction: discord.Interaction, path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.open_path(path)
        await interaction.followup.send(result)

    @app_group.command(name="close", description="Gracefully close an application by name")
    @app_commands.describe(name="Process name (without .exe)")
    async def app_close(self, interaction: discord.Interaction, name: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.close_app(name)
        await interaction.followup.send(result)

    @app_group.command(name="run", description="Run a .ps1 PowerShell script from disk")
    @app_commands.describe(script_path="Full path to .ps1 file")
    async def app_run(self, interaction: discord.Interaction, script_path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.run_powershell(script_path)
        await interaction.followup.send(result)

    # ---------------------------------------------------------------
    # /web download | /web ping
    # ---------------------------------------------------------------
    web_group = app_commands.Group(name="web", description="Downloads & web checks")

    @web_group.command(name="download", description="Download a URL to a folder on your PC")
    @app_commands.describe(url="URL to download", dest_folder="Destination folder on PC")
    async def web_download(self, interaction: discord.Interaction, url: str, dest_folder: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.download_url(url, dest_folder)
        await interaction.followup.send(result)

    @web_group.command(name="ping", description="Check if a URL is reachable from your PC")
    @app_commands.describe(url="URL to check")
    async def web_ping(self, interaction: discord.Interaction, url: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.ping_url(url)
        await interaction.followup.send(result)

    # ---------------------------------------------------------------
    # /git status | /git pull
    # ---------------------------------------------------------------
    git_group = app_commands.Group(name="git_ops", description="Git operations")

    @git_group.command(name="status", description="Show git status of a repository")
    @app_commands.describe(repo_path="Path to repository root")
    async def git_status_cmd(self, interaction: discord.Interaction, repo_path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.git_status(repo_path)
        await interaction.followup.send(result)

    @git_group.command(name="pull", description="Git pull in a repository")
    @app_commands.describe(repo_path="Path to repository root")
    async def git_pull_cmd(self, interaction: discord.Interaction, repo_path: str) -> None:
        if await _guard(interaction):
            return
        await interaction.response.defer()
        result = await rc.git_pull(repo_path)
        await interaction.followup.send(result)


async def setup(bot: FieldAssistBot) -> None:
    """Load cog into bot instance."""
    await bot.add_cog(RemoteControlCog(bot))
