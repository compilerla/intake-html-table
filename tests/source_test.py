import pytest

from intake_html_table.source import HtmlTableSource


@pytest.fixture
def example_path(pytestconfig):
    """Factory to get the `path` under the `examples/` directory, with respect to the pytest root path."""
    root = pytestconfig.rootpath
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
            raise RuntimeError("examples/ directory cannot be found")

    def _example_path(path):
        return examples.joinpath(path)

    yield _example_path


@pytest.fixture
def document_source(example_path):
    """Factory for an HtmlTableSource instance for `examples/document.html`."""

    def _document_source(**kwargs):
        return HtmlTableSource(example_path("document.html"), **kwargs)

    yield _document_source


@pytest.fixture
def table_source(example_path):
    """Factory for an HtmlTableSource instance for `examples/table.html`."""

    def _table_source(**kwargs):
        return HtmlTableSource(example_path("table.html"), **kwargs)

    yield _table_source


def test_container(table_source):
    assert table_source().container == "dataframe"
