class __api_result__(APIMethod):
	def run(self, username, message):
		self.socket.chat_private_message(self.socket, username, message)

		return ({}, True)