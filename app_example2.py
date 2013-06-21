from chatter import BaseSocketHandler, run_application, Clients

class Example2SocketHandler(BaseSocketHandler):
    group = 'example2'

    def send_events(self):
        #send event to current client
        self.run_event('test', 'event1', {'hello': 'world', 'foo': 'bar'})

        #send event to all connected and subscribed clients
        self.run_broadcast_event('test', 'event2', {'someparam': 'somevalue'})

def main():
    run_application([
        (r'/example2', Example2SocketHandler),
    ])

if __name__ == '__main__':
    main()