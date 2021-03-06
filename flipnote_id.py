
import os
import sys

import objects
import procHeaders
import htmlOut

# Stores the version of this script
FNID_VERSION = "0.3.0"
# Name of the directory that HTML exports will be placed in
HTML_OUTPUT_DIR_NAME = "flipnoteid_out"

# Function for taking a filepath, opening the file, and trying to get header info from it
# TODO: Make it try to ID files with no extension
def importFile(filePath):
    if (filePath[(len(filePath) - 3):len(filePath)].lower() == "ppm"):
        try:
            if (GVAR_VERBOSE):
                print("Processing file as PPM: " + filePath)
            inFile = open(filePath, 'rb')
            headerInfo = []
            stillGoing = True
            bytesRead = 0
            while (stillGoing):
                headerInfo += inFile.read(1)
                bytesRead += 1
                if (bytesRead >= 0x9F):
                    stillGoing = False
            
            inFile.close()
            return headerInfo
        except:
            pass
    elif (filePath[(len(filePath) - 3):len(filePath)].lower() == "kwz"):
        try:
            if (GVAR_VERBOSE):
                print("Processing file as KWZ: " + filePath)
            inFile = open(filePath, 'rb')
            headerInfo = []
            stillGoing = True
            bytesRead = 0
            while (stillGoing):
                headerInfo += inFile.read(1)
                bytesRead += 1
                if (bytesRead >= 0xD3):
                    stillGoing = False
            
            inFile.close()
            return headerInfo
        except:
            pass
    else:
        raise Exception("Error: File does not end with extension ppm or kwz")

# Goes through the files in a directory to import them. Travels recursively if told to do so
def importFilesFromDir(dirPath, recursive, relativePath):
    headerList = []
    headerList.append([])   # Two of the same command so it becomes a 2D list
    headerList.append([])
    dirList = os.listdir(dirPath)

    for i in range(len(dirList)):
        if os.path.isfile(dirPath + dirList[i]):
            try:
                getBytes = importFile(dirPath + dirList[i])
                if (GVAR_VERBOSE):
                    print("Appending info to lists.")
                headerList[0].append(getBytes)
                headerList[1].append(relativePath + dirList[i])
            except:
                pass

        elif (recursive and os.path.isdir(dirPath + dirList[i])):
            if (GVAR_VERBOSE):
                print("Recursively searching in: " + relativePath + dirList[i] + "/")
            nextdir = importFilesFromDir(dirPath + dirList[i] + "/", recursive, relativePath + dirList[i] + "/")
            if (GVAR_VERBOSE):
                print("Search in " + relativePath + dirList[i] + "/ complete. Merging info into parent lists")
            for j in range(len(nextdir[0])):
                headerList[0].append(nextdir[0][j])
                headerList[1].append(nextdir[1][j])
    return headerList

# MAIN FUNCTION
def main():
    if (len(sys.argv) < 2):
        print("Error: Expected at least one additional argument\n  Usage: python3 flipnote_id.py [IN_PATH] [OPTIONS]\nFor additional usage info, read the included documentation or run\n  python3 flipnote_id.py -h")
    elif (len(sys.argv) == 2 and sys.argv[1] == "-h"):
        printHelp()
    else:
        locationIn = sys.argv[1]
        users = []
        notes = []
        global GVAR_VERBOSE
        if (os.path.isdir(locationIn)):
            # Defaults
            locationOut = sys.argv[1]
            template = "plain"
            recursive = True
            ignorePpm = False
            ignoreKwz = False
            consoleOut = False
            validArgs = True
            GVAR_VERBOSE = False
            # If the last character is not a forward slash, append one to the end
            if (locationIn[len(locationIn) - 1] != "/"):
                locationIn += "/"
            # Process and handle args
            for i in range(2, len(sys.argv)):
                if (sys.argv[i] == "-c"):
                    consoleOut = True
                elif (sys.argv[i] == "-ik"):
                    ignoreKwz = True
                elif (sys.argv[i] == "-ip"):
                    ignorePpm = True
                elif (sys.argv[i] == "-nr"):
                    recursive = False
                elif (sys.argv[i] == "-v"):
                    GVAR_VERBOSE = True
                    setVerboseAll()
                elif (len(sys.argv[i]) > 3 and (sys.argv[i])[0:3] == "-o="):
                    locationOut = (sys.argv[i])[3:len(sys.argv[i])]
                    if (not os.path.isdir(locationOut)):
                        validArgs = False
                        print("Error: Specified output directory does not exist.\nGiven directory: " + locationOut)
                    elif (not os.access(locationOut, os.W_OK)):
                        validArgs = False
                        print("Error: Cannot write to specified output directory.\nGiven directory: " + locationOut)
                    elif (locationOut[len(locationOut) - 1] != "/"):
                        locationOut += "/"
                elif (len(sys.argv[i]) > 3 and (sys.argv[i])[0:3] == "-t="):
                    template = (sys.argv[i]).replace("/", "")
                    if (not os.path.isdir(getScriptDir() + "web_template/" + template)):
                        validArgs = False
                        print("Error: Specified template does not appear to exist. Check the web_templates\ndirectory for options.\nGiven template: " + template)
                else:
                    validArgs = False
                    print("Error: Unrecognized argument: " + sys.argv[i])
            # Once args have been processed, go through the files if all args were valid
            if (validArgs):
                print("Obtaining header info from files in specified input directory...")
                getHeaders = importFilesFromDir(locationIn, recursive, "")
                print("Processing header info...")
                for i in range(len(getHeaders[0])):
                    if ((not ignorePpm) and getHeaders[0][i][0] == 0x50):
                        procHeaders.procHeaderPpm(getHeaders[0][i], getHeaders[1][i], users, notes)
                    elif ((not ignoreKwz) and getHeaders[0][i][0] == 0x4B):
                        procHeaders.procHeaderKwz(getHeaders[0][i], getHeaders[1][i], users, notes)
                if (consoleOut):
                    outputToConsole(users, notes)
                else:
                    print("Exporting to HTML files at " + locationOut + HTML_OUTPUT_DIR_NAME)
                    htmlOut.htmlExport(users, notes, locationOut, template, locationIn)
                    print("HTML export finished.")

        # Handling for the IN_PATH being a file
        else:
            GVAR_VERBOSE = True
            setVerboseAll()
            if (os.path.isfile(locationIn)):
                checkExtFile = open(locationIn, 'rb')
                checkExt = []
                for i in range(0, 4):
                    checkExt += checkExtFile.read(1)
                checkExtFile.close()
                if (checkExt[0] == 0x50 and checkExt[1] == 0x41 and checkExt[2] == 0x52 and checkExt[3] == 0x41):
                    getHeader = importFile(locationIn)
                    processed = procHeaders.procHeaderPpm(getHeader, locationIn, users, notes)
                    outputToConsole(users, notes)
                elif (checkExt[0] == 0x4B and checkExt[1] == 0x46 and checkExt[2] == 0x48):
                    getHeader = importFile(locationIn)
                    processed = procHeaders.procHeaderKwz(getHeader, locationIn, users, notes)
                    outputToConsole(users, notes)
                else:
                    print("Error: Specified file does not appear to be a PPM or KWZ file.")
            else:
                print("Error: Specified input path does not appear to be an existing file or directory.\nGiven path: " + locationIn)

# When the script is run with the -h option, this function is run to print the detailed usage info
def printHelp():
    print("  Usage: python3 flipnote_id.py [IN_PATH] [OPTIONS]\n")
    print("If the given IN_PATH points to a file, the information about it will\nbe printed to the console. If it points to a directory, it will be collected\nand exported to HTML files. Most of the below options only apply to\noutputs of directory scans.\n")
    print("OPTIONS")
    print("  -h     Print usage information.")
    print("  -c     Print to console instead of exporting to HTML.\n         Does not apply when the specified path is a single file.")
    print("  -ik    Ignore KWZ files when searching through directories.")
    print("  -ip    Ignore PPM files when searching through directories.")
    print("  -nr    This program defaults to recursively searching through any found\n         subdirectories. Pass this option to prevent recursive searching.")
    print("  -v     Give verbose output.")
    print("\n  -t=[TEMPLATE]    Specify a template to be used when exporting to HTML.\n                   Default is \"plain\"")
    print("\n  -o=[OUT_PATH]    Specify the directory to send an HTML export to.\n                   Default is the specified input path.")

# Handles the console output of information in the authors and flipnotes lists
def outputToConsole(usersList, flipnotesList):
    print("=== Authors ===")
    for i in range(len(usersList)):
        print("Info for ID    : " + usersList[i].getId())
        print("Total Flipnotes: " + str(usersList[i].getTotalFlipnotes()))
        print("Total Names    : " + str(usersList[i].getTotalNames()))
        print("Names: ")
        for j in range(usersList[i].getTotalNames()):
            print("  " + usersList[i].getName(j))
        print("\n")
    
    print("\n=== Flipnotes ===")
    for i in range(len(flipnotesList)):
        print("Current Filename  : " + flipnotesList[i].getFilenameCurrent())
        # If this is the original version of the Flipnote, don't print the same information twice
        if (flipnotesList[i].getIdEditor() == flipnotesList[i].getIdOriginal()):
            print("Editor ID         : " + flipnotesList[i].getIdEditor())
            print("Original Filename : " + flipnotesList[i].getFilenameOriginal())
        print("Original Author ID: " + flipnotesList[i].getIdOriginal())
        print("Is a PPM          : " + str(flipnotesList[i].isPpm()))
        print("Is Locked         : " + str(flipnotesList[i].isLocked()))
        print("Date              : " + flipnotesList[i].getDateStored())
        print("Time              : " + flipnotesList[i].getTimeStored() + "\n")

# Ensure verbose output is given when specified
def setVerboseAll():
    procHeaders.VERBOSE_OUT = True
    htmlOut.VERBOSE_OUT = True

# RUN THE MAIN FUNCTION
main()