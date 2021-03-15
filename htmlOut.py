
import os
from shutil import copyfile
import datetime

from objects import *
import getThumb

global VERBOSE_OUT
VERBOSE_OUT = False
# Stores the version of this script
FNID_VERSION = "0.4.0"
# Name of the directory that HTML exports will be placed in
HTML_OUTPUT_DIR_NAME = "flipnoteid_out"

# Returns the directory that this script file is located in and running from
def getScriptDir():
    locOfScript = os.path.realpath(__file__)
    bottomDirSlashAt = 0
    for i in range(len(locOfScript) - 1, 0, -1):
        if (locOfScript[i] == "/" or locOfScript[i] == "\\"):
            bottomDirSlashAt = i
            break
    return locOfScript[0:bottomDirSlashAt + 1]

# Looks to see if it can find Sudofont
def detectSudofontTtf():
    return os.path.isfile(getScriptDir() + "sudofont.ttf")

# Takes the collected informations and outputs it to HTML files
def htmlExport(usersList, flipnotesList, location, template, scannedPath, addThumbnails, addSudo):
    if os.access(location, os.W_OK):
        try:
            if (VERBOSE_OUT):
                print("Creating HTML export directory: " + location + HTML_OUTPUT_DIR_NAME)
                getThumb.VERBOSE_OUT = True
            os.mkdir(location + HTML_OUTPUT_DIR_NAME)
        except:
            pass
        scriptDir = getScriptDir()
        if (VERBOSE_OUT):
            print("Copying HTML hats from template: " + template)
        copyfile(scriptDir + "web_template/" + template + "/index_h.html", location + HTML_OUTPUT_DIR_NAME + "/index.html")
        copyfile(scriptDir + "web_template/" + template + "/authors_h.html", location + HTML_OUTPUT_DIR_NAME + "/authors.html")
        copyfile(scriptDir + "web_template/" + template + "/flipnotes_h.html", location + HTML_OUTPUT_DIR_NAME + "/flipnotes.html")
        if (addThumbnails):
            os.mkdir(location + HTML_OUTPUT_DIR_NAME + "/thumb")
        if (not addSudo):
            print("-ns option passed. Sudofont will not be copied over")       
        elif (detectSudofontTtf()):
            print("sudofont.ttf detected in script directory. Copying to HTML export directory.")
            copyfile(scriptDir + "sudofont.ttf", location + HTML_OUTPUT_DIR_NAME + "/sudofont.ttf")
        else:
            print("sudofont.ttf not detected in script directory.")

        htmlExportAuthors(usersList, location)
        htmlExportFlipnotes(flipnotesList, location, scannedPath, addThumbnails)
        htmlExportMain(usersList, flipnotesList, location, scannedPath)

        if (VERBOSE_OUT):
            print("Appending HTML boots from template: " + template)
        # Add the footer to the end of the generated main page
        foot = open(scriptDir + "web_template/" + template + "/index_b.html", 'r')
        generated = open(location + HTML_OUTPUT_DIR_NAME + "/index.html", 'a')
        generated.write(foot.read())
        foot.close()
        generated.close()

        # Add the footer to the end of the generated authors page
        foot = open(scriptDir + "web_template/" + template + "/authors_b.html", 'r')
        generated = open(location + HTML_OUTPUT_DIR_NAME + "/authors.html", 'a')
        generated.write(foot.read())
        foot.close()
        generated.close()

        # Add the footer to the end of the generated main page
        foot = open(scriptDir + "web_template/" + template + "/flipnotes_b.html", 'r')
        generated = open(location + HTML_OUTPUT_DIR_NAME + "/flipnotes.html", 'a')
        generated.write(foot.read())
        foot.close()
        generated.close()

    else:
        raise Exception("Error: Cannot write to specified directory.")

# Used by htmlExport to handle the core content that goes into the authors page
def htmlExportAuthors(usersList, location):
    if (VERBOSE_OUT):
        print("Exporting author information to file: " + location + HTML_OUTPUT_DIR_NAME + "/authors.html")
    authorPage = open(location + HTML_OUTPUT_DIR_NAME + "/authors.html", 'a')
    if (VERBOSE_OUT):
        print("Generating Table of Contents...")
    tableContents =  "<h1>List of Authors Found</h1>\n"
    tableContents += "<table><tr><td>Studio ID</td><td>Most Common Name/s</td></tr>\n"
    for i in range(len(usersList)):
        tableContents += "<tr><td><a href=\"./authors.html#" + usersList[i].getId() + "\">" + usersList[i].getId() + "</a></td><td>" + usersList[i].getCommonNamesString("/") + "</td></tr>\n"
    authorPage.write(tableContents + "</table><br>\n")

    for i in range(len(usersList)):
        if (VERBOSE_OUT):
            print("Exporting author (Studio ID): " + usersList[i].getId())
        addAuthor = "<a id=\"" + usersList[i].getId() + "\">\n"
        addAuthor += "<h1>User ID: " + usersList[i].getId() + " (" + usersList[i].getCommonNamesString("/") + ")</h1>\n"
        addAuthor += "<p>Total number of Flipnotes: " + str(usersList[i].getTotalFlipnotes()) + "</p>\n"
        addAuthor += "<h5>Names</h5>\n<table>\n<tr><td>Number of<br>Times Found</td><td>Name</td></tr>\n"
        for j in range(usersList[i].getTotalNames()):
            addAuthor += "<tr><td>" + str(usersList[i].getNameUsage(j)) + "</td><td>" + usersList[i].getName(j) + "</td></tr>\n"
        addAuthor += "</table>\n<h5>Flipnotes</h5>\n<table>\n<tr><td>Filename on Disk</td></tr>\n"
        for j in range(usersList[i].getTotalFlipnotes()):
            diskNameOnly = (usersList[i].getFlipnote(j)).split("/")
            addAuthor += "<tr><td><a href=\"flipnotes.html#" + (usersList[i].getFlipnote(j)).replace("/", "-") + "\">" + diskNameOnly[len(diskNameOnly) - 1] + "</a></td></tr>\n"
        addAuthor += "</table>\n<hr>\n"
        authorPage.write(addAuthor)
    authorPage.close()

# Used by htmlExport to handle the core content that goes into the Flipnotes page
def htmlExportFlipnotes(flipnotesList, location, scannedPath, addThumbnails):
    if (VERBOSE_OUT):
        print("Exporting Flipnote information to file: " + location + HTML_OUTPUT_DIR_NAME + "/flipnotes.html")
    flipnotePage = open(location + HTML_OUTPUT_DIR_NAME + "/flipnotes.html", 'a')
    for i in range(len(flipnotesList)):
        currentIsPpm = flipnotesList[i].isPpm()
        if (VERBOSE_OUT):
            print("Exporting Flipnote (relative file path): " + flipnotesList[i].getFilenameOnDisk())
        addFlipnote =  "<a id=\"" + (flipnotesList[i].getFilenameOnDisk()).replace("/", "-") + "\">\n"
        addFlipnote += "<h1>Current Name of Flipnote: " + flipnotesList[i].getFilenameCurrent() + "</h1>\n"
        if (addThumbnails):
            if (VERBOSE_OUT):
                print("Getting thumbnail for Flipnote...")
            makeRequiredThumbDirs(location, flipnotesList[i].getFilenameOnDisk())
            if (currentIsPpm):
                getThumb.getThumbPpm(scannedPath + flipnotesList[i].getFilenameOnDisk(), location + HTML_OUTPUT_DIR_NAME + "/thumb/" + flipnotesList[i].getFilenameOnDisk() + ".jpg")
            else:
                getThumb.getThumbKwz(scannedPath + flipnotesList[i].getFilenameOnDisk(), location + HTML_OUTPUT_DIR_NAME + "/thumb/" + flipnotesList[i].getFilenameOnDisk() + ".jpg")
            addFlipnote += "<img src=\"thumb/" + flipnotesList[i].getFilenameOnDisk() + ".jpg\" alt=\"Thumbnail\" style=\"height:96px;\" />\n"
        addFlipnote += "<p>Date and Time of Last Edit: " + flipnotesList[i].getDateStored() + " at " + flipnotesList[i].getTimeStored() + "</p>\n"
        lockStatus = ""
        if (flipnotesList[i].isLocked()):
            lockStatus = "Locked"
        else:
            lockStatus = "not Locked"
        if (currentIsPpm):
            addFlipnote += "<p>Flipnote is in .PPM format (Flipnote Studio / DSi) and is " + lockStatus + "</p>\n"
        else:
            addFlipnote += "<p>Flipnote is in .KWZ format (Flipnote Studio 3D / 3DS) and is " + lockStatus + "</p>\n"
        addFlipnote += "<p>Filename on Disk (Relative Path): " + flipnotesList[i].getFilenameOnDisk() + "</p>\n"
        if (flipnotesList[i].getIdEditor() != flipnotesList[i].getIdOriginal()):
            addFlipnote += "<p>Editor or Current Author: <a href=\"./authors.html#" + flipnotesList[i].getIdEditor() + "\">" + flipnotesList[i].getIdEditor() + "</a> (" + flipnotesList[i].getNameEditor() + ")</p>\n"
            addFlipnote += "<p>Original Filename: " + flipnotesList[i].getFilenameOriginal() + "</p>\n"
        addFlipnote += "<p>Original Author: <a href=\"./authors.html#" + flipnotesList[i].getIdOriginal() + "\">" + flipnotesList[i].getIdOriginal() + "</a> (" + flipnotesList[i].getNameOriginal() + ")</p>\n<hr>"
        flipnotePage.write(addFlipnote)
    flipnotePage.close()

# Used by htmlExport to handle the core content that goes into the main page
def htmlExportMain(usersList, flipnotesList, location, scannedPath):
    if (VERBOSE_OUT):
        print("Exporting main page information to file: " + location + HTML_OUTPUT_DIR_NAME + "/index.html")
    mainPage = open(location + HTML_OUTPUT_DIR_NAME + "/index.html", 'a')

    addToMain =  "<h3>This search found " + str(len(flipnotesList)) + " Flipnotes and " + str(len(usersList)) + " Studio IDs</h3>\n"
    addToMain += "<p>The search was completed on " + datetime.datetime.now().strftime("%Y/%m/%d at %H:%M:%S") + " With FlipnoteID version " + FNID_VERSION + ". The directory scanned was " + scannedPath + "</p><br>\n"
    # User with most Flipnotes
    frequent = findFrequentAuthor(usersList)
    addToMain += "<h3>User " + frequent.getId() + " has the most Flipnotes here.</h3>\n"
    addToMain += "<p>With " + str(frequent.getTotalFlipnotes()) + " Flipnotes, Studio ID <a href=\"" + frequent.getId() + "\">" + frequent.getId() + "</a> (" + frequent.getName(0)
    for i in range(1, frequent.getTotalNames()):
        addToMain += ", " + frequent.getName(i)
    addToMain += ") has the most Flipnotes in the searched collection.</p><br>\n"
    # Oldest and newest Flipnotes
    oldAndNew = findOldestAndNewestFlipnotes(flipnotesList, scannedPath)
    addToMain += "<h3>From " + (oldAndNew[0].getDateStored())[0:4] + " to " + (oldAndNew[1].getDateStored())[0:4] + "</h3>\n"
    addToMain += "<p>The oldest Flipnote found was <a href=\"./flipnotes.html#" + (oldAndNew[0].getFilenameOnDisk()).replace("/", "-") + "\">" + oldAndNew[0].getFilenameCurrent() + "</a> from " + oldAndNew[0].getDateStored()
    addToMain += ", while the newest was <a href=\"./flipnotes.html#" + (oldAndNew[1].getFilenameOnDisk()).replace("/", "-") + "\">" + oldAndNew[1].getFilenameCurrent() + "</a> from " + oldAndNew[1].getDateStored() + ".</p><br>\n"
    
    mainPage.write(addToMain)
    mainPage.close()

# Finds the author with the most flipnotes found in the search and returns the StudioUser
def findFrequentAuthor(usersList):
    if (len(usersList) <= 1):
        return usersList
    else:
        frequent = usersList[0]
        for i in range(1, len(usersList)):
            if (usersList[i].getTotalFlipnotes() > frequent.getTotalFlipnotes()):
                frequent = usersList[i]
        return frequent

# Finds the oldest and the newest flipnotes that were found and returns them in a list
def findOldestAndNewestFlipnotes(flipnotesList, scannedPath):
    if (len(flipnotesList) <= 2):
        return flipnotesList
    else:
        oldAndNew = [flipnotesList[0], flipnotesList[1]]
        unixTimeOld = grabUnixTimeFromFlipnote(flipnotesList[0], scannedPath)
        unixTimeNew = grabUnixTimeFromFlipnote(flipnotesList[1], scannedPath)
        # If it put the older of the two Flipnotes in the wrong spot, switch them around
        if (unixTimeOld > unixTimeNew):
            oldAndNew = [flipnotesList[1], flipnotesList[0]]
            temp = unixTimeNew
            unixTimeNew = unixTimeOld
            unixTimeOld = temp

        for i in range(2, len(flipnotesList)):
            unixTimeI = grabUnixTimeFromFlipnote(flipnotesList[i], scannedPath)
            # Ignore maximum values and dates in the year 2000, as neither are realistically
            # possible and are far more likely to be the result of erroneous metadata
            if (unixTimeI == 0xFFFFFFFF or unixTimeI < 31557600):
                pass
            elif (unixTimeOld > unixTimeI):
                unixTimeOld = unixTimeI
                oldAndNew[0] = flipnotesList[i]
            elif (unixTimeI > unixTimeNew):
                unixTimeNew = unixTimeI
                oldAndNew[1] = flipnotesList[i]
        return oldAndNew

# Takes the filename stored for a flipnote, reopens it, and gets the UNIX-style date/time value from it
def grabUnixTimeFromFlipnote(flipnote, scannedPath):
    flipnoteFile = open(scannedPath + flipnote.getFilenameOnDisk(), 'rb')
    timeBytes = []
    # 0x9A - 0x9D
    if (flipnote.isPpm()):
        flipnoteFile.read(0x9A)     # Ignore the bytes leading up to the date/time bytes
    # 0xC - 0xF
    else:
        flipnoteFile.read(0xC)      # Ignore the bytes leading up to the date/time bytes

    for i in range(0, 4):
        timeBytes += flipnoteFile.read(1)
    return (timeBytes[0] + (timeBytes[1] << 8) + (timeBytes[2] << 16) + (timeBytes[3] << 24))

# Makes any required subdirectories
def makeRequiredThumbDirs(location, filenameOnDisk):
    subdirs = filenameOnDisk.split("/")
    for i in range(len(subdirs) - 1):
        dirToMake = location + HTML_OUTPUT_DIR_NAME + "/thumb"
        for j in range(i + 1):
            dirToMake += "/" + subdirs[j]
        if (not os.path.isdir(dirToMake)):
            os.mkdir(dirToMake)
