# APX for Python 3

The official Python 3 implementation of [APX](https://cogu.github.io/apx/)

## Requires

- Python 3.10 or newer
- cfile

## Installation steps for virtual environment

Start bash (Linux) or Powershell (Windows).

### Create virtual environment

```bash
python -m venv .venv
```

### Activate virtual environment

On Windows:

```powershell
.\.venv\Scripts\activate
```

On Linux:

```bash
source .venv/bin/activate
```

### Upgrade toolchain

Once virtual environment is active run:

```bash
python -m pip install --upgrade pip flake8 cfile
python -m pip install --upgrade setuptools wheel twine
python -m pip install --upgrade sphinx
```

### Installing the Python module

Your current directory must be either where you unzipped the source package
or your where you cloned the git repo (See preparation step above).

For standard install, run:

```bash
pip install  .
```

For editable install, run:

```bash
pip install --editable .
```

## Running unit tests

On Windows:

```powershell
.\run_tests.cmd
```

On Linux:

```bash
./run_tests.sh
```

## Running flake

On Windows:

```powershell
.\run_flake.cmd
```

On Linux:

```bash
./run_flake.sh
```
