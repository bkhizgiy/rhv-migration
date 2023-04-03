import ovirtsdk4 as sdk
from kubernetes import client, config

# create a connection to the oVirt API
connection = sdk.Connection(
    url='<URL>',
    username='<User>',
    password='<Pass>',
    ca_file='ca.pem',
)

vms_service = connection.system_service().vms_service()
vms = vms_service.list(search='name=*')

vm_user_mapping ={}
for vm in vms:
    permissions = vms_service.vm_service(vm.id).permissions_service().list()
    users = []
    for permission in permissions:
        if permission.user is None:
            continue

        user = connection.follow_link(permission.user)
        # remove super user dont appand to list
        users.append(user.principal)
    vm_user_mapping[vm.id] = users

user_vms = {}

for vm, users in vm_user_mapping.items():
    users_list = tuple(sorted(users))
    if users_list in user_vms:
        user_vms[users_list].append(vm)
    else:
        user_vms[users_list] = [vm]

# Load the Kubernetes configuration
config.load_kube_config()

# Create a Kubernetes API client
api_client = client.CoreV1Api()
api_cr_client = client.ApiClient()

#create projects for all users:
for user in user_vms:
    # Define the project object
    users_str = str(user)
    users_str = users_str.replace("(", "").replace(")", "").replace(", ", "-").replace("'", "").replace(",", "")
    project_name = users_str+"-project"
    print(project_name)
    project = client.V1Namespace()
    project.metadata = {"name": project_name}

    # Create the project
    api_client.create_namespace(body=project, pretty=True)