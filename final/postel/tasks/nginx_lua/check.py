#!/usr/bin/env python3

import os
import os.path
import sys

#sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "packages"))

import checklib
import http.server
from io import BytesIO
import logging
from PIL import Image
import random
import requests
import re
import string
import socketserver
import subprocess
import threading

PORT = 8000
SIZES = {'small': 100, 'medium': 500, 'large': 1000, 'xlarge': 2000}
INTERFACE = os.environ.get('VM_HOST_INTERFACE', 'tap0')
PORTS_FOR_SERVER = list(range(10000, 11000))

CWD = os.path.abspath(os.path.dirname(__file__))

def get_ip_address():
    return subprocess.check_output(['ifdata', '-pa', INTERFACE]).decode().strip()
    ### return netifaces.ifaddresses(INTERFACE)[2][0]['addr']

def get_full_path(relative_path):
    return os.path.join(CWD, relative_path)

def get_file_content(filename):
    with open(get_full_path(filename)) as f:
        return f.read()

def get_binary_file_content(filename):
    with open(get_full_path(filename), 'rb') as f:
        return f.read()


class HttpServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.counter += 1

        if self.server.counter > 1:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Too late!')
            return

        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(get_binary_file_content(self.server.filename))
        return


class HttpServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    def __init__(self, filename):
        self.filename = filename
        self.counter = 0
        success = False
        while not success:
            try:
                success = True
                port = random.choice(PORTS_FOR_SERVER)
                super(http.server.HTTPServer, self).__init__(('0.0.0.0', port), HttpServerHandler)
            except:
                success = False

    def start(self):
        port = self.socket.getsockname()[1]
        logging.info('Started http server on 0.0.0.0:%d' % port)
        try:
            self.serve_forever()
        except Exception as e:
            logging.warn(e)
        try:
            self.server_close()
        except Exception as e:
            logging.warn(e)

class NginxLuaChecker(checklib.Checker):
    def equal_strings(self, str1, str2):
        str1 = re.sub('\s', '', str1)
        str2 = re.sub('\s', '', str2)
        return str1 == str2

    def test_text(self, url, local_filename, error_message='Serve static file correctly!'):
        logging.info('Check that content of "%s" is equal to content of local file' % url)
        service_data = requests.get(url, allow_redirects=False).text
        local_data = get_file_content(local_filename)
        if not self.equal_strings(service_data, local_data):
            logging.warn('Contents are different!')
            print(error_message)
            return checklib.STATUS_NOT_OK
        return checklib.STATUS_OK

    def test_binary(self, url, local_filename, error_message='Serve static file correctly!'):
        logging.info('Check that content of "%s" is equal to content of local file' % url)
        r = requests.get(url, allow_redirects=False)
        if r.status_code != 200:
            logging.warn('Status code isn\'t 200 OK')
            print(error_message)
            return checklib.STATUS_NOT_OK
        service_data = r.raw
        local_data = get_binary_file_content(local_filename)
        if service_data != local_data:
            logging.warn('Contents are different!')
            print(error_message)
            return checklib.STATUS_NOT_OK
        return checklib.STATUS_OK

    def check_403(self, url):
        logging.info('Check that "%s" returns 403 Forbidden' % url)
        if requests.get(url, allow_redirects=False).status_code != 403:
            print("You must deny access to local images without authorization cookie")
            return checklib.STATUS_NOT_OK
        return checklib.STATUS_OK

    def check_200(self, url):
        logging.info('Check that "%s" returns 200 OK' % url)
        if requests.get(url, allow_redirects=False).status_code != 200:
            print("You must allow access to local scripts and css files without authorization cookie")
            return checklib.STATUS_NOT_OK
        return checklib.STATUS_OK

    def get_auth_cookie(self, url):
        r = requests.get(url, allow_redirects=False)
        filename = re.sub('.*\/auth\/', '', url)
        logging.info('Cookies: %s' % str(r.cookies))
        if r.cookies.get('auth_' + filename) == None:
            logging.warn('Auth cookies has\'t been set')
            print('Can\'t get authorization cookie for static file')
            return None
        return r.cookies

    def check_image_size(self, image, size, error_message):
        try:
            image = Image.open(BytesIO(image))
        except Exception as e:
            logging.warn(e)
            print(error_message)
            print('Can\'t parse your image')
            return checklib.STATUS_NOT_OK

        w, h = image.size
        logging.info('Size of image is %dx%d', w, h)
        if w > size or h > size:
            print(error_message)
            print('Your scaling is invalid!')
            return checklib.STATUS_NOT_OK
        if w != size and h != size:
            print(error_message)
            print('Your scaling is invalid!')
            return checklib.STATUS_NOT_OK

        return checklib.STATUS_OK

    def test_image(self, url, error_message):
        logging.info('Test image on %s' % url)
        size = random.choice(list(SIZES.keys()))
        url = url.replace('<size>', size)

        cookie_jar = self.get_auth_cookie(re.sub('\/static\/', '/auth/', url))
        if cookie_jar is None:
            return checklib.STATUS_NOT_OK

        r = requests.get(url, cookies=cookie_jar, allow_redirects=False)
        if r.status_code != 200:
            logging.warn('Status code isn\'t 200 OK')
            print(error_message)
            return checklib.STATUS_NOT_OK

        return self.check_image_size(r.content, SIZES[size], error_message)

    def test_remote(self, url, error_message):
        http_server = HttpServer('remote/cat.jpg')
        t = threading.Thread(target=http_server.start)
        t.start()

        try:
            host = get_ip_address()
            port = http_server.socket.getsockname()[1]

            size = random.choice(list(SIZES.keys()))
            url = url.replace('<size>', size)

            url += ('%s:%d/' + ''.join([random.choice(string.ascii_lowercase + '///') for _ in range(20)]) + '/main.jpg') % (host, port)

            r = requests.get(url, allow_redirects=False)
            if r.status_code != 200:
                logging.warn('Status code isn\'t 200 OK')
                print(error_message)
                return checklib.STATUS_NOT_OK

            ## First attempt
            r = requests.get(url, allow_redirects=False)
            if r.status_code != 200:
                logging.warn('Status code isn\'t 200 OK')
                print(error_message)
                return checklib.STATUS_NOT_OK

            result = self.check_image_size(r.content, SIZES[size], error_message)
            if result != checklib.STATUS_OK:
                return result

            ## Second attempt
            r = requests.get(url, allow_redirects=False)
            if r.status_code != 200:
                logging.warn('Status code isn\'t 200 OK')
                print(error_message)
                return checklib.STATUS_NOT_OK

            result = self.check_image_size(r.content, SIZES[size], 'You must set up a cache for remote images')
            if result != checklib.STATUS_OK:
                return result

            return checklib.STATUS_OK
        finally:
            try:
                http_server.server_close()
            except Exception as e:
                logging.warn(e)


    def check(self, host):
        host = '%s:%d' % (host, PORT)
        last_exception = None
        for _ in range(3):
            try:
                return self.inline_checks(
                    (self.test_text, 'http://%s/static/local/jquery.min.js' % host, 'static/jquery.min.js', 'Serve javascript files as /static/local/*'),
                    (self.check_403, 'http://%s/static/local/%s/dog.png' % (host, random.choice(list(SIZES.keys())))),
                    (self.check_200, 'http://%s/static/local/templates.js' % host),
                    (self.test_image, 'http://%s/static/local/<size>/turtle.jpg' % host, 'Serve images as /static/local/<size>/*'),
                    (self.test_image, 'http://%s/static/local/<size>/turtle.jpg' % host, 'Serve images as /static/local/<size>/*'),
                    (self.test_image, 'http://%s/static/local/<size>/dog.png' % host, 'Serve images as /static/local/<size>/*'),
                    (self.test_image, 'http://%s/static/local/<size>/dog.png' % host, 'Serve images as /static/local/<size>/*'),
                    (self.test_remote, 'http://%s/static/remote/<size>/' % host, 'Serve remote images as /static/remote/<size>/*'),
                )
            except requests.exceptions.ConnectionError as e:
                print("Exception: {0}".format(e), file=sys.stderr)
                last_exception = e

        if last_exception is not None:
            raise last_exception


if __name__ == '__main__':
    checklib.run_checker(NginxLuaChecker())
