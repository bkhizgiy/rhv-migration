import ovirtsdk4 as sdk
from kubernetes import client, config

# create a connection to the oVirt API
connection = sdk.Connection(
    url='<URL>',
    username='<User>',
    password='<Pass>',
    ca_file='ca.pem',
)


storage_domains_service = connection.system_service().storage_domains_service()
storage_domains = storage_domains_service.list()

storage_mapping_list = []
for storage_domain in storage_domains:
    storage_mapping_list.append(storage_domain.id)

storage_plan_mapping = []
for sd_id in storage_mapping_list:
    storage_entry = {
            "destination": {
                "storageClass": "nfs-csi-benny"
            },
            "source": {
                "id": sd_id
            }
        }
    storage_plan_mapping.append(storage_entry)

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
        "map":storage_plan_mapping,
        "provider": {
            "destination": {
                "name": "host",
                "namespace": "konveyor-forklift"
            },
            "source": {
                "name": "provider_name",
                "namespace": "konveyor-forklift"
            }
        }
    }
}

config.load_kube_config()
api_cr_client = client.ApiClient()
custom_api = client.CustomObjectsApi(api_cr_client)

custom_api.create_namespaced_custom_object(
    group="forklift.konveyor.io",
    version="v1beta1",
    namespace="konveyor-forklift",
    plural="storagemaps",
    body=storage_object
)