import intake
import pandas as pd

from intake_html_table import HtmlTableSource


def test_plugin():
    plugin = HtmlTableSource

    assert isinstance(plugin.name, str)
    assert isinstance(plugin.version, str)
    assert isinstance(plugin.container, str)
    assert isinstance(plugin.partition_access, bool)

    assert plugin.name == "html_table"
    assert plugin.container == "dataframe"
    assert plugin.partition_access is True


def test_open(table_path):
    storage_options = {"storage": "options"}
    metadata = {"meta": "data"}

    src = HtmlTableSource(table_path, storage_options=storage_options, metadata=metadata, extra="kwarg")

    assert src.container == "dataframe"
    assert src.description is None
    assert src.storage_options == storage_options
    assert src.metadata == metadata

    expected = {"urlpath": table_path, "dataframes": None, "kwargs": {"extra": "kwarg"}}

    for attr, value in expected.items():
        assert hasattr(src, attr)
        assert getattr(src, attr) == value


def test_read_single(table_path):
    expected_df = pd.read_html(table_path)[0]

    src = HtmlTableSource(table_path)

    src.discover()
    assert src.npartitions == 1

    df = src.read()
    assert len(src.dataframes) == 1
    assert expected_df.equals(df)


def test_read_multi(document_path):
    expected_df = pd.concat(pd.read_html(document_path))

    src = HtmlTableSource(document_path)

    src.discover()
    assert src.npartitions == 2

    df = src.read()
    assert len(src.dataframes) == 2
    assert expected_df.equals(df)


def test_read_kwargs(document_path):
    attrs = {"id": "data"}
    skiprows = 2
    expected_df = pd.read_html(document_path, attrs=attrs, skiprows=skiprows)[0]

    src = HtmlTableSource(document_path, attrs=attrs, skiprows=skiprows)

    src.discover()
    assert src.npartitions == 1

    df = src.read()
    assert len(src.dataframes) == 1
    assert expected_df.equals(df)


def test_read_partition(document_path):
    example_dfs = pd.read_html(document_path)
    expected_df1 = example_dfs[0]
    expected_df2 = example_dfs[1]

    src = HtmlTableSource(document_path)

    src.discover()
    assert src.npartitions == 2

    # Read partitions is opposite order
    df2 = src.read_partition(1)
    df1 = src.read_partition(0)

    assert expected_df1.equals(df1)
    assert expected_df2.equals(df2)


def test_cat_read_single(cat_path, table_path):
    expected_df = pd.read_html(table_path)[0]

    cat = intake.open_catalog(cat_path)
    assert hasattr(cat, "table_single")

    df = cat.table_single.read()
    assert expected_df.equals(df)


def test_cat_read_multi(cat_path, document_path):
    expected_df = pd.concat(pd.read_html(document_path))

    cat = intake.open_catalog(cat_path)
    assert hasattr(cat, "table_concat")

    df = cat.table_concat.read()
    assert expected_df.equals(df)


def test_cat_read_kwargs(cat_path, document_path):
    attrs = {"id": "data"}
    skiprows = 2
    expected_df = pd.read_html(document_path, attrs=attrs, skiprows=skiprows)[0]

    cat = intake.open_catalog(cat_path)
    assert hasattr(cat, "table_kwargs")

    df = cat.table_kwargs.read()
    assert expected_df.equals(df)


def test_cat_read_partition(cat_path, document_path):
    example_dfs = pd.read_html(document_path)
    expected_df1 = example_dfs[0]
    expected_df2 = example_dfs[1]

    cat = intake.open_catalog(cat_path)
    assert hasattr(cat, "table_concat")

    # Read partitions is opposite order
    df2 = cat.table_concat.read_partition(1)
    df1 = cat.table_concat.read_partition(0)

    assert expected_df1.equals(df1)
    assert expected_df2.equals(df2)
