import ovirtsdk4 as sdk
import json

#fetch user-vms list from the labs
connection = sdk.Connection(
    url='https://vm-10-122.lab.eng.tlv2.redhat.com/ovirt-engine/api',
    username='admin@internal',
    password='qum5net',
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
vm_users_new = {}

for vm, users in vm_user_mapping.items():
    users_list = tuple(sorted(users))
    if users_list in user_vms:
        user_vms[users_list].append(vm)
    else:
        user_vms[users_list] = [vm]

# Convert dictionary to JSON
user_vms_json = json.dumps({str(k): v for k, v in user_vms.items()})

# Write JSON to file
with open('user_vms.json', 'w') as f:
    f.write(user_vms_json)