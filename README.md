# intake-html-table

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

### Read a simple HTML table

Use a local file path or web URL

```python
from intake_html_table import HtmlTableSource

source = HtmlTableSource("examples/table.html")

df = source.read()

df.info()
```

```console
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 3 entries, 0 to 2
Data columns (total 3 columns):
 #   Column   Non-Null Count  Dtype
---  ------   --------------  -----
 0   Column1  3 non-null      object
 1   Column2  3 non-null      object
 2   Column3  3 non-null      object
dtypes: object(3)
memory usage: 200.0+ bytes
```

```python
df.head()
```

```console
    Column1         Column2         Column3
0   Row1 Column1    Row1 Column2    Row1 Column3
1   Row2 Column1    Row2 Column2    Row2 Column3
2   Row3 Column1    Row3 Column2    Row3 Column3
```

Optionally provide a CSS-style selector for more control over the source table

```python
source = HtmlTableSource("example/table.html", selector="#data")
```

### Read an Apache Server directory

For example, the National Centers for Environmental Information (NCEI) makes data available in an Apache directory structure
at <https://www.ncei.noaa.gov/data>.

The *Global Summary of the Day* is organized by year, with a CSV file for each station for each year at
<https://www.ncei.noaa.gov/data/global-summary-of-the-day/access>.

Here we build a [catalog](https://intake.readthedocs.io/en/latest/catalog.html) from the root of the directory and list the subdirectories

```python
from intake_html_table import ApacheDirectoryCatalog

cat = ApacheDirectoryCatalog("https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/")

list(cat)
```

```console
['parent',
 '1929',
 '1930',
 '1931',
 '1932',
 '1933',
 '1934',
 '1935',
 '1936',
 '1937',
 '1938',
 '1939',
 '1940',
 '1941',
...
]
```

We can list an individual subdirectory as well

```python
list(cat['2021'])
```

```console
['parent',
 '01001099999.csv',
 '01001499999.csv',
 '01002099999.csv',
 '01003099999.csv',
 '01006099999.csv',
 '01007099999.csv',
...
]
```

This directory contains CSV files, and these can be read through the catalog:

```python
df = cat['2021']['01001099999.csv'].read()

df.info()
```

```console
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 184 entries, 0 to 183
Data columns (total 28 columns):
 #   Column            Non-Null Count  Dtype
---  ------            --------------  -----
 0   STATION           184 non-null    int64
 1   DATE              184 non-null    object
 2   LATITUDE          184 non-null    float64
 3   LONGITUDE         184 non-null    float64
 4   ELEVATION         184 non-null    float64
 5   NAME              184 non-null    object
 6   TEMP              184 non-null    float64
 7   TEMP_ATTRIBUTES   184 non-null    int64
 8   DEWP              184 non-null    float64
 9   DEWP_ATTRIBUTES   184 non-null    int64
 10  SLP               184 non-null    float64
 11  SLP_ATTRIBUTES    184 non-null    int64
 12  STP               184 non-null    float64
 13  STP_ATTRIBUTES    184 non-null    int64
 14  VISIB             184 non-null    float64
 15  VISIB_ATTRIBUTES  184 non-null    int64
 16  WDSP              184 non-null    float64
 17  WDSP_ATTRIBUTES   184 non-null    int64
 18  MXSPD             184 non-null    float64
 19  GUST              184 non-null    float64
 20  MAX               184 non-null    float64
 21  MAX_ATTRIBUTES    184 non-null    object
 22  MIN               184 non-null    float64
 23  MIN_ATTRIBUTES    184 non-null    object
 24  PRCP              184 non-null    float64
 25  PRCP_ATTRIBUTES   184 non-null    object
 26  SNDP              184 non-null    float64
 27  FRSHTT            184 non-null    int64
dtypes: float64(15), int64(8), object(5)
memory usage: 40.4+ KB
```
