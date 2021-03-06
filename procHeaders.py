
from math import ceil

from objects import *

global VERBOSE_OUT
VERBOSE_OUT = False

# Converts a series of bytes from a list into a String by interpreting them as ASCII values
def asciiBytesToString(headerBytes, byteStart, byteEnd):
    string = ""
    for i in range(byteStart, byteEnd):
        string += chr(headerBytes[i])
    return string

# Converts a series of little-endian words (byte pairs) into a String by interpreting them as UCS-2/UTF-16 values
def ucs2WordsLittleToString(headerBytes, byteStart, byteEnd):
    string = ""
    for i in range(byteStart, byteEnd, 2):
        getWord = headerBytes[i] + (headerBytes[i + 1] << 8)
        if getWord > 0:
            string += chr(getWord)
    return string

# Converts a little-endian series of bytes into a String of corresponding hex values 
def hexBytesLittleToString(headerBytes, byteStart, byteEnd):
    string = ""
    for i in range(byteStart, byteEnd):
        #if len(hex(headerBytes[i])) == 1:
        if (headerBytes[i] < 0x10):
            string = "0" + (hex(headerBytes[i])[2:len(str(headerBytes[i])) + 2]).upper() + string
        else:
            string = (hex(headerBytes[i])[2:len(str(headerBytes[i])) + 2]).upper() + string
    return string

# The code for calc_check_digit has been copied (and very slightly modified) from this source:
# https://github.com/Flipnote-Collective/flipnote-studio-docs/wiki/FSIDs-and-Filenames
# filename should be the current filename as a string e.g 'F78DA8_14768882B56B8_030'
def calc_check_digit(filename):
    checksumDict = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # sum starts out as the first byte of the current filename as stored in the PPM metadata 
    sumc = int(filename[0:2], 16)
    for i in range(1, 16):
        char = ord(filename[i])
        # sumc should stay within the uint8 range
        sumc = (sumc + char) % 256 
    return checksumDict[sumc % len(checksumDict)]

# Function for processing metadata from the header of a PPM file (Flipnote Studio / DSi)
def procHeaderPpm(headerBytes, filenameDisk, usersList, flipnotesList):
    # Check to see that we got enough values for this to be the header and detect if
    # the magic number is in the first four bytes (Hex: [50,41,52,41] == ASCII: PARA)
    if (len(headerBytes) >= 0x9F and headerBytes[0] == 0x50 and headerBytes[1] == 0x41 and headerBytes[2] == 0x52 and headerBytes[3] == 0x41):
        if (VERBOSE_OUT):
            print("Processing header info as PPM for file (relative path): " + filenameDisk)
        nameOriginal = ucs2WordsLittleToString(headerBytes, 0x14, 0x2A)
        nameCurrent = ucs2WordsLittleToString(headerBytes, 0x40, 0x56)
        idOriginal = hexBytesLittleToString(headerBytes, 0x56, 0x5E)
        idEditor = hexBytesLittleToString(headerBytes, 0x5E, 0x66)
        filenameOriginal = hexBytesLittleToString(headerBytes, 0x66, 0x69) + "_" + asciiBytesToString(headerBytes, 0x69, 0x76) + "_" + str(headerBytes[0x76] + (headerBytes[0x77] << 8)).rjust(3, '0')
        filenameCurrent = hexBytesLittleToString(headerBytes, 0x78, 0x7B) + "_" + asciiBytesToString(headerBytes, 0x7B, 0x88) + "_" + str(headerBytes[0x88] + (headerBytes[0x89] << 8)).rjust(3, '0')

        filenameOriginal = calc_check_digit(filenameOriginal) + filenameOriginal[1:len(filenameOriginal)]
        filenameCurrent = calc_check_digit(filenameCurrent) + filenameCurrent[1:len(filenameCurrent)]

        isLocked = (headerBytes[0x10] == 1)
        processedTime = []
        try:
            processedTime = secondsToDateAndTime( headerBytes[0x9A] + (headerBytes[0x9B] << 8) + (headerBytes[0x9C] << 16) + (headerBytes[0x9D] << 24) )
        except Exception as e:
            e.message = "Could not process given time from header bytes.\n" + e.message
            raise

        # Add this Flipnote's name on the disk to the user entries of the original author and the editor
        foundUserOriginal = False
        foundUserEditor = False
        if (idOriginal == idEditor):
            foundUserEditor = True
        for i in range(len(usersList)):
            if ((not foundUserOriginal) and idOriginal == usersList[i].getId()):
                if (VERBOSE_OUT):
                    print("Updating information for user (Studio ID): " + usersList[i].getId())
                usersList[i].addFlipnote(filenameDisk)
                usersList[i].addName(nameOriginal)
                foundUserOriginal = True
            elif ((not foundUserEditor) and idEditor == usersList[i].getId()):
                if (VERBOSE_OUT):
                    print("Updating information for user (Studio ID): " + usersList[i].getId())
                usersList[i].addFlipnote(filenameDisk)
                usersList[i].addName(nameCurrent)
                foundUserEditor = True
            if (foundUserOriginal and foundUserEditor):
                break

        # If user entries weren't found for one or both of the users in question, add them to the list
        if (not foundUserOriginal):
            if (VERBOSE_OUT):
                    print("User not found in list. Creating user for (Studio ID): " + idOriginal)
            i = len(usersList)
            usersList.append(StudioUser(idOriginal))
            usersList[i].addFlipnote(filenameDisk)
            usersList[i].addName(nameOriginal)
        if (not foundUserEditor):
            if (VERBOSE_OUT):
                    print("User not found in list. Creating user for (Studio ID): " + idEditor)
            i = len(usersList)
            usersList.append(StudioUser(idEditor))
            usersList[i].addFlipnote(filenameDisk)
            usersList[i].addName(nameCurrent)
        
        # Add this Flipnote to the list of Flipnotes
        if (VERBOSE_OUT):
            print("Adding Flipnote to list.")
        flipnotesList.append(FlipnoteData(filenameDisk, filenameOriginal, filenameCurrent, idOriginal, idEditor, nameOriginal, nameCurrent, processedTime[0], processedTime[1], True, isLocked))

    else:
        if (len(headerBytes) < 0x9F):
            raise Exception("Error: Expected at least 0x9F bytes for PPM header.\nGiven number of bytes: " + len(headerBytes))
        elif (headerBytes[0] == 0x4B and headerBytes[1] == 0x46 and headerBytes[2] == 0x48):
            raise Exception("Error: Detected ASCII sequence \"KFH\" at the beginning of the received header info.\nHeader is not that of a PPM file, but is likely that of a KWZ file.")
        else:
            raise Exception("Error: Did not detect ASCII sequence \"PARA\" at the beginning of the header file.")

# Function for processing metadata from the header of a KWZ file (Flipnote Studio 3D / 3DS)
def procHeaderKwz(headerBytes, filenameDisk, usersList, flipnotesList):
    if (len(headerBytes) >= 0xD3 and headerBytes[0] == 0x4B and headerBytes[1] == 0x46 and headerBytes[2] == 0x48):
        if (VERBOSE_OUT):
            print("Processing header info as KWZ for file (relative path): " + filenameDisk)
        nameOriginal = ucs2WordsLittleToString(headerBytes, 0x36, 0x4C)
        nameCurrent = ucs2WordsLittleToString(headerBytes, 0x62, 0x78)
        idOriginal = hexBytesLittleToString(headerBytes, 0x18, 0x22)
        idEditor = hexBytesLittleToString(headerBytes, 0x2C, 0x36)
        filenameOriginal = asciiBytesToString(headerBytes, 0x78, 0x94)
        filenameCurrent = asciiBytesToString(headerBytes, 0xB0, 0xCC)
        isLocked = (headerBytes[0xD0] & 0x01) == 0x01
        
        processedTime = []
        try:
            processedTime = secondsToDateAndTime( headerBytes[0xC] + (headerBytes[0xD] << 8) + (headerBytes[0xE] << 16) + (headerBytes[0xF] << 24) )
        except Exception as e:
            e.message = "Could not process given time from header bytes.\n" + e.message
            raise

        # Add this Flipnote's name on the disk to the user entries of the original author and the editor
        foundUserOriginal = False
        foundUserEditor = False
        if (idOriginal == idEditor):
            foundUserEditor = True
        for i in range(len(usersList)):
            if ((not foundUserOriginal) and idOriginal == usersList[i].getId()):
                if (VERBOSE_OUT):
                    print("Updating information for user (Studio ID): " + usersList[i].getId())
                usersList[i].addFlipnote(filenameDisk)
                usersList[i].addName(nameOriginal)
                foundUserOriginal = True
            elif ((not foundUserEditor) and idEditor == usersList[i].getId()):
                if (VERBOSE_OUT):
                    print("Updating information for user (Studio ID): " + usersList[i].getId())
                usersList[i].addFlipnote(filenameDisk)
                usersList[i].addName(nameCurrent)
                foundUserEditor = True
            if (foundUserOriginal and foundUserEditor):
                break

        # If user entries weren't found for one or both of the users in question, add them to the list
        if (not foundUserOriginal):
            if (VERBOSE_OUT):
                    print("User not found in list. Creating user for (Studio ID): " + idOriginal)
            i = len(usersList)
            usersList.append(StudioUser(idOriginal))
            usersList[i].addFlipnote(filenameDisk)
            usersList[i].addName(nameOriginal)
        if (not foundUserEditor):
            if (VERBOSE_OUT):
                    print("User not found in list. Creating user for (Studio ID): " + idEditor)
            i = len(usersList)
            usersList.append(StudioUser(idEditor))
            usersList[i].addFlipnote(filenameDisk)
            usersList[i].addName(nameCurrent)
        
        # Add this Flipnote to the list of Flipnotes
        if (VERBOSE_OUT):
            print("Adding Flipnote to list.")
        flipnotesList.append(FlipnoteData(filenameDisk, filenameOriginal, filenameCurrent, idOriginal, idEditor, nameOriginal, nameCurrent, processedTime[0], processedTime[1], False, isLocked))

    else:
        if (len(headerBytes) < 0xD3):
            raise Exception("Error: Expected at least 0xD3 bytes for KWZ header.\nGiven number of bytes: " + len(headerBytes))
        elif (headerBytes[0] == 0x50 and headerBytes[1] == 0x41 and headerBytes[2] == 0x52 and headerBytes[3] == 0x41):
            raise Exception("Error: Detected ASCII sequence \"PARA\" at the beginning of the received header info.\nHeader is not that of a KWZ file, but is likely that of a PPM file.")
        else:
            raise Exception("Error: Did not detect ASCII sequence \"KFH\" at the beginning of the header file.")

# Converts number of seconds since 2000/01/01 @ 00:00 to a date and time, stored as two separate Strings
def secondsToDateAndTime(givenCount):
    if (givenCount < 0):
        raise Exception("Given number of seconds since Midnight of 2000/01/01 is negative.")
    else:
        # 86400 is the number of seconds in a day
        daysInMonth = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        daysInMonthLeap = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

        # Calculate info on the year
        # 31557600 = product of 86400 seconds/day and 365.25 days/year
        yearsSince2000 = int(givenCount / 31557600)
        year = yearsSince2000 + 2000
        leapYearsSince2000 = int((yearsSince2000 - 1) / 4)
        # 2100 is the only year evenly divisible by 4 that is NOT a leap year that a PPM/KWZ can store 
        # Checks to see if the given date is in or before 2100
        if (yearsSince2000 <= 100):
            leapYearsSince2000 += 1
        
        # Calculate what number day it is in the year (Uses math.ceil)
        day = ceil(givenCount / 86400) - (leapYearsSince2000 * 366) - ((yearsSince2000 - leapYearsSince2000) * 365)
        month = 1
        # Figure out what month it is, and adjust the value of the day to match 
        if (year % 4 == 0 and year != 2100):
            while (day > daysInMonthLeap[month]):
                day -= daysInMonthLeap[month]
                month += 1
        else:
            while (day > daysInMonth[month]):
                day -= daysInMonth[month]
                month += 1
        
        # Calculate the hour, minute, and second
        hour = int((givenCount % 86400) / 3600)
        minute = int((int(givenCount % 86400) % 3600) / 60)
        second = int((int(givenCount % 86400) % 3600) % 60)

        # Make and give the return Strings
        dateStr = str(year) + "/" + str(month) + "/" + str(day)
        timeStr = str(hour).rjust(2, '0') + ":" + str(minute).rjust(2, '0') + ":" + str(second).rjust(2, '0')
        return [dateStr, timeStr]
