from intake.source import base


class BaseHtmlTableSource(base.DataSource):
    """
    Base class for an in-memory representation of data in an HTML table. This class cannot be used directly.

    Inherit from this class and implement `_find_rows(self, table)` and `_get_record(self, tr)` for new HTML table sources.
    """

    container = "dataframe"
    partition_access = True

    def __init__(self, uri, selector="table", columns=None, **kwargs):
        self._uri = uri
        self._selector = selector
        self._columns = columns

        self._dataframe = None
        self._soup = None
        self._table = None

        super(BaseHtmlTableSource, self).__init__(**kwargs)

    def _close(self):
        self._dataframe = None
        self._soup = None
        self._table = None

    def _load(self):
        """
        Initialize the DataFrame.
        """
        import bs4
        import fsspec

        of = fsspec.open(self._uri, **self.storage_options)
        with of as f:
            self._soup = bs4.BeautifulSoup(f.read(), "html.parser")

        table = self._soup.select_one(self._selector)
        if not table:
            raise RuntimeError(f"Could not find <table> matching selector '{self._selector}' at: {self._uri}")

        self._check_header(table)
        self._table = table
        self._dataframe = self._get_dataframe(table)

    def _check_header(self, table):
        """
        Verifies the expected table header row. Throws RuntimeError for invalid tables.
        """
        if self._columns:
            header = table.find("tr")
            cells = header.find_all(["th", "td"], recursive=False) if header else []

            if len(cells) != len(self._columns):
                raise RuntimeError(f"<table> with unexpected header row at: {self._uri}")

            for i in range(len(self._columns)):
                col = cells[i].get_text()
                if col != self._columns[i]:
                    raise RuntimeError(f"<table> column[{i}] got '{col}', expected '{self._columns[i]}' at: {self._uri}")

    def _find_rows(self, table):
        """
        Get a list of <tr> from a beautifulsoup4 tag representing a <table>.
        """
        raise NotImplementedError("Implement this method in an inherited class.")

    def _get_record(self, tr):
        """
        Create a python dict record from a beautifulsoup4 tag representing a <tr>.
        """
        raise NotImplementedError("Implement this method in an inherited class.")

    def _get_dataframe(self, table):
        """
        Produce the DataFrame from records in table.
        """
        from pandas import DataFrame as df

        record = self._get_record
        rows = self._find_rows
        dataframe = df.from_records

        records = [record(tr) for tr in rows(table)]

        return dataframe(records)

    def _get_schema(self):
        if self._dataframe is None:
            self._load()

        return base.Schema(
            datashape=None,
            dtype=self._dataframe.dtypes,
            shape=self._dataframe.shape,
            npartitions=1,
            extra_metadata={},
        )

    def _get_partition(self, i):
        self._get_schema()
        return self._dataframe

    def read(self):
        self._get_schema()
        return self._dataframe


class HtmlTableSource(BaseHtmlTableSource):
    """
    HTML table to dataframe reader (no partitioning).

    Caches entire dataframe in memory.

    Parameters
    ----------
    uri: str
        Full path to resource containing an HTML table
    infer_header: bool
        True to infer a header from table when no columns are given. Default: True.
    parse_anchors: bool
        True to extract href and target from cells with anchors. Default: True.
    selector: str
        CSS-style selector for the table element. Default: 'table'
    columns: list or None
        List of expected column names. Default: None
    """

    name = "html_table"
    version = "0.0.1"

    def __init__(self, uri, infer_header=True, parse_anchors=True, selector="table", columns=None, **kwargs):
        self.description = f"HTML table <{uri}>"
        self._infer_header = infer_header
        self._parse_anchors = parse_anchors
        super().__init__(uri, selector=selector, columns=columns, **kwargs)

    def _get_header(self):
        """
        Get the header row for this table.
        """
        if self._infer_header and not self._columns:
            # try thead, fallback to first row in table
            row = (self._table.find("thead") or self._table).find("tr")
            header = [cell.get_text().strip() for cell in row.find_all(["th", "td"], recursive=False)] if row else None
            self._columns = header
        elif self._columns:
            header = self._columns
        else:
            header = None
        return header

    def _find_rows(self, table):
        """
        Get top-level table rows with at least one data cell. When a header is defined, only get rows with matching data cells.
        """
        header = self._get_header()
        source = self._table.find("tbody") or self._table

        if header:

            def filter(t):
                return t.name == "tr" and len(t.find_all("td", recursive=False)) == len(header)

        else:

            def filter(t):
                return t.name == "tr" and t.find_all("td", recursive=False)

        return source.find_all(filter, recursive=False)

    def _get_record(self, tr):
        """
        Convert the table row of data into a python dict.
        """
        header = self._get_header()
        cells = tr.find_all("td", recursive=False)

        def key(i):
            return header[i] if header else str(i)

        def value(i):
            from collections import namedtuple

            Anchor = namedtuple("anchor", ("text", "href", "target"))
            cell = cells[i]
            if self._parse_anchors and cell.find("a"):
                a = cell.find("a")
                return Anchor(a.get_text().strip(), a.get("href"), a.get("target"))
            else:
                return cell.get_text().strip()

        if header is None or len(header) == len(cells):
            return {key(i): value(i) for i in range(len(cells))}
        else:
            return None
