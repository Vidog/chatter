import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web
import tornado.websocket

from utils import *

define('port', default=8888, help='run on the given port', type=int)

def emptyMethod():
    pass

class Application(tornado.web.Application):
    def __init__(self, handlers):
        settings = dict(
            cookie_secret='__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            xsrf_cookies=True,
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class APIEvents:
    def __init__(self):
        self.events = {}
        self.caller_events = {}
        pass

    def add_event(self, caller, system_group, group, method, callback_method, params):
        try:
            g = self.events[system_group]
        except Exception, e:
            self.events[system_group] = {}

        try:
            g = self.events[system_group][group]
        except Exception, e:
            self.events[system_group][group] = {}

        try:
            g = self.events[system_group][group][method]
        except Exception, e:
            self.events[system_group][group][method] = []

        try:
            g = self.caller_events[caller.get_unique_id()]
        except Exception, e:
            self.caller_events[caller.get_unique_id()] = []

        event = {
            'socket': caller,
            'params': params,
            'callback_method': callback_method
        }

        self.caller_events[caller.get_unique_id()].append(event)

        self.events[system_group][group][method].append(event)

    def call_event(self, caller, is_broadcast, system_group, group, method, params):
        try:
            events_list = self.events[system_group][group][method]

            for event in events_list:
                socket = event['socket']
                if not is_broadcast:
                    if socket != caller:
                        continue
                # try:
                #     caller_events = self.caller_events[caller.get_unique_id()]
                #     print 'Client ', caller.get_unique_id(), ' events:'
                #     print caller_events
                # except:
                #     continue
                socket.call_event(caller, is_broadcast, group, method, params, event)

            return True
        except Exception, e:
            return False

    def remove_caller_events(self, caller):
        pass
        #print 'Client ', caller.get_unique_id(), ' removed:'
        #del self.caller_events[caller.get_unique_id()]

class APIMethod:
    def __init__(self, _socket, _callback_id):
        self.socket = _socket
        self.callback_id = _callback_id

    def execute(self, params):
        func = self.run
        r = inspect.getargspec(func)

        args = []
        i = 0
        for arg in r.args:
            i += 1
            if i == 1:
                continue
            try:
                val = params[arg]
            except Exception, e:
                val = None
            args.append(val)

        return func(*args)

    def run(self):
        pass

class BaseSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200
    group = 'none'

    def __init__(self, *args, **kwargs):
        super(BaseSocketHandler, self).__init__(*args, **kwargs)

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        self.online = True
        self.authorized = False
        self.username = ''
        self.password = ''
        self.ws = None
        self.events = {}
        self.APIStruct = {}
        self.loadAPIStruct()
        self.request_info = req = self.request
        self.ip = ip = req.remote_ip

        try:
            self.agent = agent = req.headers['User-Agent']
        except Exception, e:
            self.agent = agent = 'Unknown'

        try:
            self.websocket_key = wskey = req.headers['Sec-Websocket-Key']
        except Exception, e:
            #@TODO: random
            self.websocket_key = wskey = 'None'

        self.unique_id = md5(ip + agent + wskey)

        BaseSocketHandler.waiters.add(self)

        #print repr(self.request)
        #HTTPRequest(protocol='http', host='vidog.vsemayki.local:8888', method='GET', uri='/call_center', version='HTTP/1.1', remote_ip='127.0.0.1', body='', headers={'Origin': 'http://callcenter.dev', 'Upgrade': 'websocket', 'Sec-Websocket-Extensions': 'x-webkit-deflate-frame', 'Sec-Websocket-Version': '13', 'Connection': 'Upgrade', 'Sec-Websocket-Key': 'wWvkhEuyFQlibcfshB9f1A==', 'Host': 'vidog.vsemayki.local:8888', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'})
        #HTTPRequest(protocol='http', host='vidog.vsemayki.local:8888', method='GET', uri='/call_center', version='HTTP/1.1', remote_ip='10.5.3.215', body='', headers={'Origin': 'http://callcenter.dev', 'Upgrade': 'websocket', 'Sec-Websocket-Extensions': 'x-webkit-deflate-frame', 'Sec-Websocket-Version': '13', 'Connection': 'Upgrade', 'Sec-Websocket-Key': 'OjPjUI6eKitMpoDUGPZDqw==', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36', 'Host': 'vidog.vsemayki.local:8888', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'})

        self.onConnect()

    def on_close(self):
        self.online = False

        self.onDisconnect()

        BaseSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    def disconnect(self):
        self.close()

    def onConnect(self):
        try:
            self.call_command(self.group, 'system', 'on_connect', {})
        except Exception, e:
            pass

    def onDisconnect(self):
        try:
            self.call_command(self.group, 'system', 'on_disconnect', {})
        except Exception, e:
            pass

    def get_unique_id(self):
        return self.unique_id

    # @classmethod
    # def send_updates(cls, chat):
    #     for waiter in cls.waiters:
    #         try:
    #             waiter.write_message(chat)
    #         except:
    #             logging.error('Error sending message', exc_info=True)

    def call_event(self, caller, is_broadcast, group, method, params, event):
        data = event['params']
        socket = event['socket']
        callback = event['callback_method']

        self.send_package({'params': params, 'data': data}, True, callback)

    def run_broadcast_event(self, group, event, params):
        Events.call_event(self, True, self.group, group, event, params)

    def run_event(self, group, event, params):
        Events.call_event(self, False, self.group, group, event, params)

    def loadAPIStruct(self):
        struct = {'system_groups': {}}

        api_dir = './api/'
        dr = os.listdir(api_dir)
        for fl in dr:
            if os.path.isdir(api_dir + fl):
                api_dir2 = api_dir + fl + '/'
                struct['system_groups'][fl] = {
                    'name': fl,
                    'path': api_dir2,
                    'groups': {}
                }
                dr2 = os.listdir(api_dir2)
                for fl2 in dr2:
                    if os.path.isdir(api_dir2 + fl2):
                        api_dir3 = api_dir2 + fl2 + '/'
                        struct['system_groups'][fl]['groups'][fl2] = {
                            'name': fl2,
                            'path': api_dir3,
                            'methods': {}
                        }
                        dr3 = os.listdir(api_dir3)
                        for fl3 in dr3:
                            if not os.path.isdir(api_dir3 + fl3):
                                file_path = api_dir3 + fl3

                                env = {
                                    'APIMethod': APIMethod,
                                    'Events': Events,
                                    'Clients': Clients,
                                    'md5': md5,
                                    'sha1': sha1
                                }
                                x = execfile(file_path, env)

                                try:
                                    obj_method = env['__api_result__']
                                except Exception, e:
                                    obj_method = emptyMethod

                                struct['system_groups'][fl]['groups'][fl2]['methods'][fl3] = {
                                    'name': fl3,
                                    'path': file_path,
                                    'method': obj_method
                                }
                            else:
                                pass
                    else:
                        pass
            else:
                pass

        gc.collect()

        self.APIStruct = struct

    def send_error(self, code, message, idx=None):
        response, success = self.error_response(code, message)
        self.send_package(response, success, idx)

    def error_response(self, code, message):
        return ({'errors': [ {'code': code, 'message': message} ]}, False)

    def on_auth(self, package, sock, params):
        return True

    def call_command(self, system_group, group, method, params, idx=None):
        return self.APIStruct['system_groups'][system_group]['groups'][group]['methods'][method + '.py']['method'](self, idx).execute(params)

    def parse_package(self, package):
        try:
            group = package['group']
            method = package['method']
            params = package['params']
            idx = package['id']

            package = {
                'socket': self,
                'group': group,
                'package': package,
                'method': method,
                'id': idx
            }

            check = self.on_auth(package, self, params)

            if check != True:
                if check == False:
                    return self.error_response(0, 'Access denied')
                return check

            result = self.call_command(self.group, group, method, params, idx)

            gc.collect()

            return result
        except Exception, e:
            print traceback.format_exc()
            return self.error_response(0, 'Exception')

    def send_package(self, response, success, idx):
        self.send_data( self.build_package(response, success, idx) )

    def send_data(self, data):
        if self.online:
            try:
                self.write_message( data )
            except Exception, e:
                #pass
                print e
                print '[Cant send message to ', self, ': client is offline]'

    def build_package(self, response, success, idx):
        return {'success': success, 'response': response, 'id': idx}

    def on_message(self, message):
        try:
            package = tornado.escape.json_decode(message)
            response, success = self.parse_package(package)
            idx = package['id']
        except Exception, e:
            print traceback.format_exc()
            response, success = self.error_response(0, 'Exception')
            idx = None

        self.send_package( response, success, idx )

        gc.collect()

def run_application(handlers):
    tornado.options.parse_command_line()
    app = Application(handlers)
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

Events = APIEvents()
Clients = {}