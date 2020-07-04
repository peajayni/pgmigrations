import pathlib
import re

from setuptools import setup


def get_version():
    version_path = pathlib.Path("pgmigrations") / "version.py"
    version_text = version_path.read_text()
    version_pattern = r"__version__ = \"(.*)\""
    match = re.search(version_pattern, version_text)
    if not match:
        raise ValueError(f"Could not extract version from: {version_path}")
    return match.group(1)


def get_requirements():
    requirements_text = pathlib.Path("requirements.txt").read_text()
    return [requirement.strip() for requirement in requirements_text.splitlines()]


def get_long_description():
    return pathlib.Path("README.md").read_text()


setup(
    name="pgmigrations",
    version=get_version(),
    packages=["pgmigrations"],
    install_requires=get_requirements(),
    description="SQL migrations for projects using PostgreSQL",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/peajayni/pgmigrations",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["pgmigrations=pgmigrations.cli:cli",],},
    package_data={"pgmigrations": ["bootstrap_migrations/**/*"],},
)
