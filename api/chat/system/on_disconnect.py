class __api_result__(APIMethod):
	def run(self):
		Events.remove_caller_events(self.socket)

		if self.socket.authorized:
			self.socket.user_off(self.socket)
			del Clients[self.socket.username]

		return None