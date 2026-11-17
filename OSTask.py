#OSTask - Created by Kaia Aydelotte, 09.03.26
#Class designed to handle differences in operating systems
#Last updated 11.10.26

import os           #General operating-system functions
from pathlib import Path
import platform     #Detects current system OS
import pywinctl as pwc
import subprocess   #Launches/interacts with other programs
import time
from tkinter import filedialog
import webbrowser

print("Reached HERE")

class OSTask:
    def __init__(self):
        self.os = platform.system()
        self.file = None                #The libreOffice file.
        self.browser = None             #the Ellipsus link.

    def openFile(self, filename):
        """Function designed to open files"""  
        if self.os == "Windows":
            os.startfile(filename)
        elif self.os == "Linux":
            subprocess.Popen(["libreoffice", filename])
        else:
            raise OSError("Unsupported operating system")

    def fileExplorer(self):
        """Function designed to use and handle the file explorer"""
        if self.os == "Windows":
            filename = filedialog.askopenfilename(       #open file window for user to browse files, copy file path of selected file
                title = "Choose Document  (.odt, .docx)", #...title the file selection window...
                initialdir = Path.home(),                #...open the window to "Home"...
                filetypes = [                            #...and restrict possible filetypes to .odt and .docx
                ("LibreOffice Doc",
                 "*.odt *.docx"),
                ("All files",                        #...Still show all files though (* means "anything before this")
                 "*.*")
            ]
        )
        elif self.os == "Linux":
            result = subprocess.run(
            [
                "zenity",
                "--file-selection",
                "--title=Choose Document (.odt, .docx)",
                f"--filename={Path.home()}/",
                "--file-filter=LibreOffice documents | *.odt *.docx",
                "--file-filter=All files | *"
            ],
            capture_output=True,
            text=True
            )

            if result.returncode == 0:
                filename = result.stdout.strip()
            else:
                filename = ""

        return filename

    def launchLibreOffice(filename, updateStatus, safeSleep):
        """Launches the selected LibreOffice document the first time
           Also saves the path reference."""

        updateStatus("Launching LibreOffice document...") #tell user the file is being launched...
        self.openFile(filename)                           #then launch the right LibreOffice file

        docTitle = Path(filename).stem.lower()            #Now, extract just the document title from the file name, for identification
        timeout = time.monotonic() + 30                   #sets timeout to current time plus thirty seconds

        while time.monotonic() < timeout:                 #While time is less than the timeout deadline...
            matches = [                                       #create a list
                window for window in pwc.getAllWindows()      #examining each window individually, look at all open windows...
                if docTitle in window.title.lower()           #...if the docTitle matches a window, put it on the list
            ]
            if len(matches) == 1:                             #If there is only one match on the list...
                self.file = matches[0]                        #...save that match to the OSTask instance - we'll remember it for later
                return safeSleep(5)                           #...then end function, pausing five seconds for Automaton to catch up
            if len(matches) > 1:                              #If there are multiple matches on the list...
                raise Exception("Multiple documents found.")  #...raise an error and say so

            safeSleep(.25)                                    #Pause the loop a quarter second, so while loop doesn't run into oblivion...
        raise TimeoutError("File window not found.")      #if we got to here... its because LibreOffice didn't respond in the thirty seconds. 


    def launchEllipsus(self, url, docTitle, updateStatus, safeSleep):
        """
        Initializes the specified Ellipsus document in the default browser
        the first time.
        (The user must already be signed into Ellipsus in that browser.)
        """
        updateStatus("Initializing Ellipsus document...") #display message that program is opening Ellipsus doc the first time...
        webbrowser.open(url)                              #...then open Ellipsus doc from the URL

        docTitle = docTitle.lower()                       #This code mimics launchLibreOffice() pretty much exactly, so.... look at that
        timeout = time.monotonic() + 30

        while time.monotonic() < timeout:
            matches = [
                window for window in pwc.getAllWindows()
                if docTitle in window.title.lower()
            ]
            if len(matches) == 1:
                self.browser = matches[0]
                return
            if len(matches) > 1:
                raise Exception("Multiple tabs found.")
            
            safeSleep(.25)
        raise TimeoutError("Window not found.")


    def openLibreoffice(self):
        """Reactivates the correct, open LibreOffice file"""

        if self.libreOfficeWindow is None or not self.libreOfficeWindow.isAlive:  #if there isn't any file reference stored, or 
            raise Exception("LibreOffice window is unavailable.")                 #
        if not self.libreOfficeWindow.activate(wait=True):                        #
                raise Exception("Could not activate LibreOffice.")                #


    def openEllipsus(self):
        """Reactivates the right, open Ellipsus tab"""

        if self.ellipsusWindow is None or not self.ellipsusWindow.isAlive:        #
            raise Exception("Ellipsus browser window is unavailable.")            #
        if not self.ellipsusWindow.activate(wait=True):                           #
            raise Exception("Could not activate Ellipsus.")                       #
