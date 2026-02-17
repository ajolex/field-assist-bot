"""Whitelisted remote automation jobs triggered from Discord."""

import asyncio
import csv
import json
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.config import settings
from src.integrations.surveycto import SurveyCTOClient
from src.utils.logger import get_logger

log = get_logger("remote_automation")


@dataclass
class AutomationRunResult:
	"""Execution result for a remote automation job."""

	ok: bool
	summary: str
	details: list[str]


class RemoteAutomationService:
	"""Runs approved jobs only; rejects arbitrary command execution."""

	DAILY_DMS_JOB = "scto_dms_daily"

	def __init__(self, survey_client: SurveyCTOClient) -> None:
		"""Initialize with SurveyCTO client and log location."""
		self.survey_client = survey_client
		self.log_path = Path(settings.remote_jobs_log_path)

	def allowed_jobs(self) -> dict[str, str]:
		"""Return whitelisted jobs and human-readable descriptions."""
		return {
			self.DAILY_DMS_JOB: (
				"Run SurveyCTO sctoapi downloads for two forms, then run two Stata master do-files"
			),
		}

	async def run_job(self, *, job_name: str, requester: str) -> AutomationRunResult:
		"""Execute one of the predefined jobs."""
		if job_name != self.DAILY_DMS_JOB:
			return AutomationRunResult(ok=False, summary="Unknown or disallowed job.", details=[])

		details: list[str] = []
		try:
			hh_path = Path(settings.surveycto_household_csv_path)
			biz_path = Path(settings.surveycto_business_csv_path)
			hh_output_folder = hh_path.parent
			biz_output_folder = biz_path.parent
			hh_output_folder.mkdir(parents=True, exist_ok=True)
			biz_output_folder.mkdir(parents=True, exist_ok=True)

			hh_download = await self._run_sctoapi_download(
				form_id=settings.surveycto_form_household_id,
				output_folder=hh_output_folder,
				csv_output_path=hh_path,
			)
			details.append(hh_download)

			biz_download = await self._run_sctoapi_download(
				form_id=settings.surveycto_form_business_id,
				output_folder=biz_output_folder,
				csv_output_path=biz_path,
			)
			details.append(biz_download)

			hh_do = Path(settings.stata_household_master_do_path)
			biz_do = Path(settings.stata_business_master_do_path)

			hh_run = await self._run_stata_do_file(hh_do)
			details.append(hh_run)
			biz_run = await self._run_stata_do_file(biz_do)
			details.append(biz_run)

			result = AutomationRunResult(
				ok=True,
				summary="✅ Job completed: SurveyCTO sctoapi download + Stata pipelines finished.",
				details=details,
			)
			await self._append_log(job_name=job_name, requester=requester, ok=True, details=details)
			return result
		except Exception as error:
			message = f"❌ Job failed: {error}"
			log.error("remote_job.failed", job=job_name, error=str(error))
			await self._append_log(
				job_name=job_name,
				requester=requester,
				ok=False,
				details=details + [str(error)],
			)
			return AutomationRunResult(ok=False, summary=message, details=details)

	async def _run_sctoapi_download(
		self,
		*,
		form_id: str,
		output_folder: Path,
		csv_output_path: Path,
	) -> str:
		if not form_id.strip():
			raise ValueError("SurveyCTO form ID is required for sctoapi.")
		if not settings.surveycto_server_name.strip():
			raise ValueError("SURVEYCTO_SERVER_NAME is required for sctoapi.")
		if not settings.surveycto_username.strip() or not settings.surveycto_password.strip():
			raise ValueError("SURVEYCTO_USERNAME and SURVEYCTO_PASSWORD are required for sctoapi.")

		output_folder.mkdir(parents=True, exist_ok=True)
		started_at = datetime.now(UTC)
		stata_script = self._build_sctoapi_script(form_id=form_id, output_folder=output_folder)
		result = await self._run_stata_script(stata_script, label=f"sctoapi_{form_id}")
		csv_message = self._ensure_csv_output(
			form_id=form_id,
			output_folder=output_folder,
			csv_output_path=csv_output_path,
			started_at=started_at,
		)
		return f"Downloaded {form_id} via sctoapi to {output_folder}: {result}; {csv_message}"

	def _ensure_csv_output(
		self,
		*,
		form_id: str,
		output_folder: Path,
		csv_output_path: Path,
		started_at: datetime,
	) -> str:
		started_ts = started_at.timestamp() - 2
		candidates = [
			output_folder / f"{form_id}_WIDE.csv",
			output_folder / f"{form_id}.csv",
		]

		fresh_csv = next(
			(
				path
				for path in candidates
				if path.exists() and path.stat().st_mtime >= started_ts
			),
			None,
		)

		if fresh_csv is not None:
			if fresh_csv.resolve() != csv_output_path.resolve():
				csv_output_path.parent.mkdir(parents=True, exist_ok=True)
				csv_output_path.write_bytes(fresh_csv.read_bytes())
			return f"csv_ready path={csv_output_path}"

		json_path = output_folder / f"{form_id}.json"
		if not json_path.exists():
			raise FileNotFoundError(
				f"sctoapi output missing CSV and JSON for form '{form_id}' in {output_folder}"
			)

		rows = self._rows_from_scto_json(json_path)
		self._write_rows_csv(rows, csv_output_path)
		return f"csv_built_from_json path={csv_output_path} rows={len(rows)}"

	def _rows_from_scto_json(self, json_path: Path) -> list[dict[str, str]]:
		try:
			payload = json.loads(json_path.read_text(encoding="utf-8"))
		except Exception as error:
			raise RuntimeError(f"Failed parsing sctoapi JSON output: {json_path}") from error

		if isinstance(payload, list):
			raw_rows = payload
		elif isinstance(payload, dict):
			candidate = payload.get("data")
			if not isinstance(candidate, list):
				candidate = payload.get("items")
			raw_rows = candidate if isinstance(candidate, list) else []
		else:
			raw_rows = []

		rows: list[dict[str, str]] = []
		for item in raw_rows:
			if not isinstance(item, dict):
				continue
			normalized: dict[str, str] = {}
			for key, value in item.items():
				if isinstance(value, (dict, list)):
					normalized[str(key)] = json.dumps(value, ensure_ascii=False)
				else:
					normalized[str(key)] = "" if value is None else str(value)
			rows.append(normalized)
		return rows

	def _write_rows_csv(self, rows: list[dict[str, str]], csv_path: Path) -> None:
		csv_path.parent.mkdir(parents=True, exist_ok=True)
		fieldnames: list[str] = []
		seen: set[str] = set()
		for row in rows:
			for key in row:
				if key not in seen:
					seen.add(key)
					fieldnames.append(key)

		with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
			if not fieldnames:
				handle.write("")
				return
			writer = csv.DictWriter(handle, fieldnames=fieldnames)
			writer.writeheader()
			for row in rows:
				writer.writerow({name: row.get(name, "") for name in fieldnames})

	def _build_sctoapi_script(self, *, form_id: str, output_folder: Path) -> str:
		def _stata_escape(value: str) -> str:
			return value.replace('"', '""')

		server = _stata_escape(settings.surveycto_server_name)
		username = _stata_escape(settings.surveycto_username)
		password = _stata_escape(settings.surveycto_password)
		output = _stata_escape(str(output_folder))
		clean_form_id = _stata_escape(form_id)

		return (
			"version 18\n"
			"capture noisily which sctoapi\n"
			"if _rc {\n"
			"    noisily ssc install sctoapi, replace\n"
			"}\n"
			f"sctoapi {clean_form_id}, "
			f"server({server}) "
			f"username({username}) "
			f"password({password}) "
			f"date({settings.surveycto_sctoapi_date}) "
			f"outputfolder(\"{output}\")\n"
			"exit, clear\n"
		)

	async def _run_stata_script(self, script: str, *, label: str) -> str:
		with tempfile.NamedTemporaryFile(
			mode="w",
			suffix=".do",
			prefix=f"{label}_",
			delete=False,
			encoding="utf-8",
		) as handle:
			handle.write(script)
			temp_path = Path(handle.name)

		try:
			return await self._run_stata_do_file(temp_path)
		finally:
			try:
				temp_path.unlink(missing_ok=True)
			except Exception:
				pass

	async def _run_stata_do_file(self, do_file: Path) -> str:
		if not do_file.exists():
			raise FileNotFoundError(f"Stata do-file not found: {do_file}")

		proc = await asyncio.create_subprocess_exec(
			settings.stata_executable,
			"/e",
			"do",
			str(do_file),
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
		)
		try:
			stdout_bytes, stderr_bytes = await asyncio.wait_for(
				proc.communicate(),
				timeout=max(settings.stata_run_timeout_seconds, 60),
			)
		except TimeoutError as error:
			proc.kill()
			await proc.wait()
			raise TimeoutError(
				f"Stata timed out for {do_file.name} after {settings.stata_run_timeout_seconds}s"
			) from error

		stdout_text = stdout_bytes.decode("utf-8", errors="ignore").strip()
		stderr_text = stderr_bytes.decode("utf-8", errors="ignore").strip()
		if proc.returncode != 0:
			raise RuntimeError(
				f"Stata failed for {do_file.name} (code {proc.returncode}). "
				f"stderr: {stderr_text[:500]}"
			)

		preview = stdout_text[:300] if stdout_text else "ok"
		return f"Ran {do_file.name}: {preview}"

	async def _append_log(
		self,
		*,
		job_name: str,
		requester: str,
		ok: bool,
		details: list[str],
	) -> None:
		event = {
			"timestamp": datetime.now(UTC).isoformat(),
			"job_name": job_name,
			"requester": requester,
			"ok": ok,
			"details": details,
		}
		self.log_path.parent.mkdir(parents=True, exist_ok=True)

		def _write() -> None:
			with self.log_path.open("a", encoding="utf-8") as handle:
				handle.write(json.dumps(event, ensure_ascii=False) + "\n")

		await asyncio.to_thread(_write)
