class __api_result__(APIMethod):
	def run(self, message):
		self.socket.chat_message(self.socket, message)

		return ({}, True)