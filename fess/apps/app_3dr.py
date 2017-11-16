#! /usr/bin/env python
import os
import sys
import json
import getopt
import zmq
import threading
import time

kModeAltHold = 'ALT_HOLD'
kModeLoiter = 'LOITER'
kModeStabilize = 'STABILIZE'

kPrefixHeartbeat = 'heartbeat'
kPrefixLand = 'land'
kPrefixRCOverride = 'rc_override'
kPrefixSensor = 'sensor'
kPrefixTakeOff = 'takeoff'

kOveride = 1500


class App3DR(object):
    def __init__(self, heartbeat_rate=1., fess_send=None, mode=kModeAltHold, pub=None, verbose=False):
        self.heartbeat_rate = heartbeat_rate
        self.verbose = verbose
        self.fess_send = fess_send
        # Create 1 sec thread send
        self.running = True
        self.thread = threading.Thread(target=self.send_heartbeat)
        self.thread.daemon = True
        self.flying = 0
        self.thread.start()
        self.data = [0]*8
        self.mode = mode
        self.pub = pub

        self.set_defaults()

    def set_defaults(self):
        self.data[0] = kOveride
        self.data[1] = kOveride
        self.data[2] = kOveride

    def set_power(self, val):
        self.data[2] = val
        self.send(kPrefixRCOverride)

    def set_pitch(self, val):
        self.data[1] = val
        self.send(kPrefixRCOverride)

    def set_yaw(self, val):
        self.data[0] = val
        self.send(kPrefixRCOverride)

    def send(self, prefix):
        self.fess_send(pub=self.pub, prefix=prefix, data=self.data, verbose=self.verbose)

    def land(self):
        self.set_defaults()
        self.send(kPrefixRCOverride)
        time.sleep(0.1)
        self.send(kPrefixLand)
        self.flying = 0

    def take_off(self):
        if self.mode == kModeStabilize:
            self.data[7] = 0
        elif self.mode == kModeAltHold:
            self.data[7] = 1
        elif self.mode == kModeLoiter:
            self.data[7] = 2

        self.send(kPrefixTakeOff)
        # time.sleep(5.0)
        self.flying = 1

    def send_heartbeat(self):
        while self.running:
            if self.flying == 1:
                self.send(kPrefixHeartbeat)
            time.sleep(self.heartbeat_rate)

    def process_data(self, prefix, data):
        if prefix == kPrefixTakeOff:
            print "take off!"
        elif prefix == kPrefixHeartbeat:
            print "heartbeat"
        elif prefix == kPrefixRCOverride:
            print "rc override"
        elif prefix == kPrefixSensor:
            print "sensor"

        print data
