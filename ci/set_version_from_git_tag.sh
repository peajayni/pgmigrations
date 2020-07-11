#!/bin/bash
set -eufx

version=$(git tag | tail -1)

echo "__version__ = \"${version}\"" > pgmigrations/version.py
