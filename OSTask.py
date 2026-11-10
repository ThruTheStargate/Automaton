#OSTask - Created by Kaia Aydelotte, 09.03.26
#Class designed to handle differences in operating systems
#Last updated 11.10.26

import os           #General operating-system functions
from pathlib import Path
import platform     #Detects current system OS
import subprocess   #Launches/interacts with other programs
from tkinter import filedialog, messagebox

print("Reached HERE")

class OSTask:
    def __init__(self):
        self.os = platform.system()

    def openFile(self, filename):
        """Function designed to open files"""  
        if self.os == "Windows":
            os.startfile(filename)
        elif self.os == "Linux":
            subprocess.Popen(["libreoffice", filename])
        else:
            raise OSError("Unsupported operating system")

    def fileExplorer(self):
        """Function designed to use and handle the file picker"""
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