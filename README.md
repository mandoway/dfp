# DFP - DockerFile Patcher

This artifact aims to improve the quality of Dockerfiles by analyzing the file using the linter [Hadolint 1.23.0](https://github.com/hadolint/hadolint/releases/tag/v1.23.0), retrieving possible patches from a database and applying them in order of their ranking.

The patching script will suggest patches for various lines in a given dockerfile, but won't change the original file.

This repository contains scripts to
1. Generate patches based on Hadolint's violations and a large collection of Dockerfile changes in Open-Source projects [MSR18 database](https://github.com/sealuzh/msr18-docker-dataset)
and
2. Retrieve and apply these patches to any given Dockerfile

## Getting started

There are several possibilities to get the artifact up and running:
1. Docker image
2. Docker build
3. Local

### Docker image
TODO

Pre-requisites:
- Docker

### Docker build
Pre-requisites:
- Docker

Build the docker image using 
```shell
docker build -t dfp .
```
This will create a docker image on your local machine with the tag ``dfp``.  
Then create a container and run it detached:
````shell
docker run --rm --name dfp -d dfp
````

You now have a running container from your local image with the container name ``dfp``.
The container will remove itself once it is stopped.  
To access the container using ``bash`` the following command can be used:
````shell
docker exec -it dfp /bin/bash
````

### Local
TODO 

Pre-requisites:
- Python 3.9
- PostgreSQL


## File structure

This repository contains scripts for creating patches, running ``dfp`` to apply patches and evaluating it with a test set.

- [dfp_main.py](./dfp_main.py)  
When supplied with a Dockerfile, analyzes it and retrieves fitting patches from the patch database and applies them according to a ranking.
- [plotResults.py](./plotResults.py)  
Used to create result plots from the evaluation.
- [evalTestSet.py](./evalTestSet.py)  
Runs ``dfp`` for the test set.
- [patch_database.sql](./patch_database.sql)  
A database dump of the patch database.
- [/testSet](./testSet)  
A collection of 100 Dockerfiles and their linting violations for evaluation.
- [/results](./results)  
Contains evaluation results of the test set, once with all patches and once with no custom/manual patches.
These results are included, since the evaluation can take several hours. 
- [/dbHelper](./dbHelper)  
Code to connect to the Postgres DB.
- [/dfp](./dfp)  
Contains main code for ``dfp``. Functions to extract patches from the source database, get violations of a Dockerfile and retrieve fitting patches.
- [/linter](./linter)  
Code to use hadolint in python.
- [/msr18model](./msr18model)  
Model classes of the source database.
- [/utils](./utils)
Other utility code.


