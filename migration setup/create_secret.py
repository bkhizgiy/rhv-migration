from kubernetes import client, config
import base64, os

# Load the Kubernetes configuration
config.load_kube_config()

user = "<user>"
password = "<pass>"
url = "<url>/ovir-engine/api"
insecure = "false"
with open('ca.pem', 'r') as f:
    cacert = f.read()

user = encoded_value = base64.b64encode(user.encode("utf-8")).decode("utf-8")
password = encoded_value = base64.b64encode(password.encode("utf-8")).decode("utf-8")
url = encoded_value = base64.b64encode(url.encode("utf-8")).decode("utf-8")
insecure = encoded_value = base64.b64encode(insecure.encode("utf-8")).decode("utf-8")
cacert = encoded_value = base64.b64encode(cacert.encode("utf-8")).decode("utf-8")

secret_name = os.environ.get('SECRET')
mtv_namespace = os.environ.get('NAMESPACE')

metadata = client.V1ObjectMeta(name=secret_name, labels={"createdForProviderType" : "ovirt"})
# Create the Secret object
secret = client.V1Secret(
    metadata=metadata,
    type="Opaque",
    data={
        "username": user,
        "password": password,
        "url": url,
        "insecureSkipVerify": insecure,
        "cacert": cacert
    }
)


# Create the Secret using the Kubernetes API
api_instance = client.CoreV1Api()
api_instance.create_namespaced_secret(namespace=mtv_namespace, body=secret)
