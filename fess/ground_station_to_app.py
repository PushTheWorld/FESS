#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import time

from apps import App3DR

STUB_PMT = False
try:
    import pmt
except ImportError:
    STUB_PMT = True


def send_to_gs(pub=None, prefix=None, data=None, verbose=False):
    if not STUB_PMT:
        meta = pmt.to_pmt(prefix)
        pmtdata = pmt.to_pmt(data)
        msg = pmt.cons(meta, pmtdata)
        pub.send(pmt.serialize_str(msg))
        if verbose:
            print meta, data
    else:
        pub.send(json.dumps({
            'prefix': prefix,
            'data': data
        }))
        if verbose:
            print json.dumps({
                'prefix': prefix,
                'data': data
            })


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

        # ZMQ likes to take it's time to set up
        time.sleep(1.0)

        app = App3DR(heartbeat_rate=1., fess_send=send_to_gs, pub=socket_pub, verbose=verbose)
        app.take_off()
        app.set_power(1650)

        while True:
            try:
                msg = socket_sub.recv()
                if not STUB_PMT:
                    rawr = str(pmt.deserialize_str(msg)).split('.')[1]
                    rawr_str = rawr[3:-2].split(' ')
                    data = [int(i) for i in rawr_str]
                    app.process_data(prefix='none', data=data)
                else:
                    print msg
            except KeyboardInterrupt:
                print "W: interrupt received, stopping"
                print "Telling drone to land"
                app.land()
                time.sleep(0.1)
                print "PubSub Cleaned Up"
                socket_pub.close()
                socket_sub.close()
                context.term()
    except BaseException as e:
        print e


if __name__ == '__main__':
    main(sys.argv[1:])
