#OSTask - Created by Kaia Aydelotte, 09.03.26
#Class designed to handle differences in operating systems
#Last updated 11.10.26

import os           #General operating-system functions
from pathlib import Path
import platform     #Detects current system OS
import pywinctl as pwc
import subprocess   #Launches/interacts with other programs
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
        """Initializes the selected LibreOffice document the first time."""

        updateStatus("Opening LibreOffice document...")   #tell user the file is opening by displaying message on GUI...
        self.openFile(filename)                           #then launch the right LibreOffice file

        docTitle = Path(filename).stem.lower()            #Now, extract just the document title from the file name, for identification
        timeout = 30                                      #

        return safeSleep(5)                               #...then pause for five seconds

    def launchEllipsus(url, updateStatus, safeSleep):
        """
        Initializes the specified Ellipsus document in the default browser
        the first time.
        (The user must already be signed into Ellipsus in that browser.)
        """
        updateStatus("Initializing Ellipsus document...")   #display message that program is opening Ellipsus doc the first time...
        webbrowser.open(url)                                #...then open Ellipsus doc from the URL

        return safeSleep(5)                                 #return delay - Finished!


    def openLibreoffice(self):
        """Seeks out the correct, open LibreOffice file"""
        ...

    def openEllipsus(self):
        """Seeks out the right, open Ellipsus tab"""
        ...

    



    while time.monotonic() < timeout:
        matches = [
            window for window in pwc.getAllWindows()
            if titlePart in window.title.lower()
        ]

        if len(matches) == 1:
            self.libreOfficeWindow = matches[0]
            return

        if len(matches) > 1:
            raise Exception("Multiple LibreOffice windows found.")

        time.sleep(0.25)

    raise TimeoutError("LibreOffice window was not found.")


def initializeEllipsus(self, url, titlePart):
    """Opens Ellipsus and stores its browser window reference."""
    webbrowser.open(url)

    titlePart = titlePart.lower()
    timeout = time.monotonic() + 30

    while time.monotonic() < timeout:
        matches = [
            window for window in pwc.getAllWindows()
            if titlePart in window.title.lower()
        ]

        if len(matches) == 1:
            self.ellipsusWindow = matches[0]
            return

        if len(matches) > 1:
            raise Exception("Multiple Ellipsus windows found.")

        time.sleep(0.25)

    raise TimeoutError("Ellipsus browser window was not found.")


def openLibreOffice(self):
    """Activates the initialized LibreOffice window."""
    if self.libreOfficeWindow is None or not self.libreOfficeWindow.isAlive:
        raise Exception("LibreOffice window is unavailable.")

    if not self.libreOfficeWindow.activate(wait=True):
        raise Exception("Could not activate LibreOffice.")


def openEllipsus(self):
    """Activates the initialized Ellipsus browser window."""
    if self.ellipsusWindow is None or not self.ellipsusWindow.isAlive:
        raise Exception("Ellipsus browser window is unavailable.")

    if not self.ellipsusWindow.activate(wait=True):
        raise Exception("Could not activate Ellipsus.")
