import cli
def test_export():
    assert cli.cmd_export("a.txt", "json") == "exported a.txt as json"
