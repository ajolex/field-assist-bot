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
