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
