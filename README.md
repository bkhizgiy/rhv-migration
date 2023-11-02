# RHV to OpenShift (CNV) Migration

This repository contains scripts to assist with migrating virtual machines from Red Hat Virtualization (RHV) to OpenShift Container Native Virtualization (CNV) using the Migration Toolkit for Virtualization (MTV) 2.4.

# Prerequisites
Before using the scripts in this repository, you will need to have the following:

- A Red Hat Virtualization (RHV) environment
- An OpenShift Container Platform (OCP) environment with Container Native Virtualization (CNV) installed
- The Migration Toolkit for Virtualization (MTV) <= 2.4 installed on your machine
- Python 3.6 or higher installed on your machine
- A workstation or server with the following installed:
  - The ovirt-engine-sdk-python package (for RHV API access)
  - The oc command-line tool (for interacting with OCP)

# Usage
The `run_full_deployment.sh` script in this repository is the main script that you should run to perform a full migration from RHV to CNV using MTV 2.4. Before running the script, make sure to modify the variables at the beginning of the script to match your environment.

The steps of the script are as following:
- creates secret
- creates provider
- creates storage and network maps
- creates the plans and project
- starting the migration
