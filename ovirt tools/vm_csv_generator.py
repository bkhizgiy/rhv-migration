import ovirtsdk4 as sdk
import csv

# Connect to the oVirt engine
connection = sdk.Connection(
    url='url',
    username='user',
    password='password',
    ca_file='ca.pem',
)

# Get a reference to the VM service and user service
vm_service = connection.system_service().vms_service()
user_service = connection.system_service().users_service()

# Get a list of all users
users = user_service.list()

# Create a dictionary to store the user and VM IDs
user_vm_dict = {}

# Loop through each user and get their VMs
for user in users:
    user_vm_dict[user.principal] = []
    user_vms = vm_service.list(search=f"user={user.principal}")
    for vm in user_vms:
        user_vm_dict[user.principal].append(vm.name)

# Create a CSV file and write the user and VM IDs to it
with open('user_vms.csv', 'w', newline='') as csvfile:
    fieldnames = ['User', 'VM Name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for user, vms in user_vm_dict.items():
        for vm in vms:
            writer.writerow({'User': user, 'VM Name': vm})

# Close the connection
connection.close()