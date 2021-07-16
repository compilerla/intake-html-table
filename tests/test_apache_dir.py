import intake
import pandas as pd

from intake_html_table import ApacheDirectoryCatalog


def test_plugin():
    plugin = ApacheDirectoryCatalog

    assert isinstance(plugin.name, str)
    assert isinstance(plugin.version, str)
    assert isinstance(plugin.container, str)

    assert plugin.name == "apache_dir"
    assert plugin.container == "catalog"


def test_open(index_path):
    csv_kwargs = {"csv": "kwargs"}
    storage_options = {"storage": "options"}

    index_path = str(index_path).rstrip("/")
    index_path_with_slash = index_path + "/"

    cat = ApacheDirectoryCatalog(index_path_with_slash, csv_kwargs=csv_kwargs, storage_options=storage_options)

    assert cat.container == "catalog"
    assert cat.description is not None
    assert cat.description.find(str(index_path)) > -1
    assert cat.urlpath == index_path
    assert cat.csv_kwargs == csv_kwargs
    assert cat.storage_options == storage_options
    assert isinstance(cat.dataframe, pd.DataFrame)


def test_close(index_path):
    cat = ApacheDirectoryCatalog(index_path)

    cat.close()
    assert cat.dataframe is None


def test_list_root(index_path):
    expected = ["parent", "sub/index.html", "data.csv"]

    cat = ApacheDirectoryCatalog(index_path)

    assert list(cat) == expected


def test_list_sub(index_path):
    expected = ["parent", "data.csv"]

    cat = ApacheDirectoryCatalog(index_path)

    assert "sub/index.html" in cat
    assert list(cat["sub/index.html"]) == expected


def test_list_sub_parent(index_path):
    cat = ApacheDirectoryCatalog(index_path)
    expected = list(cat)

    assert "parent" in cat["sub/index.html"]
    parent = cat["sub/index.html"]["parent"]
    assert list(parent) == expected


def test_read_root_data(index_path):
    cat = ApacheDirectoryCatalog(index_path)
    data_entry = cat["data.csv"]
    expected = pd.read_csv(data_entry.urlpath)

    df = data_entry.read()
    assert expected.equals(df)


def test_read_sub_data(index_path):
    cat = ApacheDirectoryCatalog(index_path)
    data_entry = cat["sub/index.html"]["data.csv"]
    expected = pd.read_csv(data_entry.urlpath)

    df = data_entry.read()
    assert expected.equals(df)


def test_read_sub_parent_data(index_path):
    cat = ApacheDirectoryCatalog(index_path)
    data_entry = cat["sub/index.html"]["parent"]["data.csv"]
    expected = pd.read_csv(data_entry.urlpath)

    df = data_entry.read()
    assert expected.equals(df)


def test_cat_list_root(cat_path):
    expected = ["parent", "sub/index.html", "data.csv"]
    cat = intake.open_catalog(cat_path)

    assert hasattr(cat, "apache_local")
    assert list(cat.apache_local) == expected


def test_cat_list_sub(cat_path):
    expected = ["parent", "data.csv"]
    cat = intake.open_catalog(cat_path).apache_local

    assert list(cat["sub/index.html"]) == expected


def test_cat_list_sub_parent(cat_path):
    cat = intake.open_catalog(cat_path).apache_local

    parent = cat["sub/index.html"]["parent"]
    assert list(parent) == list(cat)


def test_cat_read_root_data(cat_path):
    cat = intake.open_catalog(cat_path).apache_local
    data_entry = cat["data.csv"]
    expected = pd.read_csv(data_entry.urlpath)

    df = data_entry.read()
    assert expected.equals(df)


def test_cat_read_sub_data(cat_path):
    cat = intake.open_catalog(cat_path).apache_local
    data_entry = cat["sub/index.html"]["data.csv"]
    expected = pd.read_csv(data_entry.urlpath)

    df = data_entry.read()
    assert expected.equals(df)


def test_cat_read_sub_parent_data(cat_path):
    cat = intake.open_catalog(cat_path).apache_local
    data_entry = cat["sub/index.html"]["parent"]["data.csv"]
    expected = pd.read_csv(data_entry.urlpath)

    df = data_entry.read()
    assert expected.equals(df)
