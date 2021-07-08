from intake.catalog.base import Catalog
from intake.catalog.local import LocalCatalogEntry


class ApacheDirectoryCatalog(Catalog):
    """
    Makes data sources out of an Apache Server Directory index page.

    Subdirectories become ``ApacheDirectoryCatalog`` entries in this catalog.
    """

    name = "apache_dir"
    version = "0.0.1"
    columns = {"Name": "object", "Last modified": "datetime64", "Size": "string", "Description": "string"}

    def __init__(self, urlpath, **kwargs):
        self.dataframe = None
        self.urlpath = urlpath
        self.description = f"Apache server directory <{urlpath}>"
        super(ApacheDirectoryCatalog, self).__init__(**kwargs)

    def _process_row(self, row):
        """
        Parse a single table row from an Apache Server directory page table.
        Return a record like:

        ```python
        {
            "path": "string",
            "modified": "datetime",
            "size": "int64",
            "description": "string",
            "is_directory": "boolean",
            "file_extension": "string"
        }
        ```
        """
        anchor = row.Name

        if not anchor:
            return {}

        parent = anchor.text.lower() == "parent directory"
        path = anchor.href
        directory = path.endswith("/")

        return {
            "path": path if not parent else self.urlpath.rstrip(path)[: self.urlpath.rstrip(path).rindex("/")] + "/",
            "modified": row._2,
            "size": row.Size.replace("-", ""),
            "description": row.Description,
            "is_directory": directory,
            "file_extension": None if (directory or path.find(".") < 0) else path[path.rindex(".") :],  # noqa
        }

    def _path_to_name(self, path):
        return path.rstrip("/")

    def _subdir_entry(self, path, urlpath=None):
        name = self._path_to_name(path)
        urlpath = urlpath or f"{self.urlpath.rstrip('/')}/{path}"
        description = f"Apache Server directory <{urlpath}>"
        args = {"urlpath": urlpath}
        driver = ApacheDirectoryCatalog.name

        e = LocalCatalogEntry(name, description, driver, True, args, getenv=False, getshell=False, catalog=self)

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
                # special handling for the "Parent Directory" entry
                if row.Index == 0:
                    e = self._subdir_entry("parent", record["path"])
                else:
                    e = self._subdir_entry(record["path"])

            self._entries[e.name] = e

    def _close(self):
        self.dataframe = None
        return super()._close()

    def read(self):
        if self.dataframe is None:
            self._load()
        return self.dataframe
