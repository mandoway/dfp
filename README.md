# DFP - DockerFile Patcher

This artifact aims to improve the quality of Dockerfiles by analyzing the file using the
linter [Hadolint 1.23.0](https://github.com/hadolint/hadolint/releases/tag/v1.23.0), retrieving possible patches from a
database and applying them in order of their ranking.

The patching script will suggest patches for various lines in a given dockerfile, but won't change the original file.

This repository contains scripts to

1. Generate patches based on Hadolint's violations and a large collection of Dockerfile changes in Open-Source
   projects [MSR18 database](https://github.com/sealuzh/msr18-docker-dataset)
   and
2. Retrieve and apply these patches to any given Dockerfile

## Getting started

There are several possibilities to get the artifact up and running:

1. Docker image (*recommended*)
2. Docker build
3. Local

### Docker image (*recommended*)
Pre-requisites:

- [Docker](https://docs.docker.com/get-docker/)

Download the image and start the container:
````shell
docker run --rm --name dfp -d mando9/dfp
````

You now have a running container with the name ``dfp``.
The container will remove itself once it is stopped, due to the option ``--rm``.  
To access the container using ``bash`` the following command can be used:

````shell
docker exec -it dfp /bin/bash
````

### Docker build

Pre-requisites:

- [Docker](https://docs.docker.com/get-docker/)

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
The container will remove itself once it is stopped, due to the option ``--rm``.  
To access the container using ``bash`` the following command can be used:

````shell
docker exec -it dfp /bin/bash
````

### Local

Pre-requisites:

- [Python 3.9](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)

The following uses the default user ``postgres`` with password `postgres` (can vary on different installation methods).
If you want to use a different user, change the option ``-U <user>``.
You will also need to change the login information in [config.ini](./config.ini) accordingly.

The patch database can be restored by running

````shell
psql -U postgres -e < patch_database.sql
````

in a terminal (Windows: PowerShell won't work, use the command prompt).
This will create a database ``dfp`` with all patches.  
Alternatively, you can create the database yourself and restore the data using

````shell
pg_restore -U postgres --dbname dfp patch_database
````

When you run the main script using the Dockerfile for this artifact,

````shell
# python executable for python 3.9 either just "python" or "python3"
python .\dfp_main.py .\Dockerfile
````

you should get an output like:

````
Number of violations: 3
Searching for patches for line (DL3009): RUN apt-get update
Trying patches for violation 0: : 82it [00:09,  8.59it/s]
````

You can then abort the execution using ``Ctrl+C``.

## File structure

This repository contains scripts for creating patches, running ``dfp`` to apply patches and evaluating it with a test
set.

- [dfp_main.py](./dfp_main.py)  
  When supplied with a Dockerfile, analyzes it and retrieves fitting patches from the patch database and applies them
  according to a ranking.
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
  Contains main code for ``dfp``. Functions to extract patches from the source database, get violations of a Dockerfile
  and retrieve fitting patches.
- [/linter](./linter)  
  Code to use hadolint in python.
- [/msr18model](./msr18model)  
  Model classes of the source database.
- [/utils](./utils)
  Other utility code.

## Running DFP

### Main script

The main script analyzes a Dockerfile, queries the patch database and applies patches to find fixes.  
Execution can last several minutes, depending on the amount of violations in the Dockerfile.  
Usage of the main script is as follows:

````shell
python dfp_main.py [OPTIONS] DOCKERFILE
````

with options:

- ``-l <violation_file>``  
  Path to a CSV file containing the result of a linting run on this Dockerfile.
  These violations will be used for the query.  
  Without this option, the script will run the linter before querying patches.
- ``-q``  
  Quiet flag. The script will not output anything.
- ``-pl <limit>``  
  Patch limit. The maximum number of patches to be queried and applied to the Dockerfile.  
  Can reduce runtime. Default is ``300``.

All files with suffix ``*_dockerfile`` in `/testSet` are Dockerfiles to patch.  
An example execution would be

````shell
python dfp_main.py ./testSet/pID201_dID3718_sID7015_dockerfile
````

### Processing the test set

This process can take a long time (several hours), since many Dockerfiles are analyzed.  
Therefore, pre-computed results are provided in folder ``/results``.  
All files in the test set can be process using

````shell
python evalTestSet.py
````

The script will print some statistics about the evaluation and saves the data to a file
called ``evalStats_<current_time>.pkl`` in the project repository.

### Evaluate results

To display the results visually, use the script

````shell
python plotResults.py RESULT_FILE
````

This will show several plots of the result data and prints statistical information and LateX tables to the console.
Plots:

1. Violation distribution (Figure 9)  
   Which rule violations are found how often.
2. Execution times (Figure 10)  
   How long does the execution take for one Dockerfile and for one violation.
3. Fix rate (Figure 11)  
   Found violations versus fixed violations
4. Impact of patch limit to fixes  
   How limiting the patch query affects found fixes. Can be found in Table 19.

The plots are then stored in the same directory as the results files pre-fixed with the result file name, i.e. for
pre-computed patches in folder ``/results``.

To view pre-computed results containing **generated and custom patches**, use

````shell
python plotResults.py ./results/resultsWithAllPatches.pkl
````

To view pre-computed results containing **only generated patches**, use

````shell
python plotResults.py ./results/resultsWithOnlyGeneratedPatches.pkl
````

To copy the plots from the docker container use the following on the host machine (example files for resultsWithAllPatches.pkl):

````shell
docker cp dfp:/dfp/results/resultsWithAllPatches_ExecutionTimes.png .             
docker cp dfp:/dfp/results/resultsWithAllPatches_FixRate.png .       
docker cp dfp:/dfp/results/resultsWithAllPatches_RuleDistribution.png .
docker cp dfp:/dfp/results/resultsWithAllPatches_PatchLimitImpact.png .
````

