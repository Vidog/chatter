class __api_result__(APIMethod):
	def run(self):
		print 'Client disconnected: ', self.socket.ip
		return None