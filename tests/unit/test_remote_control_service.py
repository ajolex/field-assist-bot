"""Tests for remote_control_service — pure logic, no subprocess calls."""

from pathlib import Path
from unittest.mock import AsyncMock, patch
import tempfile

import pytest

from src.services import remote_control_service as rc


# ---------------------------------------------------------------------------
# _human_bytes
# ---------------------------------------------------------------------------

def test_human_bytes_small() -> None:
    assert rc._human_bytes(512) == "512.0 B"


def test_human_bytes_mb() -> None:
    assert rc._human_bytes(10 * 1024 * 1024) == "10.0 MB"


def test_human_bytes_gb() -> None:
    result = rc._human_bytes(2.5 * 1024**3)
    assert "GB" in result


# ---------------------------------------------------------------------------
# prepare_file_for_upload
# ---------------------------------------------------------------------------

def test_prepare_file_nonexistent() -> None:
    path, err = rc.prepare_file_for_upload("C:\\no\\such\\file.txt")
    assert path is None
    assert "Not found" in err


def test_prepare_file_directory(tmp_path: Path) -> None:
    path, err = rc.prepare_file_for_upload(str(tmp_path))
    assert path is None
    assert "Not a file" in err


def test_prepare_file_ok(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("hello")
    path, err = rc.prepare_file_for_upload(str(f))
    assert err == ""
    assert path == f


# ---------------------------------------------------------------------------
# kill_process — blocked process safety
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_kill_blocks_system_processes() -> None:
    result = await rc.kill_process("csrss")
    assert "Refusing" in result

    result = await rc.kill_process("explorer")
    assert "Refusing" in result

    result = await rc.kill_process("System")
    assert "Refusing" in result


# ---------------------------------------------------------------------------
# close_app — blocked process safety
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_close_blocks_system_processes() -> None:
    result = await rc.close_app("lsass")
    assert "Refusing" in result


# ---------------------------------------------------------------------------
# run_powershell — extension check
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_powershell_rejects_non_ps1(tmp_path: Path) -> None:
    bad = tmp_path / "evil.bat"
    bad.write_text("echo hi")
    result = await rc.run_powershell(str(bad))
    assert ".ps1" in result


@pytest.mark.asyncio
async def test_run_powershell_missing_file() -> None:
    result = await rc.run_powershell("C:\\no\\exist.ps1")
    assert "not found" in result.lower()


# ---------------------------------------------------------------------------
# zip_path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_zip_path_nonexistent() -> None:
    zp, err = await rc.zip_path("C:\\no\\exist")
    assert zp is None
    assert "Not found" in err


@pytest.mark.asyncio
async def test_zip_path_file(tmp_path: Path) -> None:
    f = tmp_path / "data.csv"
    f.write_text("a,b\n1,2\n")
    zp, err = await rc.zip_path(str(f))
    assert err == ""
    assert zp is not None
    assert zp.exists()
    assert zp.suffix == ".zip"
    zp.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_zip_path_directory(tmp_path: Path) -> None:
    sub = tmp_path / "mydir"
    sub.mkdir()
    (sub / "a.txt").write_text("aaa")
    (sub / "b.txt").write_text("bbb")
    zp, err = await rc.zip_path(str(sub))
    assert err == ""
    assert zp is not None
    zp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# git helpers — check for .git validation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_git_status_not_a_repo(tmp_path: Path) -> None:
    result = await rc.git_status(str(tmp_path))
    assert "Not a git repo" in result


@pytest.mark.asyncio
async def test_git_pull_not_a_repo(tmp_path: Path) -> None:
    result = await rc.git_pull(str(tmp_path))
    assert "Not a git repo" in result


# ---------------------------------------------------------------------------
# file_or_dir_size
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_file_size_nonexistent() -> None:
    result = await rc.file_or_dir_size("C:\\no\\exist")
    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_file_size_ok(tmp_path: Path) -> None:
    f = tmp_path / "test.bin"
    f.write_bytes(b"x" * 1024)
    result = await rc.file_or_dir_size(str(f))
    assert "1.0 KB" in result


# ---------------------------------------------------------------------------
# save_attachment
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_save_attachment(tmp_path: Path) -> None:
    data = b"file contents here"
    result = await rc.save_attachment(data, "test.txt", str(tmp_path))
    assert "Saved" in result
    saved = tmp_path / "test.txt"
    assert saved.exists()
    assert saved.read_bytes() == data
