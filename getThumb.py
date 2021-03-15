
# Process and export thumbnails from PPM and KWZ files

from os.path import isfile
from PIL import Image

from objects import *

global VERBOSE_OUT
VERBOSE_OUT = False
# Indexed palette used for PPM thumbnails.
PPM_THUMB_PALETTE = [
    (0xFF, 0xFF, 0xFF),
    (0x52, 0x52, 0x52),
    (0xFF, 0xFF, 0xFF),
    (0x9C, 0x9C, 0x9C),
    (0xFF, 0x48, 0x44),
    (0xC8, 0x51, 0x4F),
    (0xFF, 0xAD, 0xAC),
    (0x00, 0xFF, 0x00),
    (0x48, 0x40, 0xFF),
    (0x51, 0x4F, 0xB8),
    (0xAD, 0xAB, 0xFF),
    (0x00, 0xFF, 0x00),
    (0xB6, 0x57, 0xB7),
    (0x00, 0xFF, 0x00),
    (0x00, 0xFF, 0x00),
    (0x00, 0xFF, 0x00)
]

# Get the JPEG thumbnail from a specified KWZ file and copy it to a specified JPG file
def getThumbKwz(pathIn, pathOut):
    if (isfile(pathIn)):
        if (VERBOSE_OUT):
            print("Opening input and output files for KWZ thumbnail export. Input: " + pathIn + "\nOutput: " + pathOut)
        inputKwz = open(pathIn, 'rb')
        outputJpg = open(pathOut, 'wb')
        # Find beginning of KTN (thumbnail) section
        if (VERBOSE_OUT):
            print("Locating KTN header...")
        inputKwz.read(4)            # Skip past the "KFH" in the KFH header
        kfhSizeBytes = []
        for i in range(4):
            kfhSizeBytes += inputKwz.read(1)
        kfhSize = (kfhSizeBytes[0] + (kfhSizeBytes[1] << 8) + (kfhSizeBytes[2] << 16) + (kfhSizeBytes[3] << 24))
        inputKwz.read(kfhSize + 4)  # Skip past the entire KFH and the "KTN" in the KTN header
        ktnSizeBytes = []
        for i in range(4):
            ktnSizeBytes += inputKwz.read(1)
        ktnSize = (ktnSizeBytes[0] + (ktnSizeBytes[1] << 8) + (ktnSizeBytes[2] << 16) + (ktnSizeBytes[3] << 24))
        # JPEG image data does not seem to start immediately after the 8-byte KTN header. The commented out code
        # below was supposed to locate the actual beginning of the JPEG data, but it doesn't work. Just skipping
        # the first four bytes after the KTN header seems to resolve the issue though
        #startAt = 0
        #for i in range(ktnSize):
        #    currentByte = inputKwz.read(1)
        #    if (currentByte == 0xFF):
        #        currentByte = inputKwz.read(1)
        #        if (currentByte == 0xD8):
        #            notFoundStart = True
        #        startAt += 2
        #    else:
        #        startAt += 1
        # Write the JPEG data to the specified jpg file
        if (VERBOSE_OUT):
            print("Copying JPEG information from KTN to output JPG...")
        inputKwz.read(4)    # I'm not sure what the 4 bytes after the KTN header are for, but they didn't seem to be part of the JPEG image
        outputJpg.write(inputKwz.read(ktnSize - 4))
        inputKwz.close()
        outputJpg.close()

    else:
        raise Exception("Error: Specified input path is not a file.\nGiven path: " + pathIn)

# Gets the thumbnail bytes from a specified PPM file and processes it so it can be exported to a JPG file
def getThumbPpm(pathIn, pathOut):
    if (isfile(pathIn)):
        if (VERBOSE_OUT):
            print("Opening input file for PPM thumbnail export. Input: " + pathIn)
        inputPpm = open(pathIn, 'rb')
        outputImage = Image.new(mode = "RGB", size = (64, 48), color = (0xFF, 0xFF, 0xFF))
        inputPpm.read(0xA0)     # Skip the PPM's header
        ppmThumbBytes = []
        for i in range(1536):
            ppmThumbBytes += inputPpm.read(1)
        
        # Processes the thumbnail data from the PPM. This part is adapted from the pseudocode
        # in the Flipnote Collective's documentation on Flipnote Studio's PPM format
        # Link: https://github.com/Flipnote-Collective/flipnote-studio-docs/wiki/PPM-format#thumbnail-images
        if (VERBOSE_OUT):
            print("Processing thumbnail bytes...")
        data_offset = 0
        for tile_y in range(0, 48, 8):
            for tile_x in range(0, 64, 8):
                for line in range(0, 8):
                    for pixel in range(0, 8, 2):
                        x = tile_x + pixel
                        y = tile_y + line
                        outputImage.putpixel((x, y), PPM_THUMB_PALETTE[ppmThumbBytes[data_offset] & 0x0F])
                        outputImage.putpixel((x + 1, y), PPM_THUMB_PALETTE[(ppmThumbBytes[data_offset] >> 4) & 0x0F])
                        data_offset += 1
        
        # Exports the image to a JPEG
        if (VERBOSE_OUT):
            print("Opening output file and exporting as JPG. Output: " + pathOut)
        outputImage.save(pathOut, "JPEG")

    else:
        raise Exception("Error: Specified input path is not a file.\nGiven path: " + pathIn)