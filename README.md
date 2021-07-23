# intake-html-table

![Test coverage percentage](tests/coverage.svg)

[Intake](https://intake.readthedocs.io/) plugin for HTML tables.

## Installation

```bash
pip install -e git+https://github.com/compilerla/intake-html-table@main#egg=intake-html-table
```

Or

```bash
git clone https://github.com/compilerla/intake-html-table
cd intake-html-table/
pip install -e .
```

## Usage

See [examples/notebook.ipynb](./examples/notebook.ipynb) or view on [nbviewer][nbviewer] for more.

### From an [`intake` catalog][intake-cat]

Use the `html_table` driver to read data from HTML tables. Pass additional kwargs to [`pandas.read_html()`][pandas.read_html]:

```yaml
metadata:
  version: 1
sources:
  table:
    description: Read from an HTML table with id=data, skipping the first 2 rows
    driver: html_table
    args:
      urlpath: "https://example.com/"
      attr:
        id: data
      skiprows: 2
```

Use the `apache_dir` driver to read a catalog from an Apache Server directory:

```yaml
metadata:
  version: 1
sources:
  ncei:
    description: National Centers for Environmental Information data catalog
    driver: apache_dir
    args:
      urlpath: "https://www.ncei.noaa.gov/data/"
```

## Tests

Run the test suite (from the root of the repository):

```bash
coverage run -m pytest
```

To view the `coverage` report with indicators for untested (missed) lines:

```bash
coverage report -m
```

To upate the README badge ![Test coverage percentage](tests/coverage.svg) from the latest test run:

```bash
coverage-badge -f -o tests/coverage.svg
```

The `-f` argument ensures the existing badge is overwritten.

Tests also run via [GitHub Action](./.github/workflows/test.yml) on events against the `main` branch.


[intake-cat]: https://intake.readthedocs.io/en/latest/catalog.html#yaml-format
[nbviewer]: https://nbviewer.jupyter.org/github/compilerla/intake-html-table/blob/main/examples/notebook.ipynb
[pandas.read_html]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_html.html?highlight=read_html#pandas.read_html
