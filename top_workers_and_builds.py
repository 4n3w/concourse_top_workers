import subprocess
import json
import pandas as pd
import sys

def fetch_json_data(command):
    """Run a command and return JSON parsed output."""
    process = subprocess.run(command, capture_output=True, text=True, shell=False)
    if process.returncode == 0:
        return json.loads(process.stdout)
    else:
        print(f"Failed to fetch data: {process.stderr}")
        return None

def get_top_workers(deployment_name):
    """Fetch top 10 busiest workers based on CPU load."""
    data = fetch_json_data(['bosh', '-d', deployment_name, 'vms', '--vitals', '--json'])
    if data:
        rows = data['Tables'][0]['Rows']
        df = pd.DataFrame(rows)
        df['cpu_total'] = df.apply(lambda x: sum(float(x[col].rstrip('%')) for col in ['cpu_sys', 'cpu_user', 'cpu_wait']), axis=1)
        return df[df['instance'].str.startswith('worker')].nlargest(10, 'cpu_total')
    return pd.DataFrame()

def get_containers(target):
    """Fetch container data, ensure it is filtered for 'task' type and 'created' state, and correct the data types."""
    data = fetch_json_data(['fly', '-t', target, 'containers', '--json'])
    if data:
        df = pd.DataFrame(data)
        # Ensure job_id and build_id are integers; handle NaNs by converting to -1 and then to int
        # Also ensure they're present, we'll just assign a bogus value if they're not found
        if 'job_id' not in df.columns:
            df['job_id'] = -1
        else:
            df['job_id'] = df['job_id'].fillna(-1).astype(int)

        if 'build_id' not in df.columns:
            df['build_id'] = -1
        else:
            df['build_id'] = df['build_id'].fillna(-1).astype(int)

        df['build_name'] = df['build_name'].fillna("Unknown")

        # Filter containers to include only those that are 'task' type and in 'created' state
        filtered_df = df[(df['type'] == 'task') & (df['state'] == 'created')]
        return filtered_df
    return pd.DataFrame()

def get_builds(target):
    """Fetch all 'started' builds."""
    data = fetch_json_data(['fly', '-t', target, 'builds', '--json'])
    if data:
        builds_df = pd.DataFrame(data)
        builds_df.rename(columns={'id': 'build_id'}, inplace=True)
        return builds_df[builds_df['status'] == 'started']
    return pd.DataFrame()

def main(deployment_name, target):
    top_workers = get_top_workers(deployment_name)
    containers_df = get_containers(target)
    builds_df = get_builds(target)

    print("Top 10 Busiest Workers:")

    if top_workers.empty:
        print("No worker data available.")
        return

    print(top_workers[['instance', 'cpu_total']].to_string(index=False))

    print("\nWorker Details: \n")

    if containers_df.empty or builds_df.empty:
        print("No sufficient build or container data available via fly/concourse. Not busy?!")
        return

    for _, worker in top_workers.iterrows():
        full_worker_id = worker['instance']
        worker_id_prefix = full_worker_id.split('/')[1][:8]  # Extract the worker ID and take first 8 characters

        # Using substring matching for worker_name to ensure correct association
        worker_containers = containers_df[containers_df['worker_name'].str.startswith(worker_id_prefix)]

        if not worker_containers.empty:
            worker_build_ids = worker_containers['build_id'].unique()
            worker_builds = builds_df[builds_df['build_id'].isin(worker_build_ids)]

            if not worker_builds.empty:
                # Merge and keep both job_name columns separately if necessary
                merged_builds = worker_builds.merge(worker_containers[['build_id', 'job_name', 'build_name', 'step_name']], on='build_id', how='left', suffixes=('_build', '_container'))
                try:
                    merged_builds.rename(columns={'build_name': 'build_number'}, inplace=True)  # Renaming column for clarity
                    merged_builds.rename(columns={'job_name_build': 'job_name'}, inplace=True)  # Renaming column for clarity
                    print(f"{full_worker_id} builds:\n")
                    print(merged_builds[['team_name', 'pipeline_name', 'job_name', 'step_name', 'build_number', 'status']].to_string(index=False))
                except KeyError as e:
                    print(f"KeyError after merge for {full_worker_id}: {e}")
                print("\n")
            else:
                print(f"{full_worker_id} No started builds found for this worker.")
        else:
            print(f"{full_worker_id} No containers found for worker")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python top_workers_and_builds.py <bosh_deployment_name> <fly_target>")
    else:
        deployment_name = sys.argv[1]
        target = sys.argv[2]
        main(deployment_name, target)

