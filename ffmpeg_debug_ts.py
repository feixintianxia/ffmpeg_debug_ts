# -*- coding: cp936 -*-
# !/usr/bin/python
##############################################################################
 # Copyright 2015 Jeff <163jogh@gmail.com>
##############################################################################
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #     http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
##############################################################################
 # @brief visualization for ffmpeg -debug_ts
##############################################################################

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

'''
demuxer -> ist_index:1 type:audio next_dts:2194875219 next_dts_time:2194.88 next_pts:2194875219 next_pts_time:2194.88 pkt_pts:2194853 pkt_pts_time:2194.85 pkt_dts:2194853 pkt_dts_time:2194.85 off:0 off_time:0

demuxer+ffmpeg -> ist_index:1 type:audio pkt_pts:2194853 pkt_pts_time:2194.85 pkt_dts:2194853 pkt_dts_time:2194.85 off:0 off_time:0

muxer <- type:audio pkt_pts:197536770 pkt_pts_time:2194.85 pkt_dts:197536770 pkt_dts_time:2194.85 size:121

'''
def ffmpeg_log_analyse( flog ):
    '''
    Collect data into a global 3-layer map object 'figData' like this:
        { streamid : { ts_name : [-ts-] } }
    '''
    import re
    demuxExp = r"ist_index:(?P<streamid>\d+)\s+"
    demuxExp += r"type:(?P<type>(audio|video))\s+"
    demuxExp += r"next_dts:(\d+)\s+"
    demuxExp += r"next_dts_time:(?P<next_dts>[.\d]+)\s+"
    demuxExp += r"next_pts:(\d+)\s+"
    demuxExp += r"next_pts_time:(?P<next_pts>[.\d]+)\s+"
    demuxExp += r"pkt_pts:(\d+)\s+"
    demuxExp += r"pkt_pts_time:(?P<pkt_pts>[.\d]+)\s+"
    demuxExp += r"pkt_dts:(\d+)\s+"
    demuxExp += r"pkt_dts_time:(?P<pkt_dts>[.\d]+)\s+"
    demuxObj = re.compile( demuxExp )
    figData  = {}
    print "ffmpeg_log_analyse()..."
    with open( flog, 'r' ) as f:
        for line in f:
            demuxMatch = demuxObj.search( line )
            if demuxMatch:
                frame_ts = demuxMatch.groupdict()
                type = frame_ts.pop( 'type' )
                streamid = frame_ts.pop( 'streamid' )
                if streamid not in figData:
                    ''' insert stream '''
                    figData[streamid] = {k:[] for k in frame_ts.keys()}
                for k, v in frame_ts.iteritems():
                    f = float(v)
                    if f > float(opt.start) and f < float(opt.end):
                        figData[streamid][k].append( float(v) )
        #end for line
    #end with open()
    return figData
#end def


def ffmpeg_log_draw( opt, figData ):
    print "ffmpeg_log_draw()..."
    figTitle = opt.out
    streams = figData.keys()
    
    nStreams = len( streams )
    fig = plt.figure( figTitle, figsize = (9*2, nStreams*3) )
    gs  = gridspec.GridSpec( nStreams, 2 )
    
    for i, sid in enumerate( streams ):
        stream = figData[sid]
        axInc = fig.add_subplot( gs[i, 0] )
        axInc.set_title( "stream:" + sid + " ts_inc" )
        axInc.set_xlabel( "ts" )
        axInc.set_ylabel( "ts inc" )
        if float(opt.start) > float(-sys.float_info.max):
            axInc.set_xlim(left = float(opt.start) )
        if float(opt.end) < float(sys.float_info.max):
            axInc.set_xlim(right = float(opt.end) )
        
        axTs = fig.add_subplot( gs[i, 1] )
        axTs.set_title( "stream:" + sid )
        axTs.set_xlabel( "order" )
        axTs.set_ylabel( "ts" )
            
        for j, tsName in enumerate( stream ):
            if opt.select and tsName not in opt.select:
                continue
            tsList = stream[tsName]
            tsCurr = np.array(tsList[0:len(tsList)-1])
            tsNext = np.array(tsList[1:len(tsList)])
            tsInc  = tsNext - tsCurr
            
            tsLable = "stream-" + sid + ":" + tsName
            if opt.comp:
                axTs.semilogy( tsCurr, '-*', label = tsLable )
                axInc.loglog( tsCurr, tsInc, '-*', label = tsLable )
            else:
                axTs.plot( tsCurr, '-*', label = tsLable )
                axInc.plot( tsCurr, tsInc, '-*', label = tsLable )
                
            for i, jump in enumerate( tsInc ):
                if (jump>opt.threshold or jump < 0):
                    print "stream{:s}.{:s} has large inc {:f} at {:f}".format( sid, tsName, jump, tsCurr[i] )
                    
        axInc.legend( fontsize = 10, loc = 0 )
        axInc.grid( True )
    fig.tight_layout()
    fig.savefig( figTitle )
    #plt.close( fig )
    plt.show( fig )
    #end for tsName, tsList in figData.iteritems()

def ffprobe_log_analyse( flog ):
    pass
#end def

def opt_define():
    import sys
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input",
                      help=r"movie to be analyzed")
    parser.add_option("-l", "--log", dest="log",
                      help="log to be analyzed if you don't specify movie")
    parser.add_option("-o", "--out", dest="out",
                      help=r"Name for saved picture.")
    parser.add_option("-s", "--start", dest="start",
                      default=float(-sys.float_info.max),
                      help="start time")
    parser.add_option("-e", "--end", dest="end",
                      default=float(sys.float_info.max),
                      help="end time")
    parser.add_option("-d", "--decoder", dest="decoder",
                      default="ffmpeg",
                      help="Decoder type: ffmpeg or ffprobe. [%default]")
    parser.add_option("-t", "--threshold", dest="threshold",
                      default=1,
                      help="Time inc above the threshold will trigger error report.")
    parser.add_option("-c", "--compress", dest="comp",
                      default=0, action = "store_true",
                      help="Whether use log scaling axises. [%default]")
    parser.add_option("--select", dest="select",
                      default=r"pkt_pts,pkt_dts",
                      help="select time-stamp type for showing. [%default]")
    return parser

def opt_check(opt):
    import sys
    if not opt.input and not opt.log:
        sys.exit("Error : No input or log specified")
    if not opt.log:
        opt.log = opt.input + "." + opt.decoder + ".log"
    if os.path.isfile(opt.log):
        print "Warning: " + opt.log + " already exist."
    if not opt.out:
        opt.out = opt.log + ".png"
    if opt.select:
        opt.select = opt.select.split(",")
        fullset = ["pkt_pts", "pkt_dts", "next_pts", "next_dts"]
        exset = [i for i in opt.select if i not in fullset]
        if exset:
            print "Error: --select (", exset, ") out of", fullset
            exit(1)
    return 0


if __name__ == "__main__":
    import os, sys
    parser = opt_define()
    (opt, args) = parser.parse_args()
    print "option value:\n", opt
    if opt_check(opt):
        sys.exit("Error: Invalid options")
      
    if opt.input:
        cmd = opt.decoder + " -i " + opt.input
        if opt.decoder == "ffmpeg":
            cmd += " -debug_ts -c:v copy -c:a copy -f null out.null >"
        else:
            cmd += " -show_frames -of xml >"
        cmd += opt.log + " 2>&1"
        print "excute[ " + cmd + " ]"
        
        r = os.system(cmd)
        if r:
            sys.exit("Decoding failed !!!")
   
    figData = {}
    if opt.decoder == "ffmpeg":
        figData = ffmpeg_log_analyse( opt.log )
        #figData = ffmpeg_log_process( opt, figData )
        ffmpeg_log_draw( opt, figData )
    '''
    else:
        figData = ffprobe_log_analyse( opt.log )
    '''
    exit(0)