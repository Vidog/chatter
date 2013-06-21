class __api_result__(APIMethod):
	def run(self):
		print 'Client connected: ', self.socket.ip
		return None