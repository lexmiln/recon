#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyaudio
import struct
import numpy
import scipy.misc

WINDOW_SIZE = 2200
CHUNK = WINDOW_SIZE / 2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# The largest amplitude we expect to see in the input signal.
MAX_AMP = 16384.


def cognise(log):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    #spectra = []

    try:

        log("RECORDING")

        # Analyses overlap 50% so that momentary sounds like glottal stops
        # aren't lost under the window.
        front = None
        back = None

        while True:

            back = [0] * CHUNK

            try:
                data = stream.read(CHUNK)
            except IOError as e:
                if e[1] != pyaudio.paInputOverflowed:
                    raise
                log("OVERFLOW")

            i = 0
            for i in xrange(CHUNK):
                # Two bytes per sample - get an index into the data.
                idx = i * 2
                short = data[idx:idx + 2]
                value = (struct.unpack("<h", short)[0]) / MAX_AMP
                # Write the value to the back chunk.
                back[i] = value

            # We can only perform the analysis if there's a front chunk.
            if front:

                # DFT
                series = front + back
                ft = numpy.fft.rfft(series * numpy.hamming(WINDOW_SIZE))

                # If my math is correct, and I'm basically making it up,
                # the second term is the first harmonic - ie. 20Hz
                # the third term is the second harmonic - 40Hz
                # We're not interested in anything below 100Hz, which
                # we assume to be nonvocal, so the first term that's interesting to us is the 7th.
                # We take 150 terms, so we get everything between 120Hz and 3120Hz.
                # According to some earlier testing, 80 terms could be enough
                # to discriminate between vowels, but for now, more data seems better.
                interesting = numpy.absolute(ft[7:157])

                #spectra.append(interesting)

                log("".join(["%s" % (asciibar(i)) for i in interesting]))

            # The back chunk is the front of the next window.
            front = back

        log("DONE RECORDING")

    except KeyboardInterrupt:
        log("Interrupted.")

    finally:

        stream.stop_stream()
        stream.close()

        p.terminate()

    #data = numpy.array(spectra)

    # print "\nDATA\n"
    #
    # print data
    # print data.shape

    #print "\nFULL PRINT\n"

    #print_fingerprint(data)

    #rdata = scipy.misc.imresize(data, (data.shape[0] / 2, 10), interp="bilinear", mode="F")

    # print "\nREDUCED DATA\n"
    #
    # print rdata
    # print rdata.shape

    #print "\nFINGERPRINT\n"

    #print_fingerprint(rdata)

    #print "\nDONE\n"


def linetest():
    print "0"        # 0
    print "1 ▏▏▏▏▏"  # 1
    print "2 ▎▎▎▎▎"  # 2
    print "3 ▍▍▍▍▍"  # 3
    print "4 ▌▌▌▌▌"  # 4
    print "5 ▋▋▋▋▋"  # 5
    print "6 ▊▊▊▊▊"
    print "7 ▉▉▉▉▉"


BARS = u" ▏▎▍▌▋"


def bar(val):
    val = min(max(val, 0), 1)
    idx = int(val * 6)
    idx = min(idx, 5)
    return BARS[idx]


#ASCIIBARS = " `.,~:i!|/?8NRMEEEE"
#ASCIIBARS = " .'`,^:\";~-_+<>i!lI?/\|()1{}[]rcvunxzjftLCJUYXZO0Q*WMB8&%$#@   "
ASCIIBARS = "  `-.:+=*%#@"
ASCIIBARS = " .,;i1IM#"

def asciibar(val):
    val = min(max(val, 0), 1)
    idx = int(val * len(ASCIIBARS))
    idx = min(idx, len(ASCIIBARS) - 1)
    return ASCIIBARS[idx]


def print_fingerprint(arr):
    for j in xrange(arr.shape[0]):
        print "".join(["%s" % (asciibar(i)) for i in arr[j, :]])


if (__name__ == "__main__"):
    cognise(lambda x: None)
