#Rick Bhardwaj, 9/17/13

#Quite a few libraries, seems easiest to install in Windows/Linux (though installing matplotlib is not trivial
#in linux.) If you can't install them, don't worry! Read my comments and see the attached output shell.
import pyaudio, wave, numpy, sys, random, winsound, time, itertools, collections, scipy
import matplotlib.pyplot as plt
from scipy.signal import chirp, sweep_poly


codebook = {}
perms = ["".join(seq) for seq in itertools.product("01", repeat=4)]
for perm,freq in zip(perms, range(400, 10000, 9600/len(perms))):
    codebook[freq] = perm

#Parameters for PyAudio stream object. Most chosen as recommended sampling rates, etc.
#One exception; RECORD_SECONDS is 8 seconds because I want my bits to be sent as tones with 1 sec duration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 100100 #44100
RECORD_SECONDS = 3.2
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
startSound = False
samp = 0
syncFreqs = []
print("Listening...")

#This is my synchronization loop
#This loop waits for a tone with an intensity of 3000, waits 1 second (agreed upon by sender/recepient) and starts
#I originally included a requirement of >600 Hz, but unnecessary without adverserial noise
startSound = False
while(startSound is not True):
    if samp > 3000:
        print("Sync time " + str(time.time()))
        startSound = True
    #print("wait")
    interval = stream.read(CHUNK)
    t = numpy.fromstring(interval, dtype='int16')
    samp = numpy.abs(t).mean()
    #fftData = numpy.fft.rfft(t)
    #syncFreqs.append(fftData)
    #print(highestFreq)

#print("CONVOLVEEEEEEEEEEE")
#print(len(syncFreqs))
stream.stop_stream()
stream.close()
time.sleep(1)    


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


print("START Begin recording " + str(time.time()))
print("* recording")

#Data arrays that I will chop up and parse through to analyze our signal

#Raw data from PyAudio
frames = []

#Amplitude
amps = []

#Frequencies
freqs = []

#Analysis loop. Most important part of the code! Two main processes
# 1. Reads a chunk, converts to int16, stores amplitude
# 2. Uses Fast Fourier Transform to find frequency of relevant chunk
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    b = numpy.fromstring(data, dtype='int16')
    fftData = numpy.fft.rfft(b)
    highestFreq = fftData[1:].argmax() + 1
    frequency = (highestFreq * RATE)/CHUNK
    #print("FREQUENCY " + str(frequency))


    #print numpy.abs(b).mean()

    amps.append(numpy.abs(b).mean())
    freqs.append(frequency)
    frames.append(data)

print("STOP Done Recording " + str(time.time()))
print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

#Helper method

def chunks(li, n):
    for i in xrange(0, len(li), n):
        yield li[i:i+n]

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg
    return out


print("------CONVOLUTION-------")
print(len(freqs))
'''
t = numpy.linspace(0, 100, 5000001)
chirpy = chirp(t, f0=300.5, f1=1000.5, t1=10, method='quadratic')
print(numpy.convolve(chirpy, chirpy))
'''
#Chopping up our data arrays into 8 equal pieces (since we're expecting 8 bits)
#If the 35 seems arbitrary, that's because it is
e = chunkIt(amps, 16)
f = chunkIt(freqs, 64)

print("GIVEN REAL NOISE for 00111100")

def modePart(li, r):
    for i in range(len(li)):
        li[i] = round(li[i]/r)*r
        #print(li[i])
    inQuestion = collections.Counter(li)
    return inQuestion.most_common(1)[0][0]

def modeFreq(li):
    hard = [250, 296, 342, 388, 434, 480, 526, 572, 618, 664, 710, 756, 802, 848, 894, 940]
    #for i in range(len(li)):
        #li[i] = hard[min(range(len(li)), key=lambda i: abs(hard[i]-li[i]))]
    #for i in range(len(li)):
        #li[i] = min(li, key=lambda x:abs(x-li[i]))
    takeClosest = lambda num,collection:min(collection,key=lambda x:abs(x-num))
    for i in range(len(li)):
        li[i] = takeClosest(li[i], hard)
    inQuestion = collections.Counter(li)
    return inQuestion.most_common(1)[0][0]

hard = range(250, 11000, (11000-250)/64)
takeClosest = lambda num,collection:min(collection,key=lambda x:abs(x-num)) 
    

#These next two loops essentially take the mean of our intensity and frequency chunks and decode them
#I'm not actually decoding based on frequency and intensity seperately, just helped for debugging
#These thresholds work almost perfectly, save for a bit off because of sync delay
meanIntensities = []
for eight in e:
        print("Mean intensity of second sample " + str(numpy.mean(eight)))
        meanIntensities.append(numpy.mean(eight))
        #if(numpy.mean(eight) >= 1000):
            #print("Given intensity, bit decoded as 1")
        #else:
            #print("Given intensity, bit decoded as 0")

print()

meanFrequencies = []
for freight in f:
        #print("Mean frequency of second sample " + str(numpy.mean(freight)))
        print("Mode fequency of sample " + str(modePart(freight, 10)))
        #print("Matched fequency of sample " + str(modeFreq(freight)))
        meanFrequencies.append(modePart(freight, 10))
        for decode in codebook.keys():
            if numpy.mean(freight) >= decode - 200 and numpy.mean(freight) <= decode + 200:
                #print("Given frequency, tone decoded as " + codebook[decode])
                break
            
        #if(numpy.mean(freight) >= 400):
            #print("Given frequency, bit decoded as 1")
        #else:
            #print("Given frequency, bit decoded as 0")

#Zipping up a tuple of the mean frequencies and intensities I just found for the final decoding
intentfreq = []
for z in zip(meanIntensities, meanFrequencies):
        intentfreq.append(z)

#Decoding given frequency and intensity
print("---ANALYSIS---")

for starter in range(len(meanFrequencies)):
    meanFrequencies[starter] = takeClosest(meanFrequencies[starter], hard)

print(meanFrequencies)

br = 0
while(meanFrequencies[br] == 584):
    br += 1
print(br)
meanFrequencies = meanFrequencies[br:]
print(meanFrequencies)
if meanFrequencies[9] == 10938:
    print("<IN SYNC>")
else:
    print("Not " + str(meanFrequencies[9]))
    br = 9
    #while(meanFrequencies[br] != 10938):
        
#for z in intentfreq:
        #if(z[0] >= 1000 and z[1] >= 400):
                #print(1)
        #else:
                #print(0)
'''

def decode(signal):
    for decode in codebook.keys():
        if signal[0] >= decode - 200 and signal[0] <= decode + 200 and signal[1] >= 1000:
            return codebook[decode]
    return 0

#I wanted to generate a new plot everytime for different volumes, but that kind of sys control would be scary
volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
correct = [0, 0, 0, 0, 0, 0, 0.75, 0.75, 0.875, 1, 1]
plt.plot(correct)
plt.xlabel("Percentage Volume")
plt.ylabel("Correct Bits Percentage")
#plt.show()


#And testing our decoding
perfectOutput = []
perfectInput = zip(codebook.keys(), [1500] * len(codebook.keys()))
print("Noiseless Perfect Input " + str(perfectInput))
for signal in perfectInput:
    perfectOutput.append(decode(signal))

print("Noiseless Output " + str(perfectOutput))

#Simulating sending perfect 01010101 signal through IID white noise

#Helper function
#This simulates noise by adding an IID selected frequency and supplied noise (x variable in plot)
def plotNoise(iNoise):
    noiseInput = []
    for x in perfectInput:
        newSignal = [-1, -1]
        newSignal[0] = x[0] + random.randrange(0, 350)
        newSignal[1] = x[1] - random.randrange(0, iNoise)    
        noiseInput.append(newSignal)
    #Feel free to uncomment this to see our noisyInput array. Beware: 250 arrays of len = 100.
    #print(noiseInput)
   
    #print("Noise Input " + str(noiseInput))
    #Decode the noisy signal here
    noiseOutput = []
    for signal in noiseInput:
        noiseOutput.append(decode(signal))
    #print("Noise Output " + str(noiseOutput))

    #Compare to perfect input to find errors
    errors = 0
    for count in range(0, len(perfectInput)):
        if noiseOutput[count] != perfectOutput[count]:
            errors += 1
            
    return [noiseOutput, errors]

#Array of errors for signals with different supplied noise intensities
#plotNoise(150)
totalErrors = []
print("Now inputing 250 noisy signals (100 bits) of different intensities")
for x in range(1, 1000, 1):
    #print("Noise intensity " + str(x))
    #plotNoise(x)
    totalErrors.append(plotNoise(x)[1])

#Normalized the errors
normalized = [float(x)/float(len(totalErrors)) for x in totalErrors]
print("Normalized errors for noisy signals " + str(normalized))

#And plotted
plt.plot(normalized)
plt.xlabel("Mean White Noise")
plt.ylabel("Probablity of Error")
plt.show()
    
#Questions? rickbhardwaj@gmail.com
'''
