import ovirtsdk4 as sdk

# Create a connection to the oVirt Engine
connection = sdk.Connection(
    url='<URL>',
    username='<User>',
    password='<Pass>',
    ca_file='ca.pem',
)

vms_service = connection.system_service().vms_service()
vms = vms_service.list()

# Calculate the total size of disks for all the VMs
total_size_provisioned = 0
total_size_actual = 0
for vm in vms:
    vm_service = vms_service.vm_service(vm.id)
    disk_attachments_service = vm_service.disk_attachments_service()

    disk_attachments = disk_attachments_service.list()

    # Calculate the total provisioned size of disks for the VM
    for disk_attachment in disk_attachments:
        disk_service = connection.system_service().disks_service().disk_service(disk_attachment.disk.id)
        disk = disk_service.get()
        total_size_provisioned += disk.provisioned_size
    
    # Calculate the total actual size of disks for the VM
    for disk_attachment in disk_attachments:
        disk_service = connection.system_service().disks_service().disk_service(disk_attachment.disk.id)
        disk = disk_service.get()
        total_size_actual += disk.actual_size

total_size_gb_actual = total_size_actual / 1073741824
total_size_gb_provisioned = total_size_provisioned / 1073741824

# Print the total size of disks for all the VMs
print(f'Total provisioned size of disks for all the VMs: {total_size_provisioned} bytes, {total_size_gb_provisioned} GB')
print(f'Total actual size of disks for all the VMs: {total_size_actual} bytes, {total_size_gb_actual} GB')

# Close the connection to the oVirt Engine
connection.close()