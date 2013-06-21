from chatter import BaseSocketHandler, run_application, Clients
from tornado.options import define

class ChatSocketHandler(BaseSocketHandler):
    group = 'chat'

    def user_on(self, user):
        self.run_broadcast_event('user', 'on', {'user': user.username})

    def user_off(self, user):
        self.run_broadcast_event('user', 'off', {'user': user.username})

    def chat_users(self, user):
        users = Clients.keys()
        user.run_event('chat', 'users', {'users': users})

    def chat_message(self, sender, message):
        self.run_broadcast_event('chat', 'message', {'user': sender.username, 'message': message})

    def chat_private_message(self, sender, username, message):
        try:
            receiver = Clients[username]
            receiver.socket.run_event('chat', 'message', {'user': sender.username, 'message': message})
        except Exception, e:
            pass

    def on_auth(self, package, sock, params):
        if not sock.authorized:
            if package['group'] == 'user' and package['method'] == 'auth':
                return True
            if package['group'] == 'system':
                return True
            return self.error_response(0, 'Access denied')
        return True

def main():
    run_application([
        (r'/chat', ChatSocketHandler),
    ])

if __name__ == '__main__':
    main()