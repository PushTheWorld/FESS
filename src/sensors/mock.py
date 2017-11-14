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
    counter = 0
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
            print("Mock sensor will publish on local host on port %d" % port)
        context = zmq.Context()
        socket_pub = context.socket(zmq.PUB)
        socket_pub.bind("tcp://*:%d" % port)

        while True:
            try:
                socket_pub.send_string(json.dumps({
                    'value': counter
                }))

                counter += 1
                time.sleep(1)

            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Mock Pubber Cleaned Up"
                socket_pub.close()
                context.term()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
