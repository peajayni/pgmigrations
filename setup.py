from setuptools import setup

with open("requirements.txt") as f:
    REQUIREMENTS = [requirement.strip() for requirement in f.readlines()]

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='pgmigrations',
    version='0.0.1.0',
    packages=["pgmigrations"],
    install_requires=REQUIREMENTS,
    description="SQL migrations for projects using PostgreSQL",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/peajayni/pgmigrations",
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'pgmigrations=pgmigrations.cli:cli',
        ],
    },
)