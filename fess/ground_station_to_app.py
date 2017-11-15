#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time

STUB_PMT = False
try:
    import pmt
except ImportError:
    STUB_PMT = True


def main(argv):
    input_port = 5556
    output_port = 5557
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "vi:o:", ["verbose", "input-port=", "output-port="])
    except getopt.GetoptError:
        print 'ground_station_to_app.py -v -i <input_port> -o <output_port>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'ground_station_to_app.py -v -i <input_port> -o <output_port>'
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
            print("Subscribing to ground station on port %d" % input_port)
            print("Publishing data to app on port %d" % output_port)

        context = zmq.Context()

        socket_sub = context.socket(zmq.SUB)
        socket_sub.connect("tcp://localhost:%d" % input_port)
        socket_sub.setsockopt(zmq.SUBSCRIBE, b"")
        socket_pub = context.socket(zmq.PUB)
        socket_pub.bind("tcp://*:%d" % output_port)

        while True:
            try:
                msg = socket_sub.recv()
                if not STUB_PMT:
                    rawr = str(pmt.deserialize_str(msg)).split('.')[1]
                    rawr_str = rawr[3:-2].split(' ')
                    data = [int(i) for i in rawr_str]
                    socket_pub.send(json.dumps({
                        'data': data[:-1]
                    }))
                else:
                    socket_pub.send(msg)
            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "PubSub Cleaned Up"
                socket_pub.close()
                socket_sub.close()
                context.term()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
