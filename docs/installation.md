# Installation instructions

radtext is compatible with Python 3.6+ and runs on Unix/Linux and macOS/OS X. 
The latest radtext releases are available over [pip](https://pypi.python.org/pypi/radtext).

## pip

Using pip, radtext releases are available as source packages and binary wheels.

```shell
$ pip install -U pip setuptools wheel
$ pip install -U radtext
```

When using pip it is generally recommended to install packages in a virtual environment to avoid modifying system state:

```shell
$ python -m venv radtext_env
$ source radtext_env/bin/activate
$ pip install -U pip setuptools wheel
$ pip install -U radtext
```

## Compile from source

radtext is actively developed on [GitHub repository](https://github.com/bionlplab/radtext).
The other way to install radtext is to clone its GitHub repository.

```shell
$ python -m pip install -U pip setuptools wheel   # install/update build tools
$ git clone https://github.com/bionlplab/radtext  # clone spaCy
$ cd radtext                                      # navigate into dir
$ python -m venv radtext_env                      # create environment in .env
$ source radtext_env/bin/activate                 # activate virtual env
$ pip install -r requirements.txt                 # install requirements
$ python -m build                                 # build the package
$ pip install dist/path/to/wheel                  # install radtext
```

### Unix/Linux

* python >=3.6
* Linux
* Java

Install system-level dependencies via `apt`

```shell
$ sudo apt install install python3 python3-dev build-essential default-java
```

### Windows (experimental)

* python >=3.6, <3.9
* Java
* Microsoft Visual C++ >=14.0

When working on Microsoft Windows OS, some packages requires Microsoft Visual C++ 14.0 or greater. 
You can get it with "Microsoft C++ Build Tools": <https://visualstudio.microsoft.com/visual-cpp-build-tools/>

After install Microsoft Build Tools for Visual Studio, select: Workloads → Desktop development with C++, 
then for Individual Components, select only:

*  Windows SDK 
*  C++ x64/x86 build tools

The build tools allow using MSVC "cl.exe" C / C++ compiler from the command line.

More information can be found at <https://www.scivision.dev/python-windows-visual-c-14-required/>