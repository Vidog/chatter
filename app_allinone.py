from chatter import BaseSocketHandler, run_application, Clients

from app_chat import ChatSocketHandler
from app_example1 import Example1SocketHandler
from app_example2 import Example2SocketHandler

def main():
    run_application([
        (r'/chat', ChatSocketHandler),
        (r'/example1', Example1SocketHandler),
        (r'/example2', Example2SocketHandler),
    ])

if __name__ == '__main__':
    main()