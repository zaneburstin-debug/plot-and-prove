import client
def test_display_name():
    client.fetch_user = lambda uid: {"first": "Ada", "last": "Lovelace"}
    assert client.display_name(1) == "Ada Lovelace"
