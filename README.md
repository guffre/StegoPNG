# StegoPNG

Python stegonography tool with builtin encryption/obfuscation of the data.
By default, places 6 bits of data into each pixel of a .png-type file.
It does this by overwriting the 2 least-significant bits in each band (R,G,B).
Only tested with .png files, but will probably work with .bmp files as well.

Features built-in encryption, using Python's `random` library.

## Usage

There is no "main", you will need to import the code into your project.
    
    def steg(image, data_file, output_file)
        
You can call it like: 
    
    steg("C:\\my_picture.png", "E:\\some_document.pdf", "C:\\my_picture_stego.png")
    
`desteg()` works in a similar fashion:

    def desteg(image, savefile)
    
There are two OPTIONAL arguments at the end of each funtion:
    
    def steg(image, data_file, output_file, BITS_TO_SHIFT=2, BANDS_TO_USE=3)
    def desteg(image, savefile, BITS_TO_SHIFT=2, BANDS_TO_USE=3)
    
These determine how many least-significant bits and how many bands (R,G,B) to write data to.
