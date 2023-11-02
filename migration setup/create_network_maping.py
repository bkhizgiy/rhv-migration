#get all mapped network for networkmaps:
import ovirtsdk4 as sdk
from kubernetes import client, config
import os

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

mtv_namespace = os.environ.get('NAMESPACE')
provider_name = os.environ.get('PROVIDER')
network_mapping_name = os.environ.get('NETWORK_MAP')

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
network_object = {
    "apiVersion": "forklift.konveyor.io/v1beta1",
    "kind": "NetworkMap",
    "metadata": {
        "name": network_mapping_name,
        "namespace": mtv_namespace
    },
    "spec": {
        "map": network_plan_mapping,
        "provider": {
            "destination": {
                "name": "host",
                "namespace": mtv_namespace
            },
            "source": {
                "name": provider_name,
                "namespace": mtv_namespace
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
    namespace=mtv_namespace,
    plural="networkmaps",
    body=network_object
)