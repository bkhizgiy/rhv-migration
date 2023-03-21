
from kubernetes import client, config
import base64
import ovirtsdk4 as sdk


#fetch user-vms list from the lab
connection = sdk.Connection(
    url='<URL>',
    username='<User>',
    password='<Pass>',
    insecure=True,
)

vms_service = connection.system_service().vms_service()
#vms = vms_service.list(search='name=bzlotnik*')
vms = vms_service.list()

#create a map of users with all the vms that belonges to them
vm_list ={}
for vm in vms:
    permissions = vms_service.vm_service(vm.id).permissions_service().list()
    users = []
    for permission in permissions:
        if permission.user is None:
            continue

        user = connection.follow_link(permission.user)
        users.append(user.principal)
        if user.principal in vm_list:
            new_vm = vm_list[user.principal]
            new_vm.append(vm.id)
            vm_list[user.principal] = new_vm
        else:
            vm_list[user.principal] = [vm.id]

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

#create projects for all users:
for user in vm_list:
    # Define the project object
    project_name = user+"-project"
    project = client.V1Namespace()
    project.metadata = {"name": project_name}

    # Create the project
    api_client.create_namespace(body=project, pretty=True)

    #get all mapped network for networkmaps:
    networks_mapping = set()
    for vm_id in vm_list[user]:
        nics_service = vms_service.vm_service(vm_id).nics_service()
        nics = nics_service.list()
        for nic in nics:
            vnic = connection.follow_link(nic.vnic_profile)
            networks_mapping.add(vnic.network.id)

    network_plan_mapping = []
    for net in networks_mapping:
        network_entry = {
                "destination": {
                    "type": "pod"
                },
                "source": {
                    "id": net
                }
        }
        network_plan_mapping.append(network_entry)

    #create network map
    network_name = "network-script"
    network_object = {
        "apiVersion": "forklift.konveyor.io/v1beta1",
        "kind": "NetworkMap",
        "metadata": {
            "name": network_name,
            "namespace": "konveyor-forklift"
        },
        "spec": {
            "map": network_plan_mapping,
            "provider": {
                "destination": {
                    "name": "host",
                    "namespace": "konveyor-forklift"
                },
                "source": {
                    "name": provider_name,
                    "namespace": "konveyor-forklift"
                }
            }
        }
    }


    custom_api.create_namespaced_custom_object(
        group="forklift.konveyor.io",
        version="v1beta1",
        namespace="konveyor-forklift",
        plural="networkmaps",
        body=network_object
    )

    #find all vms_networks for maping
    storage_mapping = set()
    for vm_id in vm_list[user]:
        disks_service = vms_service.vm_service(vm_id).disk_attachments_service()
        disk_attachments = disks_service.list()
        for attachment in disk_attachments:
            disk = connection.follow_link(attachment.disk)
            for sd in disk.storage_domains:
                storage_mapping.add(sd.id)

    storage_plan_maping = []
    for storage in storage_mapping:
        storage_entry = {
                "destination": {
                    "storageClass": "nfs-csi-benny"
                },
                "source": {
                    "id": storage
                }
            }
        storage_plan_maping.append(storage_entry)

    #create storage map
    storage_name = "storage-script"
    storage_object = {
        "apiVersion": "forklift.konveyor.io/v1beta1",
        "kind": "StorageMap",
        "metadata": {
            "name": storage_name,
            "namespace": "konveyor-forklift"
        },
        "spec": {
            "map":storage_plan_maping,
            "provider": {
                "destination": {
                    "name": "host",
                    "namespace": "konveyor-forklift"
                },
                "source": {
                    "name": provider_name,
                    "namespace": "konveyor-forklift"
                }
            }
        }
    }

    custom_api.create_namespaced_custom_object(
        group="forklift.konveyor.io",
        version="v1beta1",
        namespace="konveyor-forklift",
        plural="storagemaps",
        body=storage_object
    )

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

    #create migration
    migration_name = "migration-script"
    migration_object = {
        "apiVersion": "forklift.konveyor.io/v1beta1",
        "kind": "Migration",
        "metadata": {
            "name": migration_name,
            "namespace": "konveyor-forklift"
        },
        "spec": {
            "plan": {
                "name": plan_name,
                "namespace": "konveyor-forklift"
            }
        }
    }
    '''
    custom_api.create_namespaced_custom_object(
        group="forklift.konveyor.io",
        version="v1beta1",
        namespace="konveyor-forklift",
        plural="migrations",
        body=migration_object
    )
    print("Custom Resource created successfully!")
    '''

