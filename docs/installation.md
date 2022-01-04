# Installation of NegBio

This part of the documentation covers the installation of NegBio. The first step to using any software package is getting it properly installed.

## Prerequisites

*  python >=3.6
*  Linux
*  Java

Note: since v1.0, MetaMap is not required. You can use the vocabularies (e.g., ``patterns/cxr14_phrases_v2.yml``) instead.


## Installation of MetaMap

**If you want to use MetaMap to extract findings!!!**

1. Download [MetaMap full version ](https://metamap.nlm.nih.gov/MainDownload.shtml) and extract inot the directory called `public_mm`.

2. Install MetaMap locally. Installation instructions can be found at [https://metamap.nlm.nih.gov/Installation.shtml](https://metamap.nlm.nih.gov/Installation.shtml).

    ```bash
    cd public_mm
    ./bin/install.sh
    ```

3. Start the server.

    ```bash
    ./bin/skrmedpostctl start
    ./bin/wsdserverctl start
    ```

## Getting the source code

NegBio is actively developed on GitHub, where the code is [always available](https://github.com/yfpeng/negbio2).

You can clone the public repository

```bash
$ git clone https://github.com/ncbi-nlp/NegBio.git
$ cd negbio
```

Once you have a copy of the source, you can prepare a virtual environment

```bash
$ conda create --name negbio python=3.6
$ source activate negbio
$ pip install --upgrade pip setuptools
```

or

```bash
$ virtualenv --python=/usr/bin/python3.6 negbio_env
$ source negbio_env/bin/activate
```

Finally, you can install the required packages:

```bash
$ pip install -r requirements3.txt
```