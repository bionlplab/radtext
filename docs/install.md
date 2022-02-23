# Installation instructions

RadText is compatible with Python (3.6-3.8) and runs on Unix/Linux and macOS/OS X. 
The latest radtext releases are available over
[pypi](https://pypi.python.org/pypi/radtext).

Using pip, RadText releases are available as source packages and binary wheels.
It is also generally recommended installing packages in a virtual
environment to avoid modifying system state:

```shell
$ python -m venv venv
$ source venv/bin/activate
$ pip install -U pip setuptools wheel
$ pip install -U radtext
$ python -m spacy download en_core_web_sm
$ radtext-download --all
```
