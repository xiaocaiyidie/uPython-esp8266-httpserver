# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Global import
import socket  # Networking support
import time    # Current time
import gc      # Current time

# Local import
from request import parse_request
from config import config
from content import cb_open, cb_status, cb_getconf, cb_setconf, cb_resetconf
from content import cb_temperature, cb_temperature_json

# A simple HTTP server
class Server:
  def __init__(self, title='uServer'):
     # Constructor
     self.title = config.get_config('place')
     self.conn = None
     self.addr = None
     self.head2 = cb_open('header.txt')
     self.footer = cb_open('footer.txt')

  def activate(self, port, host='0.0.0.0'):
     # Attempts to aquire the socket and launch the server
     try:
         self.socket = socket.socket()
         self.socket.settimeout(5.0) # otherwise it will wait forever
         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         self.socket.bind((host, port))
         print("Server ", host, ":", port)
     except Exception as e:
         print(e)
     self.socket.listen(1) # maximum number of queued connections

  def wait_connections(self, sta_if):
     # Main loop awaiting connections
     refresh30 = '<meta http-equiv="refresh" content="300">\n'
     error404 = '404 - Error'

     from register import register
     rurl = config.get_config('register')
     auth = config.get_config('authorization')

     counting = 0
     startime = time.time()
     while True:
         if not sta_if.isconnected():
             print('Disconnected...')
             return

         nowtime = time.time()
         if nowtime-startime > 299: # means every 60*5 = 300 sec == 5 mins
             register(rurl, auth)
             startime = time.time()

         counting += 1
         print("Wait ", counting)

         try:
            self.conn, self.addr = self.socket.accept()
         except KeyboardInterrupt:
            print("Timeout")
            return
         except:
            continue

         try:
            req = self.conn.readline()
         except:
            continue

         # conn - socket to client // addr - clients address
         while True:
            h = self.conn.readline()
            if not h or h == b'\r\n':
                break

         # Some defaults
         code = 200
         extension = 'h'
         refresh = ''
         # determine request method (GET / POST are supported)
         r = parse_request(req)
         if r == None:
             code = 404
             content = error404
         elif r['uri'] == b'/temperature' or r['uri'] == b'/' :
             refresh=refresh30
             content = cb_temperature()
         elif r['uri'] == b'/j' :
             extension = 'j'
             content = cb_temperature_json()
             self.http_send(code, content, extension, refresh)
             continue
         elif r['uri'] == b'/status':
             content = cb_status()
         elif r['uri'] == b'/getconf':
             content = cb_getconf()
         elif b'/setconf' in r['uri']:
             if 'key' in r['args'] and 'value' in r['args']:
                 content = cb_setconf(r['args']['key'], r['args']['value'])
             elif 'key' in r['args'] :
                 content = cb_setconf(r['args']['key'], None)
             else:
                 content = cb_setconf(None, None)
             self.title = config.get_config('place') # just in case
         elif r['uri'] == b'/reboot' :
             content = '<h2>Reboot</h2></div>'
             self.http_send(code, content, extension, refresh)
             return
         elif r['file'] != b'':
             myfile = r['file']
             code = 200
             content = cb_open(myfile)
         else:
             code = 404
             content = error404

         # At end of loop just close socket and collect garbage
         self.http_send(code, content, extension, refresh)
         self.conn.close()
         gc.collect()

  def http_send(self, code, content, extension='h', refresh=''):
     mt = {'h': "text/html", 'j': "application/json"}
     codes = {200:" OK", 400:" Bad Request", 404:" Not Found", 302:" Redirect", 501:"Server Error" }
     head0 = 'HTTP/1.1 %s\r\nServer: tempserver\r\nContent-Type: %s\r\n'
     #head1 = 'Cache-Control: private, no-store\r\nConnection: close\r\n\r\n'
     head1 = 'Connection: close\r\n\r\n'

     if code not in codes: code = 501
     httpstatus = str(code) + codes[code]
     if extension not in mt: extension = 'h'
     mimetype = mt[extension]

     head0 = head0 % (httpstatus, mimetype)
     self.conn.send(head0)
     self.conn.send(head1)
     if extension != 'j':
        for c in self.head2:
            self.conn.send(c)

     # if type(content) is list or type(content) is tuple:
     if type(content) is list :
        for c in content:
            self.conn.send(c)
     elif content != '':
        self.conn.send(content)

     if extension != 'j':
        for c in self.footer:
            self.conn.sendall(c)

