import pytest

from intake_html_table import HtmlTableSource

from . import examples


@pytest.fixture
def document_example():
    def _document_example(**kwargs):
        return HtmlTableSource(examples.document_path(), **kwargs)

    yield _document_example


@pytest.fixture
def table_example():
    def _table_example(**kwargs):
        return HtmlTableSource(examples.table_path(), **kwargs)

    yield _table_example


def test_plugin():
    plugin = HtmlTableSource

    assert isinstance(plugin.name, str)
    assert isinstance(plugin.version, str)
    assert isinstance(plugin.container, str)
    assert isinstance(plugin.partition_access, bool)

    assert plugin.name == "html_table"
    assert plugin.container == "dataframe"
    assert plugin.partition_access is True


def test_open(table_example):
    storage_options = {"storage": "options"}
    metadata = {"meta": "data"}

    src = table_example(storage_options=storage_options, metadata=metadata, extra="kwarg")

    assert src.container == "dataframe"
    assert src.description is None
    assert src.storage_options == storage_options
    assert src.metadata == metadata

    expected = {"io": examples.table_path(), "dataframes": None, "kwargs": {"extra": "kwarg"}}

    for attr, value in expected.items():
        assert hasattr(src, attr)
        assert getattr(src, attr) == value
