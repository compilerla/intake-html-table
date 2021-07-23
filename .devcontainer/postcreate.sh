#!/usr/bin/env bash
set -eu

# ensure pip is up to date
python -m pip install --upgrade pip

# install dev requirements
pip install -r .devcontainer/requirements.txt
pip install -r tests/requirements.txt

# install the package
pip install -e .

# initialize hook environments
pre-commit install --install-hooks --overwrite

# manage commit-msg hooks
pre-commit install --hook-type commit-msg
