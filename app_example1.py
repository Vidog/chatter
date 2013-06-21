from chatter import BaseSocketHandler, run_application, Clients

class Example1SocketHandler(BaseSocketHandler):
    group = 'example1'

def main():
    run_application([
        (r'/example1', Example1SocketHandler),
    ])

if __name__ == '__main__':
    main()