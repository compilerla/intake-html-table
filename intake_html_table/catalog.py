from intake.catalog.base import Catalog
from intake.catalog.local import LocalCatalogEntry


class ApacheDirectoryCatalog(Catalog):
    """
    Makes data sources out of an Apache Server Directory index page.

    Subdirectories become ``ApacheDirectoryCatalog`` entries in this catalog.

    Parameters
    ----------
    urlpath: str
        Full path to resource containing an HTML table

    Additional kwargs are passed through to the base Catalog.
    """

    name = "apache_dir"
    version = "0.0.1"
    columns = {"Name": "object", "Last modified": "datetime64", "Size": "string", "Description": "string"}

    def __init__(self, urlpath, **kwargs):
        self.dataframe = None
        self.urlpath = urlpath.rstrip("/")
        self.description = f"Apache server directory <{urlpath}>"
        super(ApacheDirectoryCatalog, self).__init__(**kwargs)

    def _process_row(self, row):
        """
        Parse a single table row from an Apache Server directory page table.
        Return a record like:

        ```python
        {
            "name": "string",
            "modified": "datetime64",
            "size": "int64",
            "description": "string",
            "is_directory": "boolean",
            "full_path": "string"
        }
        ```
        """
        anchor = row.Name

        if not anchor:
            return {}

        path = anchor.href
        full_path = path if path.startswith(self.urlpath) else f"{self.urlpath}/{path}"
        name = path.replace(self.urlpath, "").rstrip("/")
        parent = anchor.text.lower() == "parent directory"
        parent_dir = self.urlpath.rstrip(path)[: self.urlpath.rstrip(path).rindex("/")] + "/" if parent else None
        directory = path.endswith("/")

        return {
            "name": "parent" if parent else name,
            "modified": row._2,
            "size": row.Size.replace("-", ""),
            "description": row.Description,
            "is_directory": directory,
            "full_path": parent_dir if parent else full_path,
        }

    def _file_entry(self, name, urlpath):
        driver = "csv" if urlpath.find(".csv") > -1 else "textfiles"
        description = f"Apache server file <{urlpath}>"
        args = {"urlpath": urlpath}

        return LocalCatalogEntry(name, description, driver, True, args, getenv=False, getshell=False, catalog=self)

    def _subdir_entry(self, path, urlpath):
        description = f"Apache Server directory <{urlpath}>"
        args = {"urlpath": urlpath}
        driver = ApacheDirectoryCatalog.name

        e = LocalCatalogEntry(path, description, driver, True, args, getenv=False, getshell=False, catalog=self)

        e._plugin = [ApacheDirectoryCatalog]
        e.container = "catalog"

        return e

    def _load(self):
        from intake_html_table import HtmlTableSource

        self._entries = {}
        self.dataframe = HtmlTableSource(self.urlpath, columns=list(self.columns.keys())).read().astype(self.columns)

        for row in self.dataframe.itertuples():
            record = self._process_row(row)

            if record["is_directory"]:
                e = self._subdir_entry(record["name"], record["full_path"])
            else:
                e = self._file_entry(record["name"], record["full_path"])

            self._entries[e.name] = e

    def _close(self):
        self.dataframe = None
        return super()._close()

    def read(self):
        if self.dataframe is None:
            self._load()
        return self.dataframe
