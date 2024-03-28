#!/usr/bin/env python3

import RPi.GPIO as GPIO
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep

host_name = '192.168.55.101'  # IP Address of Raspberry Pi
host_port = 5553
GPIO_numbers = {'brama': 23, 'garaz': 17, 'Dul_prawy': 24, 'Dul_lewy': 27, 'Hal_przod': 5, 'Hal_bok': 6,
                'Hal_tyl': 13}


def setupGPIO(number):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(number, GPIO.OUT)


def getTemperature():
    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
    return temp


class MyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        html = '''
           <html>
            <head lang="pl">
                <meta charset="utf-8">
                
            </head>
           <body 
            style="width:100%; margin: 20px auto;">
           <h1 style="font-size: 100px;" align="center">Pilot Ogiegło</h1>
           <div class="glowny" align="center"> 
           <form action="/" method="POST">
               <input type="submit" name="submit" value="brama" style="width: 50%; height: 25%; font-size: 100px; float: left;">
               <input type="submit" name="submit" value="garaz" style="width: 50%;  height: 25%; font-size: 100px; float: left;">
               <input type="submit" name="submit" value="Dul_prawy" style="width: 50%; height: 25%; font-size: 100px; clear: both;">
               <input type="submit" name="submit" value="Dul_lewy" style="width: 50%; height: 25%; font-size: 100px; float: left;">
               <input type="submit" name="submit" value="Hal_przod" style="width: 50%; height: 25%; font-size: 100px; clear: both;">
               <input type="submit" name="submit" value="Hal_bok" style="width: 50%; height: 25%; font-size: 100px; float: left;">
               <input type="submit" name="submit" value="Hal_tyl" style="width: 50%; height: 25%; font-size: 100px; clear: both;">
            </div>
            </form>
           </body>
           </html>
        '''
        temp = getTemperature()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO(GPIO_numbers[post_data])

        GPIO.output(GPIO_numbers[post_data], GPIO.HIGH)
        sleep(1)
        GPIO.output(GPIO_numbers[post_data], GPIO.LOW)
        GPIO.output(GPIO_numbers[post_data], GPIO.OUT)
        sleep(1)
        GPIO.cleanup()
        sleep(3)
        # setupGPIO(GPIO_numbers[post_data])

        print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


# # # # # Main # # # # #

if __name__ == '__main__':
    while True:
        try:
            sleep(5)
            http_server = HTTPServer((host_name, host_port), MyServer)
            print("Server Starts - %s:%s" % (host_name, host_port))

            try:
                http_server.serve_forever()
            except KeyboardInterrupt:
                http_server.server_close()
        except OSError:
            sleep(10)
