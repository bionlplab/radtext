# Installation of RadText

This part of the documentation will walk you through the proper installation of RadText.

## Prerequisites

*  python >=3.6
*  Linux
*  Java

## Clone the source code

RadText is actively developed on GitHub, where the code is [always available](https://github.com/yfpeng/radtext).

You can clone the public repository

```bash
$ git clone https://github.com/yfpeng/radtext.git
$ cd radtext
```

Once you have a copy of the source code, you can prepare a virtual environment

```bash
$ conda create --name radtext python=3.6
$ source activate radtext 
$ pip install --upgrade pip setuptools
```

or

```bash
$ virtualenv --python=/usr/bin/python3.6 radtext_env
$ source radtext_env/bin/activate
```

Finally, install the required packages:

```bash
$ pip install -r requirements.txt
```