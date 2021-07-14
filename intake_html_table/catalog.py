from collections import namedtuple

from intake.catalog.base import Catalog
from intake.catalog.local import LocalCatalogEntry

import numpy as np


class ApacheDirectoryCatalog(Catalog):
    """
    Makes data sources out of an Apache Server Directory index page.

    Subdirectories become ``ApacheDirectoryCatalog`` entries in this catalog.

    Parameters
    ----------
    urlpath: str
        Full path to resource containing an HTML table
    csv_kwargs: dict
        Keyword configuration for reading CSV files.

    Additional kwargs are passed through to the base Catalog.
    """

    Record = namedtuple("Record", ("name", "modified", "size", "description", "is_directory", "full_path"))

    name = "apache_dir"
    version = "0.0.1"
    columns = {"Name": "string", "Last modified": "datetime64", "Size": "float64", "Description": "string"}

    def __init__(self, urlpath, csv_kwargs={}, **kwargs):
        self.dataframe = None
        self.urlpath = urlpath.rstrip("/")
        self.csv_kwargs = csv_kwargs
        self.description = f"Apache server directory <{urlpath}>"
        super(ApacheDirectoryCatalog, self).__init__(**kwargs)

    def _close(self):
        self.dataframe = None
        return super()._close()

    def _load(self):
        from intake_html_table import HtmlTableSource

        self._entries = {}

        # read and remove rows with all null values (like table separators)
        df = HtmlTableSource(self.urlpath).read().dropna(how="all")

        # fixup sizes
        df["Size"] = df["Size"].apply(self._expand_size)

        # convert to known dtypes
        self.dataframe = df.astype(self.columns)

        # add a catalog entry for each row
        self.dataframe.apply(self._add_entry, axis=1)

    def _expand_size(self, size):
        """
        Expand a value from the Size column from str -> float

        e.g. `"3.3K"` -> `3300.0`
        """
        sizes = {"K": 1000, "M": 1000000, "G": 1000000000}

        try:
            return float(size)
        except ValueError:
            for alpha, mult in sizes.items():
                if size.endswith(alpha):
                    return float(size.rstrip(alpha)) * mult
            else:
                return np.nan

    def _add_entry(self, row):
        """
        Add catalog entries to this catalog for each row. Subdirectory entries
        are handled separately from file entries.
        """
        record = self._process_row(row)

        if record.is_directory:
            e = self._subdir_entry(record.name, record.full_path)
        else:
            e = self._file_entry(record.name, record.full_path)

        self._entries[e.name] = e

    def _process_row(self, row):
        """
        Parse a single table row (as a named tuple) from an Apache Server directory page table.

        Return a named tuple:

        ```python
        (
            name="string",
            modified="string",
            size="float64",
            description="string",
            is_directory="boolean",
            full_path="string"
        )
        ```
        """
        path = row.Name
        full_path = path if path.startswith(self.urlpath) else f"{self.urlpath}/{path}"
        name = path.replace(self.urlpath, "").rstrip("/")
        parent = row.Name.lower() == "parent directory"
        parent_dir = self.urlpath.rstrip(path)[: self.urlpath.rstrip(path).rindex("/")] + "/" if parent else None
        directory = path.endswith("/")

        return ApacheDirectoryCatalog.Record(
            "parent" if parent else name,
            row["Last modified"],
            row.Size,
            row.Description,
            directory,
            parent_dir if parent else full_path,
        )

    def _file_entry(self, name, urlpath):
        """
        Create a `LocalCatalogEntry` for a file.

        `.csv` files are handled by the `csv` driver;
        other file types are handled by the `textfiles` driver
        """
        driver = "csv" if urlpath.find(".csv") > -1 else "textfiles"
        description = f"Apache server file <{urlpath}>"
        args = {"urlpath": urlpath}

        if self.csv_kwargs:
            args["csv_kwargs"] = self.csv_kwargs

        return LocalCatalogEntry(name, description, driver, True, args, getenv=False, getshell=False, catalog=self)

    def _subdir_entry(self, path, urlpath):
        """
        Create a `LocalCatalogEntry` for a subdirectory.

        Use the `ApacheDirectoryCatalog` driver to create a recursive hierarchy.
        """
        description = f"Apache Server directory <{urlpath}>"
        args = {"urlpath": urlpath}
        driver = ApacheDirectoryCatalog.name

        e = LocalCatalogEntry(path, description, driver, True, args, getenv=False, getshell=False, catalog=self)

        e._plugin = [ApacheDirectoryCatalog]
        e.container = "catalog"

        return e

    def read(self):
        if self.dataframe is None:
            self._load()
        return self.dataframe
