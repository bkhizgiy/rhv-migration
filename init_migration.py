from kubernetes import client, config
import json

config.load_kube_config()

with open('project_plans_map.json') as f:
    plans_list = json.load(f)

# Create a Kubernetes API client
api_cr_client = client.ApiClient()
custom_api = client.CustomObjectsApi(api_cr_client)

    
for  migration in plans_list: 
    #create migration
    migration_object = {
        "apiVersion": "forklift.konveyor.io/v1beta1",
        "kind": "Migration",
        "metadata": {
            "name": migration,
            "namespace": "konveyor-forklift"
        },
        "spec": {
            "plan": {
                "name": plans_list[migration],
                "namespace": "konveyor-forklift"
            }
        }
    }

    print(migration_object)

    custom_api.create_namespaced_custom_object(
        group="forklift.konveyor.io",
        version="v1beta1",
        namespace="konveyor-forklift",
        plural="migrations",
        body=migration_object
    )