from wemo import cli, core


def test_formulate_request():
    core.formulate_request("host", "service", "field")
