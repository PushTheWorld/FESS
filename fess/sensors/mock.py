#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time
import pmt


def main(argv):
    port = 5556
    verbose = False
    data=[0]*8
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
                meta = pmt.to_pmt('fess')
                pmtdata = pmt.to_pmt(data)
                msg = pmt.cons(meta, pmtdata)
                print('send_zmq fess')
                socket_pub.send(pmt.serialize_str(msg))

                counter += 1
                data[0] = counter
                data[1] = counter/2
                data[2] = counter*2
                data[7] = counter*4

                if counter > 255:
                    counter = 0

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
