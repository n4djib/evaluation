from app import app
from flask import g
from flask_login import current_user
from flask_principal import identity_loaded, Permission
from flask_principal import RoleNeed, UserNeed

# Create a permission with a single Need, in this case a RoleNeed.
be_admin = RoleNeed('admin')
admin_permission = Permission(be_admin)
admin_permission.description = "Admin's permissions"



apps_needs = [be_admin]
apps_permissions = [admin_permission]


# def current_privileges():
#     return (('{method} : {value}').format(method=n.method, value=n.value)
#             for n in apps_needs if n in g.identity.provides)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # # Add the UserNeed to the identity
    # if hasattr(current_user, 'id'):
    #     identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


