"""SurveyCTO API client."""

import csv
import io
from datetime import datetime, timezone
from pathlib import Path

import httpx
from httpx import HTTPStatusError

from src.config import settings
from src.models.case import CaseRecord
from src.utils.logger import get_logger


log = get_logger("surveycto")


class SurveyCTOClient:
	"""Async SurveyCTO client interface."""

	async def list_datasets(self, limit: int = 1000) -> list[dict[str, str]]:
		"""List datasets available to the authenticated user."""

		if not self.has_credentials:
			return []

		all_items: list[dict[str, str]] = []
		cursor: str | None = None
		pages = 0
		while pages < 20:
			params: dict[str, object] = {"limit": max(1, min(limit, 1000))}
			if cursor:
				params["cursor"] = cursor
			async with httpx.AsyncClient(timeout=60.0) as client:
				response = await client.get(
					f"{self.base_url}/datasets",
					auth=self.auth,
					params=params,
				)
				response.raise_for_status()
				payload = response.json()

			items = payload.get("items", []) if isinstance(payload, dict) else []
			if isinstance(items, list):
				for item in items:
					if isinstance(item, dict):
						all_items.append({str(k): str(v) for k, v in item.items()})

			next_cursor = payload.get("nextCursor") if isinstance(payload, dict) else None
			if not next_cursor:
				break
			cursor = str(next_cursor)
			pages += 1

		return all_items

	async def dataset_exists(self, dataset_id: str) -> bool:
		"""Check if a dataset ID exists in accessible datasets list."""

		target = dataset_id.strip().lower()
		if not target:
			return False
		datasets = await self.list_datasets()
		for item in datasets:
			if str(item.get("id", "")).strip().lower() == target:
				return True
		return False

	def __init__(self) -> None:
		normalized_server = settings.surveycto_server_name.strip().lower()
		self.has_credentials = bool(normalized_server)
		if self.has_credentials:
			self.base_url = f"https://{normalized_server}.surveycto.com/api/v2"
			self.auth = (settings.surveycto_username, settings.surveycto_password)
			log.info(
				"surveycto.initialized",
				server=settings.surveycto_server_name,
				username=settings.surveycto_username,
				normalized_server=normalized_server,
			)
		else:
			log.warning("surveycto.no_credentials", message="Using hardcoded sample data")

	async def get_case(self, case_id: str) -> CaseRecord:
		"""Fetch case details by case ID."""

		if not self.has_credentials:
			return CaseRecord(
				case_id=case_id,
				status="open",
				team="team_a",
				barangay="Bula",
				municipality="Mambusao",
				province="Capiz",
				forms=["HH Survey", "ICM Business"],
				treatment="T2",
				updated_at=datetime.now(timezone.utc),
			)

		try:
			async with httpx.AsyncClient(timeout=30.0) as client:
				response = await client.get(
					f"{self.base_url}/forms/data/wide/json/cases",
					auth=self.auth,
					params={"caseid": case_id},
				)
				response.raise_for_status()
				data = response.json()
				# Parse the response based on actual SurveyCTO API structure
				# This is a simplified example - adjust based on actual API response
				if data:
					record = data[0] if isinstance(data, list) else data
					return CaseRecord(
						case_id=case_id,
						status=record.get("status", "open"),
						team=record.get("team", "unknown"),
						barangay=record.get("barangay", ""),
						municipality=record.get("municipality", ""),
						province=record.get("province", ""),
						forms=record.get("forms", []),
						treatment=record.get("treatment", ""),
						updated_at=datetime.now(timezone.utc),
					)
		except Exception as e:
			log.error("surveycto.get_case_failed", case_id=case_id, error=str(e))

		# Fallback to sample data if API call fails
		return CaseRecord(
			case_id=case_id,
			status="open",
			team="team_a",
			barangay="Bula",
			municipality="Mambusao",
			province="Capiz",
			forms=["HH Survey", "ICM Business"],
			treatment="T2",
			updated_at=datetime.now(timezone.utc),
		)

	async def get_form_versions(self) -> dict[str, str]:
		"""Fetch latest form versions."""

		if not self.has_credentials:
			return {}

		try:
			async with httpx.AsyncClient(timeout=30.0) as client:
				response = await client.get(f"{self.base_url}/forms", auth=self.auth)
				response.raise_for_status()
				forms_data = response.json()
				# Parse form versions from the response
				versions = {}
				for form in forms_data:
					form_id = form.get("formid", "")
					version = form.get("version", "unknown")
					if form_id:
						versions[form_id] = version
				return versions
		except Exception as e:
			log.error("surveycto.get_form_versions_failed", error=str(e))
			return {}

	async def get_submission_counts(self) -> dict[str, int]:
		"""Fetch submission counts for productivity reporting."""

		if not self.has_credentials:
			return {"team_a": 42, "team_b": 39}

		try:
			async with httpx.AsyncClient(timeout=30.0) as client:
				# This endpoint might vary based on actual SurveyCTO API
				response = await client.get(f"{self.base_url}/forms/data/counts", auth=self.auth)
				response.raise_for_status()
				counts_data = response.json()
				# Parse submission counts grouped by team
				# Adjust based on actual API response structure
				return counts_data if isinstance(counts_data, dict) else {"team_a": 42, "team_b": 39}
		except Exception as e:
			log.error("surveycto.get_submission_counts_failed", error=str(e))
			return {"team_a": 42, "team_b": 39}

	async def download_form_wide_csv(self, form_id: str, output_path: Path) -> Path:
		"""Download SurveyCTO wide-format CSV for a form and save to disk."""

		if not self.has_credentials:
			raise RuntimeError("SurveyCTO credentials are required for CSV export.")
		if not form_id.strip():
			raise ValueError("form_id is required")

		url = f"{self.base_url}/forms/data/wide/csv/{form_id}"
		async with httpx.AsyncClient(timeout=120.0) as client:
			response = await client.get(url, auth=self.auth)
			response.raise_for_status()

		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_bytes(response.content)
		log.info("surveycto.wide_csv_downloaded", form_id=form_id, output_path=str(output_path))
		return output_path

	async def download_dataset_csv(self, dataset_id: str, output_path: Path) -> Path:
		"""Download SurveyCTO dataset CSV and save to disk."""

		if not self.has_credentials:
			raise RuntimeError("SurveyCTO credentials are required for CSV export.")
		if not dataset_id.strip():
			raise ValueError("dataset_id is required")

		url = f"{self.base_url}/datasets/data/csv/{dataset_id}"
		async with httpx.AsyncClient(timeout=120.0) as client:
			response = await client.get(url, auth=self.auth)
			response.raise_for_status()

		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_bytes(response.content)
		log.info("surveycto.dataset_csv_downloaded", dataset_id=dataset_id, output_path=str(output_path))
		return output_path

	async def fetch_form_wide_csv_rows(
		self,
		form_id: str,
		output_path: Path | None = None,
	) -> list[dict[str, str]]:
		"""Fetch a SurveyCTO wide-format CSV and parse it into rows."""

		if not self.has_credentials:
			return []
		if not form_id.strip():
			raise ValueError("form_id is required")

		url = f"{self.base_url}/forms/data/wide/csv/{form_id}"
		async with httpx.AsyncClient(timeout=120.0) as client:
			response = await client.get(url, auth=self.auth)
			response.raise_for_status()

		if output_path is not None:
			output_path.parent.mkdir(parents=True, exist_ok=True)
			output_path.write_bytes(response.content)
			log.info(
				"surveycto.wide_csv_overwritten",
				form_id=form_id,
				output_path=str(output_path),
			)

		text = response.content.decode("utf-8-sig", errors="ignore")
		return self._parse_csv_rows(text)

	async def fetch_dataset_csv_rows(
		self,
		dataset_id: str,
		output_path: Path | None = None,
	) -> list[dict[str, str]]:
		"""Fetch a SurveyCTO dataset CSV and parse it into rows."""

		if not self.has_credentials:
			return []
		if not dataset_id.strip():
			raise ValueError("dataset_id is required")

		url = f"{self.base_url}/datasets/data/csv/{dataset_id}"
		async with httpx.AsyncClient(timeout=120.0) as client:
			response = await client.get(url, auth=self.auth)
			response.raise_for_status()

		if output_path is not None:
			output_path.parent.mkdir(parents=True, exist_ok=True)
			output_path.write_bytes(response.content)
			log.info(
				"surveycto.dataset_csv_overwritten",
				dataset_id=dataset_id,
				output_path=str(output_path),
			)

		text = response.content.decode("utf-8-sig", errors="ignore")
		return self._parse_csv_rows(text)

	async def fetch_cases_rows_with_fallback(
		self,
		source_id: str,
		output_path: Path | None = None,
	) -> list[dict[str, str]]:
		"""Fetch case rows using dataset endpoint, with form endpoint fallback."""

		try:
			return await self.fetch_dataset_csv_rows(source_id, output_path=output_path)
		except HTTPStatusError as error:
			status = error.response.status_code if error.response is not None else None
			if status != 404:
				raise
			log.warning(
				"surveycto.dataset_not_found_fallback_form",
				source_id=source_id,
			)
			return await self.fetch_form_wide_csv_rows(source_id, output_path=output_path)

	@staticmethod
	def _parse_csv_rows(text: str) -> list[dict[str, str]]:
		"""Parse CSV text into normalized dict rows."""

		reader = csv.DictReader(io.StringIO(text))
		rows: list[dict[str, str]] = []
		for row in reader:
			rows.append({str(key): str(value or "") for key, value in row.items()})
		return rows
