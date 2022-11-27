from PIL import Image
import os
import random

# Generator to yield all coordinate pairs in a loaded Image
def getpixel(img):
    for y in range(img.height):
        for x in range(img.width):
            yield (x,y)

def steg(image, data_file, output_file, BITS_TO_SHIFT=2, BANDS_TO_USE=3):
    # Minimum of 30 bits gives you minimum of 1-gig of potential data.
    DATA_SIZE = 30
    while ((DATA_SIZE % (BITS_TO_SHIFT*BANDS_TO_USE)) != 0):
        DATA_SIZE += 1
    
    # Open the image and data files
    img = Image.open(image)
    with open(data_file, "rb") as f:
        data = bytearray(f.read())
    
    data_len = len(data)
    
    # Do some basic error checking, like make sure the data can fit in the image
    max_size = (img.height*img.width*BANDS_TO_USE*BITS_TO_SHIFT)-DATA_SIZE
    if BITS_TO_SHIFT > 8:
        print("[!] BITS_TO_SHIFT is > 8. Setting to 8.")
        BITS_TO_SHIFT = 8
    if BANDS_TO_USE > 3:
        print("[!] BANDS_TO_USE is set higher than 3, this might cause incomplete data")
    if data_len >= 2**DATA_SIZE:
        print("[*] Data file exceeds max size capable of being stego'd")
        return 1
    if data_len*8 > max_size:
        print("[*] Data file exceeds destination files capability: {} bytes".format(max_size/8))
        return 1
    
    # Turn the length of binary data into bits
    bin_datalen = str("{0:0" + str(DATA_SIZE) + "b}").format(data_len)[::-1]
    bin_datalen = (int(bit) for bit in bin_datalen)
   
    pixels = getpixel(img)
    # Checkpoint is used to NOT randomize the length, which is the "key" for decryption
    checkpoint = DATA_SIZE / BITS_TO_SHIFT / BANDS_TO_USE

    # Setup random seed. This is used to encrypt the binary data
    random.seed(data_len)
    # Create a bit-generator of all the bits that will be stored in the image
    input_bitarray   = (int(n) for n in ''.join(map("{0:08b}".format, data)))
    # Creat a bitmap and encrypt the data
    encrypt_bitarray = (int(random.choice((0,1))==input_bit) for input_bit in input_bitarray)
    
    for i in range(((data_len*8) + DATA_SIZE) / BITS_TO_SHIFT / BANDS_TO_USE):
        coord = pixels.next()
        pixel = list(img.getpixel(coord))
        if i == checkpoint:
            checkpoint = 0
        for i,byte in enumerate(pixel[:BANDS_TO_USE]):
            for s in range(BITS_TO_SHIFT):
                if checkpoint:
                    bit = bin_datalen.next()
                else:
                    bit = encrypt_bitarray.next()
                if ((byte >> s) & 1) != bit:
                    pixel[i] ^= (1 << s)
        img.putpixel(coord,tuple(pixel))
      
    print("Saving file...")
    while os.path.isfile(output_file):
        c = raw_input("{} exists!\nOverwrite? [y/n] ".format(output_file))
        if c.lower() == "y":
            break
        else:
            output_file = raw_input("Enter new file path:\n> ")
    img.save(output_file)
    print("File saved at: {}".format(output_file))

def desteg(image, savefile, BITS_TO_SHIFT=2, BANDS_TO_USE=3):
    while os.path.isfile(savefile):
        c = raw_input("{} exists!\nOverwrite? [y/n] ".format(savefile))
        if c.lower() == "y":
            break
        else:
            savefile = raw_input("Enter new file path:\n> ")
    DATA_SIZE = 30
    while ((DATA_SIZE % (BITS_TO_SHIFT*BANDS_TO_USE)) != 0):
        DATA_SIZE += 1
    # Open image
    img = Image.open(image)
    pixels = getpixel(img)
    output = []
    # Get length of stego'd data
    for _ in range(DATA_SIZE / BITS_TO_SHIFT / BANDS_TO_USE):
        coord = pixels.next()
        pixel = list(img.getpixel(coord))
        for byte in pixel[:BANDS_TO_USE]:
            for s in range(BITS_TO_SHIFT):
                output.append((byte >> s) & 1)
    
    # Translate backwards binary list into a number
    length = (reduce(lambda x,y: x << 1 | y, output[::-1]))*8
    print("Length: ", length)
    output = []
    # Set the random seed for decrypting the data, and create the bitmask
    random.seed(length/8)
    encrypt_bitmask = (random.choice((0,1)) for _ in range(length))

    # Loop through the file and pull the stego'd bits out
    # This also reverses the encryption: bitmask == pixel_bit is True (1) or False (0)
    # This 1 or 0 is the bit from the stego'd files value
    for _ in range(length / BITS_TO_SHIFT / BANDS_TO_USE):
        coord = pixels.next()
        pixel = list(img.getpixel(coord))
        for byte in pixel[:BANDS_TO_USE]:
            try:
                for s in range(BITS_TO_SHIFT):
                    bit = encrypt_bitmask.next()
                    output.append(int(((byte >> s) & 1) == bit))
            except StopIteration:
                break
 
    # Turn the binary output into bytes in a bytearray
    data = bytearray()
    for i in range(len(output)/8):
        data.append(reduce(lambda x,y: x << 1 | y, output[i*8:i*8+8]))
    
    with open(savefile, "wb") as f:
        f.write(data)
