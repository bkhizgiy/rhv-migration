from kubernetes import client, config
import json

# Open the JSON file for input
with open('user_vms.json') as f:
    vm_list = json.load(f)

# Load the Kubernetes configuration
config.load_kube_config()

# Create a Kubernetes API client
api_client = client.CoreV1Api()
api_cr_client = client.ApiClient()

project_plan_map = {}
#create projects names for all users:
for users in vm_list:
    users_str = users
    users_str = users_str.replace("(", "").replace(")", "").replace(", ", "-").replace("'", "").replace(",", "")
    project_name = "rhv-"+users_str+"-project"

    project = client.V1Namespace()
    project.metadata = {"name": project_name}

    print(project_name)

    # Create the project
    api_client.create_namespace(body=project, pretty=True)
