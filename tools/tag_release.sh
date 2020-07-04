#!/bin/bash
set -eufx

version=$(python setup.py --version)
git tag -a "${version}" -m "Version ${version} - $(date -u)"
