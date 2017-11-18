#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Uhd Psk Burst Control Rpi
# Description: Used to run on the RPI3 for communcations with the custom contorl messages
# Generated: Fri Sep  8 10:11:20 2017
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import burst
import es
import mapper
import random
import time
import uaslink


class uhd_psk_burst_control_rpi(gr.top_block):

    def __init__(self, pre_bits=[0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0], pre_bits_0=[0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0]):
        gr.top_block.__init__(self, "Uhd Psk Burst Control Rpi")

        ##################################################
        # Parameters
        ##################################################
        self.pre_bits = pre_bits
        self.pre_bits_0 = pre_bits_0

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 100e3
        self.gain = gain = 30
        #self.freq = freq = 5729000000 # Ch 1
        #self.freq = freq = 5759000000 # Ch 2
        #self.freq = freq = 5767000000 # Ch 3
        #self.freq = freq = 5775000000 # Ch 4
        #self.freq = freq = 5819000000 # Ch 5
        #self.freq = freq = 5827000000 # Ch 6
        #self.freq = freq = 5835000000 # Ch 7
        #self.freq = freq = 5843000000 # Ch 8
        self.freq = freq = 3075000000
        self.burst_size = burst_size = 288

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(freq, samp_rate/2.0), 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uaslink_pymavlink_source_sink_pp_0 = uaslink.pymavlink_source_sink_pp('/dev/ttyACM0',57600)
        self.uaslink_pdu_vector_to_pdu_control_0 = uaslink.pdu_vector_to_pdu_control()
        self.uaslink_mavlink_control_0 = uaslink.mavlink_control('127.0.0.1:14560', 57600)
        self.mapper_demapper_msg_0 = mapper.demapper_msg(mapper.QPSK, ([0,1,3,2]))
        self.es_trigger_edge_f_0 = es.trigger_edge_f(5,burst_size*8,100,gr.sizeof_gr_complex,500)
        self.es_sink_0 = es.sink(1*[gr.sizeof_gr_complex],8,64,0,2,0)
        self.es_handler_pdu_0 = es.es_make_handler_pdu(es.es_handler_print.TYPE_C32)
        self.burst_synchronizer_v4_0 = burst.synchronizer_v4(int(samp_rate), 2, (pre_bits), ([0,1,3,2]))
        self.burst_slicer_0 = burst.slicer()
        self.burst_randomizer_0 = burst.randomizer(([0,14,15]), ([1,0,0,1,0,1,0,1,0,0,0,0,0,0,0]), 100000)
        self.burst_preamble_correlator_0 = burst.preamble_correlator(2, 0.35, (pre_bits))
        self.burst_length_detect_0 = burst.length_detect()
        self.burst_framealign_0 = burst.framealign(len(pre_bits), 1024)
        self.burst_deframer_0 = burst.deframer()
        self.burst_correlator_filter_0 = burst.correlator_filter(100, 1e-4, -10)
        self.blocks_message_debug_0 = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.burst_deframer_0, 'pdus'), (self.uaslink_pdu_vector_to_pdu_control_0, 'Vector_IN'))
        self.msg_connect((self.burst_framealign_0, 'fpdus'), (self.burst_slicer_0, 'fpdus'))
        self.msg_connect((self.burst_length_detect_0, 'cpdus'), (self.burst_synchronizer_v4_0, 'cpdus'))
        self.msg_connect((self.burst_randomizer_0, 'pdus'), (self.burst_deframer_0, 'pdus'))
        self.msg_connect((self.burst_slicer_0, 'pdus'), (self.burst_randomizer_0, 'pdus'))
        self.msg_connect((self.burst_synchronizer_v4_0, 'cpdus'), (self.mapper_demapper_msg_0, 'cpdus'))
        self.msg_connect((self.es_handler_pdu_0, 'pdus_out'), (self.burst_length_detect_0, 'cpdus'))
        self.msg_connect((self.es_trigger_edge_f_0, 'edge_event'), (self.es_handler_pdu_0, 'handle_event'))
        self.msg_connect((self.es_trigger_edge_f_0, 'which_stream'), (self.es_sink_0, 'schedule_event'))
        self.msg_connect((self.mapper_demapper_msg_0, 'fpdus'), (self.burst_framealign_0, 'fpdus'))
        self.msg_connect((self.uaslink_mavlink_control_0, 'MAVLink_OUT'), (self.uaslink_pymavlink_source_sink_pp_0, 'MAVLink_IN'))
        self.msg_connect((self.uaslink_pdu_vector_to_pdu_control_0, 'Control_OUT'), (self.uaslink_mavlink_control_0, 'Command'))
        self.msg_connect((self.uaslink_pymavlink_source_sink_pp_0, 'MAVLink_OUT'), (self.uaslink_mavlink_control_0, 'MAVLink_IN'))
        self.connect((self.burst_correlator_filter_0, 0), (self.es_trigger_edge_f_0, 0))
        self.connect((self.burst_preamble_correlator_0, 0), (self.burst_correlator_filter_0, 0))
        self.connect((self.es_trigger_edge_f_0, 0), (self.es_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.burst_preamble_correlator_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.es_trigger_edge_f_0, 1))

    def get_pre_bits(self):
        return self.pre_bits

    def set_pre_bits(self, pre_bits):
        self.pre_bits = pre_bits

    def get_pre_bits_0(self):
        return self.pre_bits_0

    def set_pre_bits_0(self, pre_bits_0):
        self.pre_bits_0 = pre_bits_0

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq, self.samp_rate/2.0), 0)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0.set_gain(self.gain, 0)


    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(uhd.tune_request(self.freq, self.samp_rate/2.0), 0)

    def get_burst_size(self):
        return self.burst_size

    def set_burst_size(self, burst_size):
        self.burst_size = burst_size


def argument_parser():
    description = 'Used to run on the RPI3 for communcations with the custom contorl messages'
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option, description=description)
    return parser


def main(top_block_cls=uhd_psk_burst_control_rpi, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
