class __api_result__(APIMethod):
	def run(self, text1, text2, text3):
		self.socket.send_events()

		return ({'text': [text1, text2, text3]}, True)