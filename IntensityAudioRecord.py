#Rick Bhardwaj, 9/17/13

#Quite a few libraries, seems easiest to install in Windows/Linux (though installing matplotlib is not trivial
#in linux.) If you can't install them, don't worry! Read my comments and see the attached output shell.
import pyaudio, wave, numpy, sys, random, winsound, time
import matplotlib.pyplot as plt

#Helper method
def playBit(b):
	if(b == 1):
		winsound.Beep(440, 250)
	
	if( b == 0):
		time.sleep(0.25)

#Parameters for PyAudio stream object. Most chosen as recommended sampling rates, etc.
#One exception; RECORD_SECONDS is 8 seconds because I want my bits to be sent as tones with 1 sec duration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 8
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
startSound = False
samp = 0

#This is my synchronization loop
#This loop waits for a tone with an intensity of 3000, waits 1 second (agreed upon by sender/recepient) and starts
#I originally included a requirement of >600 Hz, but unnecessary without adverserial noise
while(startSound is not True):
    if samp > 3000:
        print("Sync time " + str(time.time()))
        startSound = True
    interval = stream.read(CHUNK)
    t = numpy.fromstring(interval, dtype='int16')
    samp = numpy.abs(t).mean()

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
        
#Chopping up our data arrays into 8 equal pieces (since we're expecting 8 bits)
#If the 35 seems arbitrary, that's because it is
e = chunks(amps, 35)
f = chunks(freqs, 35)

print("GIVEN REAL NOISE for 00111100")

#These next two loops essentially take the mean of our intensity and frequency chunks and decode them
#These thresholds work almost perfectly, save for a bit off because of sync delay
for eight in e:
        print("Mean intensity of quarter-second sample " + str(numpy.mean(eight)))
        if(numpy.mean(eight) >= 1000):
            print("Given intensity, bit decoded as 1")
        else:
            print("Given intensity, bit decoded as 0")

for freight in f:
        print("Mean frequency of quarter-second sample " + str(numpy.mean(freight)))        
        if(numpy.mean(freight) >= 400):
            print("Given frequency, bit decoded as 1")
        else:
            print("Given frequency, bit decoded as 0")

def decode(signal):
    if(signal[0] >= 350 and signal[0] <= 550 and signal[1] >= 100):
        return 1
    return 0

#I wanted to generate a new plot everytime for different volumes, but that kind of sys control would be scary
volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
correct = [0, 0, 0, 0, 0, 0, 0.75, 0.75, 0.875, 1, 1]
plt.plot(correct)
plt.xlabel("Percentage Volume")
plt.ylabel("Correct Bits Percentage")
plt.show()


#The rest of the code deals with modeled, virtual noise.
#I wrote this code before I wrote the code above. I thought we would be dealing with noise with intensity 10-100
#I was a factor of 10 off, but seemed asinine to go back and fix it. Pretend it's decibels or something.

#perfectInput is the bit stream we are sending
#perfectInput = [0, 1, 0, 1, 0, 1, 0, 1.......0,1] (100 long)
perfectInput = []
for i in range(0, 100):
    if i % 2 == 0:
        perfectInput.append(0)
    else:
        perfectInput.append(1)

#noiselessInput is how perfectInput would be transmitted with a tone, given no noise
#Each tone is represented as (Frequency, Intensity)
#noiselessInput = [[0, 0], [440, 100], [0, 0], [440, 100], [0, 0], [440, 100],.......[0, 0], [440, 100]]

noiselessInput = []
for i in range(0, 100):
    if i % 2 == 0:
        noiselessInput.append([0,0])
    else:
        noiselessInput.append([440,100])

#And testing our decoding
noiselessOutput = []
print("Noiseless Perfect Input " + str(noiselessInput))
for signal in noiselessInput:
    noiselessOutput.append(decode(signal))

print("Noiseless Perfect Output " + str(noiselessOutput))

#Simulating sending perfect 01010101 signal through IID white noise

#Helper function
#This simulates noise by adding an IID selected frequency and supplied noise (x variable in plot)
def plotNoise(iNoise):
    noiseInput = []
    for signal in noiselessInput:
        newSignal = [0, 0]
        newSignal[0] = signal[0] + random.randrange(0, 200)
        newSignal[1] = signal[1] + random.randrange(0, iNoise)
        
        noiseInput.append(newSignal)

    #print("Noise Input " + str(noiseInput))
    #Decode the noisy signal here
    noiseOutput = []
    for signal in noiseInput:
        noiseOutput.append(decode(signal))
    #print("Noise Output " + str(noiseOutput))

    #Compare to perfect input to find errors
    errors = 0
    for count in range(0, len(perfectInput)):
        if noiseOutput[count] != perfectInput[count]:
            errors += 1
            
    return [noiseOutput, errors]

#Array of errors for signals with different supplied noise intensities
#plotNoise(150)
totalErrors = []
for x in range(1, 250, 1):
    #print("Noise intensity " + str(x))
    #plotNoise(x)
    totalErrors.append(plotNoise(x)[1])

#Normalized the errors
normalized = [float(x)/float(len(totalErrors)) for x in totalErrors]
print("Normalized errors " + str(normalized))

#And plotted
plt.plot(normalized)
plt.xlabel("Mean White Noise")
plt.ylabel("Probablity of Error")
plt.show()
    
#Questions? rickbhardwaj@gmail.com
