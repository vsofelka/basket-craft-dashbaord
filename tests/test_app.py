import pathlib
from streamlit.testing.v1 import AppTest

APP_PATH = pathlib.Path(__file__).parent.parent / "app.py"


def test_title_renders():
    at = AppTest.from_file(str(APP_PATH)).run()
    assert at.title[0].value == "BasketCraft Dashboard"
