#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time
from sensors import Push_Button
from multiprocessing import Process


def main(argv):
    input_port = 5555
    output_port = 5556
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "vi:o:", ["verbose", "input-port=", "output-port="])
    except getopt.GetoptError:
        print 'controller.py -v -i <input_port> -o <output_port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'controller.py -v -i <input_port> -o <output_port>'
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-i", "--input-port"):
            input_port = int(arg)
        elif opt in ("-o", "--ouput-port"):
            output_port = int(arg)

    try:
        # Create a new python interface.
        if verbose:
            print("Sensor controller will recieve on port %d" % input_port)
            print("Further, sensor controller will tell sensors to publish to port %d" % output_port)
        context = zmq.Context()

        socket_sub = context.socket(zmq.SUB)
        socket_sub.connect("tcp://localhost:%d" % input_port)
        socket_sub.setsockopt(zmq.SUBSCRIBE, b"")

        _sensors = []
        _processes = []

        while True:
            try:
                msg = socket_sub.recv()

                if verbose:
                    print msg

                dicty = json.loads(msg)

                # The sensor you want to spin up, such as push_button
                sensor = dicty.get('sensor')

                if sensor == 'push_button':
                    # The action you want to do, such as 'start' or 'stop' or 'status'
                    action = dicty.get('action')
                    if action == 'start':
                        # spin up the push button thing
                        pin = dicty.get('pin', 2)
                        rate = dicty.get('rate', 1.)
                        push_btn = Push_Button(pin=pin, rate=rate, port=output_port, verbose=verbose)
                        push_btn_prc = Process(target=push_btn.run)
                        push_btn_prc.start()
                        _sensors.append({
                            'sensor': push_btn,
                            'process': push_btn_prc
                        })
                        if verbose:
                            print("Started push button on pin %d" % pin)
                    elif action == 'stop':
                        # stop a push button thing
                        for sensor_obj in _sensors:
                            sensor = sensor_obj.get('sensor')
                            print sensor
                            if isinstance(sensor, Push_Button):
                                print "sensor is push button"
                                pin = dicty.get('pin')
                                if sensor.pin == pin:
                                    sensor.stop()
                                    proc = sensor_obj.get('process')
                                    proc.terminate()
                                    _sensors.remove(sensor_obj)
                                    if verbose:
                                        print("Removed push button on pin %d" % pin)
                    else:
                        print "Action not found"
                else:
                    if verbose:
                        print "unknown sensor"
                        print msg

            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Mock Subber Cleaned Up"
                socket_sub.close()
                context.term()
                for sensor in _sensors:
                    sensor.stop()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
