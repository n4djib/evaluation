from flask import flash, url_for, abort
 #, session, redirect
from flask_login import current_user
from permission import Rule, Permission


# admin			developper
# manager		can do some admin actions
# grader		enters grades
# supervisor	enters absences and manage stage
# inspector		for director and D.E.S
# student	
# teacher


class RolesAcceptedRule(Rule):
	def __init__(self, roles):
		self.roles = roles
		super(RolesAcceptedRule, self).__init__()
	def check(self):
		current_user_roles = [role.name for role in current_user.roles]
		for role in self.roles:
			if role in current_user_roles:
				return True
		return False
	def deny(self):
		flash("you need to have at least one of the permissions "+str(self.roles))
		abort(403)

class RolesAcceptedPermission(Permission):
	def __init__(self, roles):
		self.roles = roles
		super(RolesAcceptedPermission, self).__init__()
	def rule(self):
		return RolesAcceptedRule(self.roles)


class RolesRequiredRule(Rule):
	def __init__(self, roles):
		self.roles = roles
		super(RolesRequiredRule, self).__init__()
	def check(self):
		if len(self.roles) == 0:
			return False
		current_user_roles = [role.name for role in current_user.roles]
		for role in self.roles:
			if role not in current_user_roles:
				return False
		return True
	def deny(self):
		flash("you need to have all permissions "+str(self.roles))
		abort(403)

class RolesRequiredPermission(Permission):
	def __init__(self, roles):
		self.roles = roles
		super(RolesRequiredPermission, self).__init__()
	def rule(self):
		return RolesRequiredRule(self.roles)


############

class RoleRule(Rule):
	def __init__(self, role):
		self.role = role
		super(RoleRule, self).__init__()
	def check(self):
		for r in current_user.roles:
			if self.role == r.name:
				return True
		return False
	def deny(self):
		flash("you don't have the needed permissions ["+str(self.role)+"]")
		abort(403)

class RolePermission(Permission):
	def __init__(self, role):
		self.role = role
		super(RolePermission, self).__init__()
	def rule(self):
		return RoleRule(self.role)

############



############
