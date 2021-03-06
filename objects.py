
# Class for storing info about a Flipnote Studio (DSi) User
class StudioUser:
    def __init__(self, studioIdIn):
        self.id = studioIdIn
        self.names = []         # For storing any name variations a user has
        self.namesCount = []    # Stores the number of times a given name occurs
        self.namesCommon = []   # Stores the most frequently occuring name or names
        self.recalcCommon = False
        self.flipnotes = []     # Stores the filenames (on disk) of this user's flipnotes
    
    def getId(self):
        return self.id
    
    def getName(self, index):
        return self.names[index]
    
    def getNameUsage(self, index):
        return self.namesCount[index]
    
    def getTotalNames(self):
        return len(self.names)
    
    def getCommonNames(self):
        if (self.recalcCommon):
            self.recalcCommon = False
            currentHigh = self.namesCount[0]
            self.namesCommon = [self.names[0]]
            for i in range(1, len(self.names)):
                if (self.namesCount[i] == currentHigh):
                    self.namesCommon.append(self.names[i])
                elif (self.namesCount[i] > currentHigh):
                    currentHigh = self.namesCount[i]
                    self.namesCommon = [self.names[i]]
            return self.namesCommon
        else:
            return self.namesCommon
    
    def getCommonNamesString(self, sepSequence):
        if (self.recalcCommon):
            self.getCommonNames()
        namesString = self.namesCommon[0]
        for i in range(1, len(self.namesCommon)):
            namesString += sepSequence + self.namesCommon[i]
        return namesString

    def getTotalFlipnotes(self):
        return len(self.flipnotes)
    
    def getFlipnote(self, index):
        return self.flipnotes[index]

    def addName(self, newName):
        newName = newName.strip()
        self.recalcCommon = True    # Most common name/s will need to be recalculated
        foundName = False
        # Look for the given name in the list of names
        for i in range(len(self.names)):
            if (newName == self.names[i]):
                foundName = True
                self.namesCount[i] += 1  # Add one to the number of times this name occurs
                break
        # If it's not there, add it
        if (not foundName):
            i = len(self.names)
            self.names += [newName]
            self.namesCount += [1]  # Initialize an occurrence value (1) for the newly added name
    
    def clearNames(self):
        self.names = []
    
    def addFlipnote(self, newFlip):
        self.flipnotes += [newFlip]
    
    def clearFlipnotes(self):
        self.flipnotes = []

# Class for storing some relevant info about a Flipnote
class FlipnoteData:
    def __init__(self, filenameDisk, filenameOriginal, filenameCurrent, idOriginal, idEditor, nameOriginal, nameEditor, dateStored, timeStored, isPpm, isLocked):
        self.nameDisk = filenameDisk
        self.nameOrig = filenameOriginal
        self.nameCurr = filenameCurrent
        self.idOrig = idOriginal
        self.idEdit = idEditor
        self.userOrig = nameOriginal
        self.userEdit = nameEditor
        self.date = dateStored
        self.time = timeStored
        self.ppm = isPpm
        self.lock = isLocked
    
    def getFilenameOnDisk(self):
        return self.nameDisk
    
    def getFilenameOriginal(self):
        return self.nameOrig
    
    def getFilenameCurrent(self):
        return self.nameCurr
    
    def getIdOriginal(self):
        return self.idOrig
    
    def getIdEditor(self):
        return self.idEdit
    
    def getNameOriginal(self):
        return self.userOrig
    
    def getNameEditor(self):
        return self.userEdit
    
    def getDateStored(self):
        return self.date
    
    def getTimeStored(self):
        return self.time
    
    def isPpm(self):
        return self.ppm
    
    def isKwz(self):
        return (not self.ppm)
    
    def isLocked(self):
        return self.lock