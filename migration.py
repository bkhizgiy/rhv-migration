
from kubernetes import client, config
import base64

# Open the file and read its contents
with open('projects_list.txt', 'r') as f:
    lines = f.readlines()

vm_list = {}

for line in lines:
    key, value = line.strip().split(': ')
    vm_list[key] = value

# Load the Kubernetes configuration
config.load_kube_config()

# Create a Kubernetes API client
api_client = client.CoreV1Api()
api_cr_client = client.ApiClient()
custom_api = client.CustomObjectsApi(api_cr_client)

#create secret
user = "<user>"
password = "<pass>"
url = "<url>"
insecure = "True"
user = encoded_value = base64.b64encode(user.encode("utf-8")).decode("utf-8")
password = encoded_value = base64.b64encode(password.encode("utf-8")).decode("utf-8")
url = encoded_value = base64.b64encode(url.encode("utf-8")).decode("utf-8")
insecure = encoded_value = base64.b64encode(insecure.encode("utf-8")).decode("utf-8")

# Create the Secret object
secret_name = "secret-script"
secret = client.V1Secret(
    metadata=client.V1ObjectMeta(name=secret_name),
    type="Opaque",
    data={
        "user": user,
        "password": password,
        "url": url,
        "insecureSkipVerify": insecure
    }
)

# Create the Secret using the Kubernetes API
api_instance = client.CoreV1Api()
api_instance.create_namespaced_secret(namespace="konveyor-forklift", body=secret)

#create provider object
provider_name = "provider-script"
cr_object = {
    "apiVersion": "forklift.konveyor.io/v1beta1",
    "kind": "Provider",
    "metadata": {
        "name": provider_name,
        "namespace": "konveyor-forklift",
    },
    "spec": {
        "secret": {
            "name": secret_name,
            "namespace": "konveyor-forklift",
        },
        "type": "ovirt",
        "url": "https://vm-10-122.lab.eng.tlv2.redhat.com/ovirt-engine/api",
    },
}

# Create the provider in Kubernetes
custom_api.create_namespaced_custom_object(
    group="forklift.konveyor.io",
    version="v1beta1",
    namespace="konveyor-forklift",
    plural="providers",
    body=cr_object
)

f =  open('migrations_list.txt', 'w')

#create projects for all users:
for user in vm_list:
    # Define the project object
    project_name = user+"-project"
    project = client.V1Namespace()
    project.metadata = {"name": project_name}

    # Create the project
    api_client.create_namespace(body=project, pretty=True)

    #create VM list
    vm_plan_list = []
    for vm_id in vm_list[user]:
        vm_entry = {
            "hooks": [],
            "id": vm_id
        }
        vm_plan_list.append(vm_entry)
    print(vm_plan_list)

    #create Plan
    plan_name = "plan-script"
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
    print("Custom Resource created successfully!")

    f.write(f"{plan_name}-migration: {plan_name}\n")

f.close()

