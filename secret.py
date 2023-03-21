from kubernetes import client, config
import base64


# Load the Kubernetes configuration
config.load_kube_config()

user = "<user>"
password = "<pass>"
url = "<url>/ovir-engine/api"
insecure = "True"
user = encoded_value = base64.b64encode(user.encode("utf-8")).decode("utf-8")
password = encoded_value = base64.b64encode(password.encode("utf-8")).decode("utf-8")
url = encoded_value = base64.b64encode(url.encode("utf-8")).decode("utf-8")
insecure = encoded_value = base64.b64encode(insecure.encode("utf-8")).decode("utf-8")

# Create the Secret object
secret = client.V1Secret(
    metadata=client.V1ObjectMeta(name="my-secret"),
    type="Opaque",
    data={
        "username": user,
        "password": password,
        "url": url,
        "insecureSkipVerify": insecure
    }
)

# Create the Secret using the Kubernetes API
api_instance = client.CoreV1Api()
api_instance.create_namespaced_secret(namespace="konveyor-forklift", body=secret)

