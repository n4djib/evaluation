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
		flash("you don't have the needed permissions to perform this operation")
		abort(403)

class RolePermission(Permission):
	def __init__(self, role):
		self.role = role
		super(RolePermission, self).__init__()
	def rule(self):
		return RoleRule(self.role)

class AnyRolePermission(Permission):
	def __init__(self, roles=[]):
		self.roles = roles
		super(AnyRolePermission, self).__init__()
	def rule(self):
		r = RoleRule(self.roles[0])
		for x in range(len(self.roles)-1):
			r = r | RoleRule(self.roles[x + 1])
		return r


# class EveryRoleRule(Rule):
# 	def __init__(self, roles):
# 		self.roles = roles
# 		super(EveryRoleRule, self).__init__()
# 	def check(self):
# 		print(' ')
# 		print('---')
# 		e = True
# 		for role in self.roles:
# 			# print('1: ' + str(e))
# 			# r = RoleRule(role)
# 			# if r != True:
# 			# 	return False
# 			e = e & RoleRule(role)
# 			print('2: ' + str(e))
# 		print('---')
# 		print(' ')
# 		return e
# 	def deny(self):
# 		flash("ggggggg EveryRoleRule ggggggg")
# 		abort(403)

class EveryRolePermission(Permission):
	def __init__(self, roles=[]):
		self.roles = roles
		super(EveryRolePermission, self).__init__()
	def rule(self):
		r = None
		# r = RoleRule(self.roles[0])
		# for x in range(len(self.roles)-1):
		# 	r = r & RoleRule(self.roles[x + 1])
		# return r
		for x in range(len(self.roles)):
			if x == 0:
				r = RoleRule(self.roles[x])
			else:
				r = r & RoleRule(self.roles[x])
		print(' ')
		print(str(r))
		print(' ')
		return r
		# return EveryRoleRule(self.roles)


############

# class AdminRule(Rule):
# 	def check(self):
# 		for role in current_user.roles:
# 			if 'admin' == role.name:
# 				return True
# 			return False

# 	def deny(self):
# 		flash('you have to be an Admin')
# 		abort(403)

# class AdminPermission(Permission):
# 	def rule(self):
# 		return AdminRule()


