from dateutil.parser import parse
from datetime import datetime, timezone
import ovirtsdk4 as sdk
import csv, json

# Create a connection to the oVirt Engine
connection = sdk.Connection(
    url='url',
    username='user',
    password='password',
    ca_file='ca.pem',
)

vms_service = connection.system_service().vms_service()
vms = vms_service.list(search='status=down')

vm_to_remove = {}
for vm in vms:
    vm_date = str(vm.stop_time)

    # parse the date string into a datetime object with timezone information
    dt = parse(vm_date)
    # create a timezone aware datetime object with UTC timezone
    dt_utc = dt.astimezone(timezone.utc)
    # calculate the time difference in seconds between dt_utc and current time
    time_diff = (datetime.now(timezone.utc) - dt_utc).total_seconds()

    if time_diff > 30 * 24 * 60 * 60: # 30 days in seconds
        vm_to_remove[vm.name] = [str(vm.stop_time.date()), vm.]

connection.close()

# Open a new CSV file in write mode
with open('output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(vm_to_remove.keys())
    for row in zip(*vm_to_remove.values()):
        writer.writerow(row)

json_string = json.dumps(vm_to_remove)
print(json_string)
