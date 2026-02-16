"""CLI entry point for barangay prefix lookup export."""

import json
from pathlib import Path


def main() -> None:
	"""Generate placeholder barangay lookup mapping."""

	mapping = {
		"H030832": {
			"barangay": "Guinacas",
			"municipality": "Pototan",
			"province": "Iloilo",
		}
	}
	output_path = Path("docs/knowledge_base/brgy_lookup.json")
	output_path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
	print(f"Wrote lookup to {output_path}")


if __name__ == "__main__":
	main()
