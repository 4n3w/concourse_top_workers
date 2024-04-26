# README for Concourse Worker Monitoring Script
## Overview
This Python script provides insights into the busiest workers in a Concourse CI environment by fetching and displaying information about the workers and any associated "started" builds. It utilizes the BOSH CLI to obtain worker data and the Fly CLI for containers and builds data, ensuring you can monitor and debug your CI pipeline effectively.

## Features
- Worker Monitoring: Identifies the top 10 busiest workers based on CPU load.
- Build Association: Displays any ongoing (started) builds that are linked to each worker, providing a clear view of what each worker is currently processing.
- Flexible Configuration: Supports custom Concourse deployment names and Fly CLI targets through command-line arguments.

## Prerequisites
- Python 3.6 or higher
- Access to a terminal or command line interface
- BOSH CLI installed and configured
- Fly CLI installed and configured
- Appropriate permissions to view BOSH deployments and Concourse builds

## Installation
No installation is required for the script itself, but ensure that Python and the necessary CLI tools (BOSH and Fly) are installed on your system. You can download and place the script in any directory where you have permissions to execute Python scripts.

## Usage
To use the script, navigate to the directory containing the script and run it using the following command format:

```bash
python monitor_workers.py <deployment_name> <fly_target>
```

* <deployment_name>: The name of your BOSH deployment for Concourse, e.g., concourse, found via `bosh deps`
* <fly_target>: The target name configured in your Fly CLI for the Concourse instance, found via `fly ts` e.g., my-concourse-target.

```bash
python monitor_workers.py concourse h2o-2-24140
```

This command will output the top 10 busiest workers in the specified Concourse deployment along with any active builds they are handling.

## Output
The script will display:

A list of the top 10 busiest workers by CPU usage.
For each worker, any associated builds that are in the "started" state.
If no active builds are found for a worker, it will note that no started builds were found for that worker.

Ex.

```
python3 top_workers_and_builds.py
Top 10 Busiest Workers:
                                      instance  cpu_total
3  worker/3b6b14a6-4ddb-4d31-98e4-38bd826460d2       99.7
5  worker/9f55a1ac-3e74-4b0e-ad9d-cd3dffeffcad       87.7
2  worker/0533664a-6b3a-4895-a22f-6d495198c449       25.2
9  worker/fcc90662-0c64-47cd-8234-fe97f7b09be6        0.5
4  worker/8c219115-71bb-4ab4-b652-eb4aeab511bc        0.3
6  worker/b929595f-dc02-4a43-85a5-a281c4eac28b        0.3
8  worker/d4ab4e4b-d97a-4443-8652-6900e950ee7b        0.3
7  worker/d18ca852-e84a-4815-af9a-de6e22f65104        0.2


Details for Worker: worker/3b6b14a6-4ddb-4d31-98e4-38bd826460d2

Related Started Builds:

       id team_name          job_name pipeline_name   status
0  134446      main   stress-cpu-load         alpha  started
2  134361      main   stress-cpu-load       whiskey  started
3  134360      main  stress-disk-load       whiskey  started


Details for Worker: worker/9f55a1ac-3e74-4b0e-ad9d-cd3dffeffcad

Related Started Builds:

       id team_name             job_name pipeline_name   status
1  134362      main  stress-network-load       whiskey  started


Details for Worker: worker/0533664a-6b3a-4895-a22f-6d495198c449

Related Started Builds:

       id team_name         job_name pipeline_name   status
4  134298      main  stress-cpu-load         bravo  started


Details for Worker: worker/fcc90662-0c64-47cd-8234-fe97f7b09be6

No containers found for worker ID prefix: fcc90662


Details for Worker: worker/8c219115-71bb-4ab4-b652-eb4aeab511bc

No containers found for worker ID prefix: 8c219115


Details for Worker: worker/b929595f-dc02-4a43-85a5-a281c4eac28b

No containers found for worker ID prefix: b929595f


Details for Worker: worker/d4ab4e4b-d97a-4443-8652-6900e950ee7b

No containers found for worker ID prefix: d4ab4e4b


Details for Worker: worker/d18ca852-e84a-4815-af9a-de6e22f65104

No containers found for worker ID prefix: d18ca852
```

## Troubleshooting

Command Not Found: Ensure Python and CLI tools are correctly installed and accessible in your system’s PATH.
Permission Issues: Verify that you have the necessary permissions to execute the BOSH and Fly commands for the given deployment and target.
Data Mismatch: If no data appears or there are mismatches, ensure that the deployment name and fly target are correctly specified and that the workers are active and reporting data.
Contributing
Contributions to enhance the script or fix issues are welcome. Please fork the repository and submit a pull request with your changes.

