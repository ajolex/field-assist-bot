"""Probe SurveyCTO cases dataset download."""

import asyncio
from pathlib import Path

from src.config import settings
from src.integrations.surveycto import SurveyCTOClient


async def main() -> None:
	client = SurveyCTOClient()
	try:
		exists = await client.dataset_exists(settings.surveycto_cases_source_id)
		print(f"dataset_exists id={settings.surveycto_cases_source_id} value={exists} (diagnostic)")
		rows = await client.fetch_dataset_csv_rows(
			settings.surveycto_cases_source_id,
			output_path=Path(settings.surveycto_cases_csv_path),
		)
		print(f"download_ok rows={len(rows)}")
		print(f"saved_to={settings.surveycto_cases_csv_path}")
	except Exception as error:
		print(f"download_error type={type(error).__name__} message={error}")


if __name__ == "__main__":
	asyncio.run(main())
