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
    data=[0]*8
    counter = 0
    try:
        opts, args = getopt.getopt(argv, "vp:", ["verbose", "port="])
    except getopt.GetoptError:
        print 'ground_station.py -v -p <port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'ground_station.py -v -p <port>'
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-p", "--port"):
            port = int(arg)

    try:
        # Create a new python interface.
        if verbose:
            print("Ground station will publish messages to controller on port %d" % port)
        context = zmq.Context()
        socket_pub = context.socket(zmq.PUB)
        socket_pub.bind("tcp://*:%d" % port)

        time.sleep(1)

        # Warm up
        for i in range(10):
            socket_pub.send_string(json.dumps({
                'action': 'status',
                'sensor': 'controller'
            }))

        socket_pub.send_string(json.dumps({
            'action': 'start',
            'sensor': 'push_button',
            'pin': 2,
            'rate': 1.
        }))

        time.sleep(1)

        socket_pub.send_string(json.dumps({
            'action': 'stop',
            'sensor': 'push_button',
            'pin': 2
        }))

        socket_pub.close()
        context.term()

    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
