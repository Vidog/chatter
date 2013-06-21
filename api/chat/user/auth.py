class __api_result__(APIMethod):
	def run(self, username, password):
		try:
			client = Clients[username]

			self.socket.send_error(0, 'Only one username connection is allowed', self.callback_id)

			self.socket.disconnect()

			return self.socket.error_response(0, 'Access denied')
		except Exception, e:
			pass

		Clients[username] = self

		self.socket.authorized = True
		self.socket.username = username
		self.socket.password = password

		self.socket.user_on(self.socket)

		return ({}, True)