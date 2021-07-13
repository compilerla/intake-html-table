from intake.source import base

import pandas as pd


class HtmlTableSource(base.DataSource):
    """
    HTML to dataframes reader. Tables are read and stored in-memory.

    Partition by individual table(s) read from source.

    Forwards extra keyword arguments to `pandas.read_html()`.
    """

    name = "html_table"
    version = "0.0.1"
    container = "dataframe"
    partition_access = True

    def __init__(self, io, storage_options=None, metadata=None, **kwargs):
        self.io = io
        self.dataframes = None
        self.kwargs = kwargs

        super(HtmlTableSource, self).__init__(storage_options=storage_options, metadata=metadata)

    def _close(self):
        self.dataframes = None

    def _load(self):
        """
        Initialize the DataFrame.
        """
        self.dataframes = pd.read_html(self.io, **self.kwargs)

    def _get_schema(self):
        if self.dataframes is None:
            self._load()

        return base.Schema(
            dtype=None,
            shape=(None,),
            npartitions=len(self.dataframes),
            extra_metadata={},
        )

    def _get_partition(self, i):
        self._load_metadata()
        return self.dataframes[i]

    def read(self):
        self._load_metadata()
        parts = [self.read_partition(i) for i in range(self.npartitions)]
        return pd.concat(parts)
