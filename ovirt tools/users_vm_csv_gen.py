import ovirtsdk4 as sdk
import csv

# Connect to the oVirt engine
connection = sdk.Connection(
    url='https://ovirt-url/ovirt-engine/api',
    username='admin@internal',
    password='password',
    ca_file='ca.pem',
)

# Get a reference to the VM service and user service
vm_service = connection.system_service().vms_service()
user_service = connection.system_service().users_service()

# Create a dictionary to store the user and VM IDs
user_vm_dict = {}

# Loop through each VM and get the users with permissions
vms = vm_service.list()
for vm in vms:
    vm_name = vm.name
    vm_id = vm.id
    user_vm_dict[vm_name] = []
    vm_permissions = vm_service.vm_permissions_service(vm_id).list()
    for perm in vm_permissions:
        user_name = perm.user.principal
        if user_name not in user_vm_dict[vm_name]:
            user_vm_dict[vm_name].append(user_name)

# Create a CSV file and write the user and VM IDs to it
with open('vm_users.csv', 'w', newline='') as csvfile:
    fieldnames = ['VM Name', 'User']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for vm, users in user_vm_dict.items():
        for user in users:
            writer.writerow({'VM Name': vm, 'User': user})

connection.close()