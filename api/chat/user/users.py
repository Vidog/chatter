class __api_result__(APIMethod):
	def run(self, message):
		self.socket.chat_users(self.socket)

		return ({}, True)