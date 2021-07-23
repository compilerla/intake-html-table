from pathlib import Path

import pytest


def get_path(path):
    """Get the `path` under the `examples/` directory, with respect to this file."""
    root = Path(__file__).parent
    examples = "../examples"
    return root.joinpath(examples).joinpath(path).resolve()


@pytest.fixture
def cat_path():
    yield get_path("cat.yaml")


@pytest.fixture
def document_path():
    """Get the path for the `document.html` example file."""
    yield get_path("document.html")


@pytest.fixture
def index_path():
    """Get the path for the `index.html` example file."""
    yield get_path("index.html")


@pytest.fixture
def table_path():
    """Get the path for the `table.html` example file."""
    yield get_path("table.html")
