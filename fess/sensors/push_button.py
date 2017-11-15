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

STUB_PMT = False
try:
    import pmt
except ImportError:
    STUB_PMT = True


class Push_Button(object):
    def __init__(self, pin=4, rate=1., port=5557, verbose=False):
        self.pin = pin
        self.rate = rate
        self.port = port
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket_pub = self.context.socket(zmq.PUB)
        self.socket_pub.connect("tcp://localhost:%d" % port)
        self.data = [0] * 8
        self.data[0] = self.pin

        if self.verbose:
            print("GPIO will be read from GPIO %d and published on port %d every %f seconds" % (self.pin, self.port, self.rate))

    def open_button(self):
        if not STUB_GPIO:

            # using BCM pin numbering scheme
            GPIO.setmode(GPIO.BCM)

            # setup pin
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        else:

            # setup fake data generator
            print "stubbed mode"
            self.APIAlive = True

    def cleanup(self):
        if self.verbose:
            print "Mock Pubber Cleaned Up"
        self.socket_pub.close()
        self.context.term()

    def close_button(self):
        self.APIAlive = False
        if not STUB_GPIO:
            GPIO.cleanup()

    def read_val(self):
        if not STUB_GPIO:
            return GPIO.input(self.pin)
        else:
            return random.randint(0, 1)

    def run(self):
        # Open up the button
        self.open_button()

        try:
            while self.APIAlive:
                self.data[1] = self.read_val()
                if not STUB_PMT:
                    meta = pmt.to_pmt('fess')
                    pmtdata = pmt.to_pmt(self.data)
                    msg = pmt.cons(meta, pmtdata)
                    self.socket_pub.send(pmt.serialize_str(msg))
                else:
                    self.socket_pub.send(json.dumps({
                        'value': self.data[1],
                        'pin': self.data[0]
                    }))
                if self.verbose:
                    print('send_zmq fess push_btn #%d with val %d' % (self.pin, self.data[1]))
                time.sleep(self.rate)
        except KeyboardInterrupt:
            print "caught the keyboard"
            self.stop()

    def stop(self):
        self.close_button()
        self.cleanup()


def main(argv):
    port = 5556
    gpio_pin = 4
    poll_rate = 1.
    verbose = False
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

        # Create and open the push button
        if verbose:
            print "Initializing push buttons"
        push_btn = Push_Button(pin=gpio_pin, rate=poll_rate, port=port)
        push_btn.run()
        if verbose:
            print "push button finished...exiting"

    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
