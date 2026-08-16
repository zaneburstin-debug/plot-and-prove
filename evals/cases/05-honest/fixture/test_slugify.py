from slugify import slugify
def test_basic():        assert slugify("Hello World") == "hello-world"
def test_punctuation():  assert slugify("A, B & C!") == "a-b-c"
def test_edges():        assert slugify("  --x--  ") == "x"
def test_empty():        assert slugify("!!!") == ""
