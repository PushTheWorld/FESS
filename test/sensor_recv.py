#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time


def main(argv):
    port = 5556
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "va:p:", ["verbose", "port="])
    except getopt.GetoptError:
        print 'mock.py -v -p <port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'mock.py -v -p <port>'
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-p", "--port"):
            port = int(arg)

    try:
        # Create a new python interface.
        if verbose:
            print("Sensor listener will recieve on port %d" % port)
        context = zmq.Context()

        socket_sub = context.socket(zmq.SUB)
        socket_sub.connect("tcp://localhost:%d" % port)
        socket_sub.setsockopt(zmq.SUBSCRIBE, b"")

        while True:
            try:
                msg = socket_sub.recv()
                dicty = json.loads(msg)
                print dicty.get('value')

            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Mock Subber Cleaned Up"
                socket_sub.close()
                context.term()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])