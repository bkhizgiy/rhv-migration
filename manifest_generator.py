import yaml

#Insert user list, for multipull users namespace, enter the users in the same string, separated by commas.
user_list = ['user#1', 'user#2', 'user#3.1, user#3.2, user#3.3']
manifest = []

#create projects for all users:
for user in user_list:
    users_str = user
    users_str = users_str.replace("(", "").replace(")", "").replace(", ", "-").replace("'", "").replace(",", "")
    project_name = "rhv-"+users_str
    users = user.split(', ')
    if len(users) > 1 :
        user_list_with_email = [user_mail + '@redhat.com' for user_mail in users]
        user_list_with_email = ', '.join(user_list_with_email)
    else:
        user_list_with_email = users_str+'@redhat.com'
    namespace = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': project_name,
            'labels': {
                'migration': 'rhv-cnv-migration'
            },
            'annotations': {
                'openshift.io/requester': user_list_with_email
            }
        }
    }
    manifest.append(namespace)

    # Optional - Create a role binding to bind the user to the namespace admin role
    users = user.split(', ')
    for namespace_user in users:
        user_email = namespace_user+"@redhat.com"
        role_binding_name = namespace_user+"-namespace-admin-role-binding"
        role_binding = {
        'apiVersion': 'rbac.authorization.k8s.io/v1',
        'kind': 'RoleBinding',
        'metadata': {
            'name': role_binding_name,
            'namespace': project_name,
            'labels': {
                'migration': 'rhv-cnv-migration'
            }
        },
        'subjects': [
            {
                'kind': 'User',
                'name': user_email,
                'apiGroup': 'rbac.authorization.k8s.io'
            }
        ],
        'roleRef': {
            'kind': 'ClusterRole',
            'name': 'admin',
            'apiGroup': 'rbac.authorization.k8s.io'
            }
        }
        manifest.append(role_binding)

# Convert the manifest list to YAML format
yaml_content = yaml.dump_all(manifest, default_flow_style=False)
print(yaml_content)

# Save the YAML content to a file
with open('project.yaml', 'w') as file:
    file.write(yaml_content)

print("Manifest file 'manifest.yaml' created.")
