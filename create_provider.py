from kubernetes import client, config

config.load_kube_config()

# Create a Kubernetes API client
api_cr_client = client.ApiClient()
custom_api = client.CustomObjectsApi(api_cr_client)

secret_name = "secret-name"

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