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
        df['job_id'] = df['job_id'].fillna(-1).astype(int)
        df['build_id'] = df['build_id'].fillna(-1).astype(int)
        # Filter containers to include only those that are 'task' type and in 'created' state
        filtered_df = df[(df['type'] == 'task') & (df['state'] == 'created')]
        return filtered_df
    return pd.DataFrame()

def get_builds(target):
    """Fetch all 'started' builds."""
    data = fetch_json_data(['fly', '-t', target, 'builds', '--json'])
    if data:
        builds_df = pd.DataFrame(data)
        return builds_df[builds_df['status'] == 'started']
    return pd.DataFrame()

def main(deployment_name, target):
    top_workers = get_top_workers(deployment_name)
    containers_df = get_containers(target)
    builds_df = get_builds(target)

    if top_workers.empty:
        print("No worker data available.")
        return
    if containers_df.empty or builds_df.empty:
        print("No sufficient build or container data available via fly/concourse.")
        return

    print("Top 10 Busiest Workers:")
    print(top_workers[['instance', 'cpu_total']].to_string(index=False))

    for _, worker in top_workers.iterrows():
        full_worker_id = worker['instance']
        worker_id_prefix = full_worker_id.split('/')[1][:8]  # Extract the worker ID and take first 8 characters

        print(f"\n\nDetails for Worker: {full_worker_id}\n")

        # Using substring matching for worker_name to ensure correct association
        worker_containers = containers_df[containers_df['worker_name'].str.startswith(worker_id_prefix)]

        if not worker_containers.empty:
            worker_build_ids = worker_containers['build_id'].unique()
            worker_builds = builds_df[builds_df['id'].isin(worker_build_ids)]
            if not worker_builds.empty:
                print("Related Started Builds:\n")
                print(worker_builds[['id', 'team_name', 'job_name', 'pipeline_name', 'status']].to_string(index=False))
            else:
                print("No started builds found for this worker.")
        else:
            print(f"No containers found for worker ID prefix: {worker_id_prefix}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python top_workers_and_builds.py <bosh_deployment_name> <fly_target>")
    else:
        deployment_name = sys.argv[1]
        target = sys.argv[2]
        main(deployment_name, target)

