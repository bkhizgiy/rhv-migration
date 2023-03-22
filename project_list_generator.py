import ovirtsdk4 as sdk

#fetch user-vms list from the labs
connection = sdk.Connection(
    url='<URL>',
    username='<user>',
    password='<pass>',
    insecure=True,
)

vms_service = connection.system_service().vms_service()
#vms = vms_service.list(search='name=*')
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
print(vm_user_mapping)


users_vm_mapping = {}
for vm, users in vm_user_mapping.items():
    # Sort the users for each VM
    users = sorted(users)
    users_tuple = tuple(users)
    if users_tuple in users_vm_mapping:
        users_vm_mapping[users_tuple].append(vm)
    else:
        users_vm_mapping[users_tuple] = [vm]

# Print the resulting users_vm_mapping dictionary
print(users_vm_mapping)