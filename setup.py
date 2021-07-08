from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("README.md") as f:
    long_description = f.read()

CLASSIFIERS = [
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]

setup(
    name="intake-html-table",
    description="Intake plugin for HTML tables, e.g. index pages from webservers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    maintainer="Compiler",
    maintainer_email="kegan@compiler.la",
    classifiers=CLASSIFIERS,
    project_urls={
        "Source": "https://github.com/compilerla/intake-html-table",
        "Tracker": "https://github.com/compilerla/intake-html-table/issues",
    },
    packages=find_packages(),
    package_dir={"intake-html-table": "intake-html-table"},
    include_package_data=True,
    install_requires=install_requires,
    license="Apache 2.0",
    entry_points={
        "intake.drivers": [
            "apache_dir = intake_html_table.catalog:ApacheDirectoryCatalog",
            "html_table = intake_html_table.source:HtmlTableSource",
        ]
    },
    keywords="intake, catalog",
)
