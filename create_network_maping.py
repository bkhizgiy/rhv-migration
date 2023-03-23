#get all mapped network for networkmaps:
import ovirtsdk4 as sdk
from kubernetes import client, config

connection = sdk.Connection(
    url='<URL>',
    username='<User>',
    password='<Pass>',
    ca_file='ca.pem',
)

networks_service = connection.system_service().networks_service()
networks = networks_service.list()

networks_mapping_list =[]
for network in networks:
    networks_mapping_list.append(network.id)

print(networks_mapping_list)

network_plan_mapping = []
for network_id in networks_mapping_list:
    network_entry = {
            "destination": {
                "type": "pod"
            },
            "source": {
                "id": network_id
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
    plural="networkmaps",
    body=network_object
)