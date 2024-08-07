from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

# Initialize the DAG
dag = DAG(
    'install_ansible_mysql_docker_parallel_from_a_to_j',
    default_args=default_args,
    description='A DAG to install Ansible, MySQL client, and Docker on instances from a to j in parallel via SSH',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['example'],
)

# Define the SSH commands to install Ansible, MySQL client, and Docker
install_ansible_command = """
sudo apt-add-repository -y ppa:ansible/ansible
sudo apt update
sudo apt install -y ansible
"""

install_mysql_client_command = """
sudo apt update
sudo apt install -y mysql-client-core-8.0
"""

install_docker_command = """
sudo apt update
sudo apt install -y docker.io
"""

# List of SSH connection IDs from 'a' to 'j'
connection_ids = [chr(i) for i in range(ord('a'), ord('j') + 1)]

# Initialize lists to store SSHOperator tasks
ansible_tasks = []
mysql_client_tasks = []
docker_tasks = []

# Create SSHOperator tasks for each connection ID
for conn_id in connection_ids:
    install_ansible_task = SSHOperator(
        task_id=f'install_ansible_{conn_id}',
        ssh_conn_id=conn_id,
        command=install_ansible_command,
        dag=dag,
    )
    ansible_tasks.append(install_ansible_task)

    install_mysql_client_task = SSHOperator(
        task_id=f'install_mysql_client_{conn_id}',
        ssh_conn_id=conn_id,
        command=install_mysql_client_command,
        dag=dag,
    )
    mysql_client_tasks.append(install_mysql_client_task)

    install_docker_task = SSHOperator(
        task_id=f'install_docker_{conn_id}',
        ssh_conn_id=conn_id,
        command=install_docker_command,
        dag=dag,
    )
    docker_tasks.append(install_docker_task)

    # Set up dependencies within each instance
    install_ansible_task >> install_mysql_client_task >> install_docker_task

# Set up parallel execution across instances
for i in range(len(connection_ids) - 1):
    ansible_tasks[i] >> ansible_tasks[i + 1]
    mysql_client_tasks[i] >> mysql_client_tasks[i + 1]
    docker_tasks[i] >> docker_tasks[i + 1]
