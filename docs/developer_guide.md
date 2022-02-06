# Developer Guide

## Create this documentation

```bash
$ pip install Sphinx sphinx_rtd_theme recommonmark
$ cd docs
$ make html
```

## Testing the code

```bash
$ python -m pytest tests
```

## Publish BioC to PyPI and TestPyPI

First, you need a PyPI user account. You can create an account using the
form on the PyPI/TestPyPI website.

Now you’ll create a PyPI/TestPyPI API token so you will be able to
securely upload your project.

Go to <https://pypi.org/manage/account/#api-tokens> and create a new API
token; don’t limit its scope to a particular project, since you are
creating a new project.

```shell
$ python -m build
```

Using local package with pip

```shell
$ pip install --force-reinstall dist/PACKAGE.whl
```

Using TestPyPI with pip

```shell
$ twine upload --repository testpypi dist/*
$ pip install --index-url https://test.pypi.org/simple/ radtext
```