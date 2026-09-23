from project_finalizer.cli import main


def test_workflow_version_reports_v2(capsys):
    code = main(["--version"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == "shipgate 2.0.0"
