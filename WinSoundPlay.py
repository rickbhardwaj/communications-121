import winsound, time


def playBit(b):
	if(b == 1):
		winsound.Beep(440, 1000)
	
	if( b == 0):
		time.sleep(1)

l = "00111100"

print("Time of START beep " + str(time.time()))
winsound.Beep(600, 1000)
#time.sleep(3)

print("START Begin sending " + str(time.time()))
for elem in l:
        playBit(int(elem))
print("STOP Done sending " + str(time.time()))
