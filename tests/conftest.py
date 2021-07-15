from pathlib import Path

import pytest


def get_path(path):
    """Get the `path` under the `examples/` directory, with respect to this file."""
    root = Path(__file__).parent
    examples = "./examples"
    if root.joinpath(examples).exists():
        examples = root.joinpath(examples)
    else:
        while root.joinpath("..").exists():
            root = root.joinpath("..")
            if root.joinpath(examples).exists():
                examples = root.joinpath(examples)
                break
        else:
            raise FileNotFoundError("examples/ directory cannot be found")

    return examples.joinpath(path).resolve()


@pytest.fixture
def cat_path():
    yield get_path("cat.yaml")


@pytest.fixture
def document_path():
    """Get the path for the `document.html` example file."""
    yield get_path("document.html")


@pytest.fixture
def table_path():
    """Get the path for the `table.html` example file."""
    yield get_path("table.html")
