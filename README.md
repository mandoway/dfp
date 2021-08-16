# DFP - DockerFile Patcher

This project aims to automatically improve dockerfiles by fixing [hadolint](https://github.com/hadolint/hadolint) violations.
The patching script will suggest patches for various lines in a given dockerfile, but won't change the original file.

## Usage

To use the patcher, first import the DB dump `patch_database` into a PostgreSQL database. 
We recommend to use pgadmin for this task.

Then install the requirements via:
```
pip install -r requirements.txt
```

The patch blacklist (words which are not patched) is configurable in the file `dfp_main.py`.
Basic usage for the patcher:
```
python dfp_main.py DOCKERFILE
```

For help:
```
python dfp_main.py --help
```
