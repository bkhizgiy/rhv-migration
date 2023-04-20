import ovirtsdk4 as sdk

# Connect to the oVirt engine
connection = sdk.Connection(
    url='<URL>',
    username='<User>',
    password='<Pass>',
    ca_file='ca.pem',
)

# Get a reference to the "users" service
users_service = connection.system_service().users_service()

# Retrieve a list of all users in the system
all_users = users_service.list()
roles = connection.system_service().roles_service()

# Filter the list to only include users with the "SuperUser" role
for user in all_users:
    roles = connection.follow_link(user.roles)
    for role in roles:
        if role.name  =='SuperUser':
            admin_users = [user.principal]

# Print the list of admin users
for user in admin_users:
    print(user)