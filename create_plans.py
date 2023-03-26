
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
custom_api = client.CustomObjectsApi(api_cr_client)

network_name = "name1"
storage_name = "name2"
provider_name = "name3"

project_plan_map = {}
#create projects names for all users:
for users in vm_list:
    users_str = users
    users_str = users_str.replace("(", "").replace(")", "").replace(", ", "-").replace("'", "")
    project_name = users_str+"-project"

    project = client.V1Namespace()
    project.metadata = {"name": project_name}

    # Create the project
    api_client.create_namespace(body=project, pretty=True)

    #create VM list
    vm_plan_list = [] 
    for vm_id in vm_list[users]:
        vm_entry = {
            "hooks": [],
            "id": vm_id
        }
        vm_plan_list.append(vm_entry)
    print(vm_plan_list)

    #create Plan
    plan_name = users_str+"-plan"
    plan_object = {
        "apiVersion": "forklift.konveyor.io/v1beta1",
        "kind": "Plan",
        "metadata": {
            "name": plan_name,
            "namespace": "konveyor-forklift"
        },
        "spec": {
            "archived": False,
            "description": "",
            "map": {
                "network": {
                    "name": network_name,
                    "namespace": "konveyor-forklift"
                },
                "storage": {
                    "name": storage_name,
                    "namespace": "konveyor-forklift"
                }
            },
            "provider": {
                "destination": {
                    "name": "host",
                    "namespace": "konveyor-forklift"
                },
                "source": {
                    "name": provider_name,
                    "namespace": "konveyor-forklift"
                }
            },
            "targetNamespace": project_name,
            "vms": vm_plan_list,
            "warm": False
        }
    }

    custom_api.create_namespaced_custom_object(
        group="forklift.konveyor.io",
        version="v1beta1",
        namespace="konveyor-forklift",
        plural="plans",
        body=plan_object
    )
    project_plan_map[users_str+"-migration"] = plan_name


#create JSON file with project and paln names mapping
project_plan_json = json.dumps({str(k): v for k, v in project_plan_map.items()})

with open('project_plans_map.json', 'w') as f:
    f.write(project_plan_json)
    f.close()