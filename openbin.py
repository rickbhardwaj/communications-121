import binascii, winsound, time, itertools

f = open("out.jpg", "rb")
biner = ""
try:
    byte = f.read()
    hexer = binascii.hexlify(byte)
    #print(type(bin(int(hexer, 16))))
    biner = bin(int(hexer, 16))[2:]
    #print("%s" % (binascii.hexlify(byte)))

finally:
    f.close()

perms = ["".join(seq) for seq in itertools.product("01", repeat=6)]
codebook = dict(zip(perms, range(250, 11000, (11000-250)/len(perms))))
print codebook.values()

print(codebook)
def playBit(mess):
    #print(codebook[mess])
    winsound.Beep(codebook[mess], 100)

print(time.time())
winsound.Beep(600, 1100)
print(time.time())

k = 0
for i in range(0, len(biner), 6):
    if k == 64:
        break
    #print(codebook[biner[i:i+6]])
    '''print(codebook[biner[i:i+6]])
    winsound.Beep(10000, 250)
    if k % 10 == 0 and k != 0 :
        time.sleep(0.50)
        print("---sync---")
    else:
    '''
    #if k % 10 == 0 and k is not 0:
        #winsound.Beep(11000, 250)
    playBit(biner[i:i+6])

    k += 1

#print(time.time())
