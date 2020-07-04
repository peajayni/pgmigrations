#!/bin/bash
set -eufx

version=$(python setup.py --version)
git tag "${version}"
