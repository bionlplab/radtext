# Developer Guide

## Create this documentation

```bash
$ pip install Sphinx sphinx_rtd_theme recommonmark
$ cd docs
$ make html
```

## Testing the code

Install pytest and pytest-cov

```shell
$ pip install pytest pytest-cov
```

Test the code

```shell
$ python -m pytest --cov-report html --cov=radtext tests
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
$ pip install --force-reinstall /path/to/whl
```

Using TestPyPI with pip

```shell
$ twine upload --repository testpypi dist/*
$ pip install --index-url https://test.pypi.org/simple/ radtext
```


## Windows (in progress)

### Prerequisites

*  python >=3.6, <3.9
*  Java
*  Microsoft Visual C++ >=14.0

When working on Microsoft Windows OS, some packages requires Microsoft Visual C++ 14.0 or greater. 
You can get it with "Microsoft C++ Build Tools": <https://visualstudio.microsoft.com/visual-cpp-build-tools/>

After install Microsoft Build Tools for Visual Studio, select: Workloads → Desktop development with C++, 
then for Individual Components, select only:

*  Windows SDK 
*  C++ x64/x86 build tools

The build tools allow using MSVC "cl.exe" C / C++ compiler from the command line.

More information can be found at <https://www.scivision.dev/python-windows-visual-c-14-required/>
