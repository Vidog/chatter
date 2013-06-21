class __api_result__(APIMethod):
	def run(self, key):
		if key != 'testtest123':
			print 'Someone want to update system with wrong key:', key
			return self.socket.error_response(0, 'Wrong key')

		print '[SYSTEM UPDATED SUCCESSFULLY]'

		self.socket.loadAPIStruct()

		return ({}, True)