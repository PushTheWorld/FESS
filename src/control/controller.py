#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time


def main(argv):
    port = 5555
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "vp:", ["verbose", "port="])
    except getopt.GetoptError:
        print 'controller.py -v -p <port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'controller.py -v -p <port>'
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-p", "--port"):
            port = int(arg)

    try:
        # Create a new python interface.
        if verbose:
            print("Sensor controller will recieve on port %d" % port)
        context = zmq.Context()

        socket_sub = context.socket(zmq.SUB)
        socket_sub.connect("tcp://localhost:%d" % port)
        socket_sub.setsockopt(zmq.SUBSCRIBE, b"")

        while True:
            try:
                msg = socket_sub.recv()
                dicty = json.loads(msg)

                # The sensor you want to spin up, such as push_button
                sensor = dicty.get('sensor')
                # The action you want to do, such as 'start' or 'stop' or 'status'
                action = dicty.get('action')

                if sensor == 'push_button':
                    if action == 'start':
                        # spin up the push button thing
                    elif action == 'stop':
                        # stop a push button thing
                    else:
                        print "Action not found"
                else:
                    print "Sensor not supported"

            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Mock Subber Cleaned Up"
                socket_sub.close()
                context.term()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
