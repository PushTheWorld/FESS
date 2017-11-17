#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time
from sensors import Push_Button
from multiprocessing import Process

STUB_PMT = False
try:
    import pmt
except ImportError:
    STUB_PMT = True

kPrefixSensor = 'sensor'


class Controller(object):
    def __init__(self, input_port=15000, output_port=14000, verbose=False):
        self.sensors = []
        self.verbose = verbose
        self.input_port = input_port
        self.output_port = output_port

        self.context = zmq.Context()
        self.socket_sub = self.context.socket(zmq.SUB)
        self.socket_sub.connect("tcp://localhost:%d" % input_port)
        self.socket_sub.setsockopt(zmq.SUBSCRIBE, b"")

        self.context = zmq.Context()
        self.socket_pub = self.context.socket(zmq.PUB)
        self.socket_pub.bind("tcp://127.0.0.1:%d" % output_port)

        if self.verbose:
            print("Sensor controller will recieve on port %d" % self.input_port)
            print("Further, sensor controller will tell sensors to publish to port %d" % self.output_port)

    def send(self, msg):
        self.socket_pub.send(msg)

    def push_button_start(self, pin=4, rate=1.):
        """
        Used to start a push button sensor on pin that is polled at rate
        :param pin:
        :param rate:
        :return:
        """
        push_btn = Push_Button(pin=pin,
                               rate=rate,
                               port=self.output_port,
                               verbose=self.verbose,
                               new_read_cb=self.send)
        push_btn_prc = Process(target=push_btn.run)
        push_btn_prc.start()
        self.sensors.append({
            'sensor': push_btn,
            'process': push_btn_prc
        })
        if self.verbose:
            print("Started push button on pin %d" % pin)

    def push_button_stop(self, pin=4):
        """
        Used to stop a push button
        :param pin:
        :return:
        """
        for sensor_obj in self.sensors:
            sensor = sensor_obj.get('sensor')
            if isinstance(sensor, Push_Button):
                if sensor.pin == pin:
                    sensor.stop()
                    proc = sensor_obj.get('process')
                    proc.terminate()
                    self.sensors.remove(sensor_obj)
                    if self.verbose:
                        print("Removed push button on pin %d" % pin)

    def cleanup(self):
        self.socket_pub.close()
        self.socket_sub.close()
        self.context.term()
        for sensor in self.sensors:
            sensor.stop()


def main(argv):
    input_port = 15000
    output_port = 14000
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "vi:o:", ["verbose", "input-port=", "output-port="])
    except getopt.GetoptError:
        print 'controller_rpi.py -v -i <input_port> -o <output_port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'controller_rpi.py -v -i <input_port> -o <output_port>'
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-i", "--input-port"):
            input_port = int(arg)
        elif opt in ("-o", "--ouput-port"):
            output_port = int(arg)

    try:
        # Create a new python interface.
        ctrl = Controller(input_port=input_port, output_port=output_port, verbose=verbose)
        ctrl.push_button_start(pin=2, rate=0.25)
        ctrl.push_button_start(pin=3, rate=0.25)
        ctrl.push_button_start(pin=4, rate=0.25)
        ctrl.push_button_start(pin=17, rate=0.25)

        while True:
            try:
                msg = ctrl.socket_sub.recv()
                data = [0] * 8

                if not STUB_PMT:
                    prefix, rawr = str(pmt.deserialize_str(msg)).split('.')
                    prefix = prefix[1:]
                    rawr_str = rawr[3:-2].split(' ')
                    for i in range(len(rawr_str)):
                        try:
                            data[i] = int(rawr_str[i])
                        except BaseException:
                            print "Problem parsing int at index %i becaus %s has chars that are not numbers" % (i, rawr_str[i])
                else:
                    dicty = json.loads(msg)
                    data = dicty.get('data')
                    prefix = dicty.get('prefix')
                if verbose:
                    print prefix, data

                # TODO: Add over the air sensor configuration

            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Turning off all push buttons"
                ctrl.push_button_stop(2)
                ctrl.push_button_stop(3)
                ctrl.push_button_stop(4)
                ctrl.push_button_stop(17)
                print "Cleaning up the ZMQ"
                ctrl.cleanup()

    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
