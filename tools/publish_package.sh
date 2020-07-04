#!/bin/bash
set -eufx

twine upload --verbose dist/*
