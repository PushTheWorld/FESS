#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time
import random


STUB_GPIO = False
try:
    import RPi.GPIO as GPIO
except ImportError:
    STUB_GPIO = True

class Push_Button(object):

    def __init__(self, pin=4, rate=1., btn_callback=None):
        self.pin = pin
        self.rate = rate
        self.btn_callback = btn_callback

    def open_button(self):
        if not STUB_GPIO:

            # using BCM pin numbering scheme
            GPIO.setmode(GPIO.BCM)

            # setup pin
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            if self.btn_callback is not None:
                GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.btn_callback)

        else:

            # setup fake data generator
            print "stubbed mode"
            self.APIAlive = True

    def close_button(self):
        if STUB_GPIO == False:
            GPIO.cleanup()

        self.APIAlive = False

    def read_val(self):
        if STUB_GPIO == False:
            return GPIO.input(self.pin)
        else:
            return random.randint(0, 1)




def main(argv):
    port = 5556
    gpio_pin = 4
    poll_rate = 1.
    verbose = False
    counter = 0
    try:
        opts, args = getopt.getopt(argv, "vp:g:", ["verbose", "port=", "gpio=", "rate="])
    except getopt.GetoptError:
        print 'push_button.py -v -p <port> -g <gpio> -r <rate>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'push_button.py -v -p <port> -g <gpio> -r <rate>'
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-g", "--gpio"):
            gpio_pin = int(arg)
        elif opt in ("-r", "--rate"):
            poll_rate = arg

    try:
        # Create a new python interface.
        if verbose:
            print("GPIO will be read from GPIO %d and published on port %d every %f seconds" % (gpio_pin, port, poll_rate))

        # Create the zmq publisher
        context = zmq.Context()
        socket_pub = context.socket(zmq.PUB)
        socket_pub.bind("tcp://*:%d" % port)

        # Create and open the push button
        push_btn = Push_Button(pin=gpio_pin, rate=poll_rate)
        push_btn.open_button()

        while True:
            try:
                socket_pub.send_string(json.dumps({
                    'value': push_btn.read_val(),
                    'gpio_pin': push_btn.pin
                }))

                time.sleep(push_btn.rate)

            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Mock Pubber Cleaned Up"
                socket_pub.close()
                context.term()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
