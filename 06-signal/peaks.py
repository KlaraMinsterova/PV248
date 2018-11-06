import sys
import wave
import struct
import numpy

file = wave.open(sys.argv[1])

channelsCount = file.getnchannels()
samplesCount = file.getnframes()
sampleRate = file.getframerate()
windowsCount = samplesCount // sampleRate
bitRate = samplesCount * channelsCount
lowPeak = None
highPeak = None

waveData = file.readframes(bitRate)
fmt = str(bitRate) + "h"
data = struct.unpack(fmt, waveData)

if channelsCount == 2:
    mono = []
    for j in range(0, len(data), 2):
        mono.append((data[j] + data[j + 1]) / 2)
    data = numpy.array(mono)

for j in range(windowsCount):
    start = j * sampleRate
    end = (j + 1) * sampleRate
    fourier = numpy.fft.rfft(data[start:end])
    absolute = numpy.abs(fourier)
    average = numpy.mean(absolute)
    peakLimit = average * 20

    for frequency, amplitude in enumerate(absolute):
        if amplitude > peakLimit:
            if lowPeak is None or frequency < lowPeak:
                lowPeak = frequency
            if highPeak is None or frequency > highPeak:
                highPeak = frequency

if lowPeak is None:
    print("no peaks")
else:
    print("low: {0}, high: {1}".format(lowPeak, highPeak))