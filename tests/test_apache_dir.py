from intake_html_table import ApacheDirectoryCatalog


def test_plugin():
    plugin = ApacheDirectoryCatalog

    assert isinstance(plugin.name, str)
    assert isinstance(plugin.version, str)
    assert isinstance(plugin.container, str)

    assert plugin.name == "apache_dir"
    assert plugin.container == "catalog"
