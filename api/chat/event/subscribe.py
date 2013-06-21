class __api_result__(APIMethod):
	def run(self, group, event, params, callback):
		Events.add_event(self.socket, self.socket.group, group, event, callback, params)

		return ({}, True)