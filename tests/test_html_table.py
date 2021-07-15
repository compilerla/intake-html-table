import pandas as pd
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

    expected = {"urlpath": examples.table_path(), "dataframes": None, "kwargs": {"extra": "kwarg"}}

    for attr, value in expected.items():
        assert hasattr(src, attr)
        assert getattr(src, attr) == value


def test_read_single(table_example):
    expected_df = pd.read_html(examples.table_path())[0]

    src = table_example()

    src.discover()
    assert src.npartitions == 1

    df = src.read()
    assert len(src.dataframes) == 1
    assert expected_df.equals(df)


def test_read_multi(document_example):
    expected_df = pd.concat(pd.read_html(examples.document_path()))

    src = document_example()

    src.discover()
    assert src.npartitions == 2

    df = src.read()
    assert len(src.dataframes) == 2
    assert expected_df.equals(df)


def test_read_kwargs(document_example):
    attrs = {"id": "data"}
    skiprows = 2
    expected_df = pd.read_html(examples.document_path(), attrs=attrs, skiprows=skiprows)[0]

    src = document_example(attrs=attrs, skiprows=skiprows)

    src.discover()
    assert src.npartitions == 1

    df = src.read()
    assert len(src.dataframes) == 1
    assert expected_df.equals(df)


def test_read_partition(document_example):
    example_dfs = pd.read_html(examples.document_path())
    expected_df1 = example_dfs[0]
    expected_df2 = example_dfs[1]

    src = document_example()

    src.discover()
    assert src.npartitions == 2

    # Read partitions is opposite order
    df2 = src.read_partition(1)
    df1 = src.read_partition(0)

    assert expected_df1.equals(df1)
    assert expected_df2.equals(df2)
