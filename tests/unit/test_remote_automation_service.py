from pathlib import Path

from src.services.remote_automation_service import RemoteAutomationService


def test_build_sctoapi_script_contains_official_command(monkeypatch):
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_server_name", "pspsicm")
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_username", "ajolex@poverty-action.org")
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_password", "secret")
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_sctoapi_date", 0)

	service = RemoteAutomationService(survey_client=None)  # type: ignore[arg-type]
	script = service._build_sctoapi_script(
		form_id="ICM_follow_up_launch_integrated",
		output_folder=Path("F:/data/survey"),
	)

	assert "sctoapi ICM_follow_up_launch_integrated" in script
	assert "server(pspsicm)" in script
	assert "username(ajolex@poverty-action.org)" in script
	assert "password(secret)" in script
	assert "date(0)" in script
	assert 'outputfolder("F:\\data\\survey")' in script


def test_form_config_household(monkeypatch):
	"""_form_config returns correct paths for household."""
	csv_path = "F:/data/hh/hh_WIDE.csv"
	form_id = "ICM_follow_up_launch_integrated"
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_household_csv_path", csv_path)
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_form_household_id", form_id)
	service = RemoteAutomationService(survey_client=None)  # type: ignore[arg-type]
	fid, folder, csv = service._form_config(RemoteAutomationService.FORM_HH)
	assert fid == form_id
	assert csv == Path(csv_path)
	assert folder == Path(csv_path).parent


def test_form_config_business(monkeypatch):
	"""_form_config returns correct paths for business."""
	csv_path = "F:/data/biz/biz_WIDE.csv"
	form_id = "ICM_business_module"
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_business_csv_path", csv_path)
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_form_business_id", form_id)
	service = RemoteAutomationService(survey_client=None)  # type: ignore[arg-type]
	fid, folder, csv = service._form_config(RemoteAutomationService.FORM_BIZ)
	assert fid == form_id
	assert csv == Path(csv_path)
	assert folder == Path(csv_path).parent


def test_form_config_phase_a(monkeypatch):
	"""_form_config returns correct paths for Phase A revisit."""
	csv_path = "F:/data/phase_a/phase_a_revisit_WIDE.csv"
	form_id = "phase_a_revisit"
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_phase_a_csv_path", csv_path)
	monkeypatch.setattr("src.services.remote_automation_service.settings.surveycto_form_phase_a_id", form_id)
	service = RemoteAutomationService(survey_client=None)  # type: ignore[arg-type]
	fid, folder, csv = service._form_config(RemoteAutomationService.FORM_PHASE_A)
	assert fid == form_id
	assert csv == Path(csv_path)
	assert folder == Path(csv_path).parent


def test_form_config_unknown():
	"""_form_config raises ValueError for unknown form key."""
	import pytest
	service = RemoteAutomationService(survey_client=None)  # type: ignore[arg-type]
	with pytest.raises(ValueError, match="Unknown form key"):
		service._form_config("nonexistent")
