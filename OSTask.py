#OSTask - Created by Kaia Aydelotte, 09.03.26
#Class designed to handle differences in operating systems
#Last updated 09.03.26

import os           #General operating-system functions
import platform     #Detects current system OS
import subprocess   #Launches/interacts with other programs

class OSTask:
    def _init_(self):
        self.os = platform.system()

    def openFile(self, filename):    
        if self.os == "Windows":
            os.startfile(filename)
        elif self.os == "Linux":
            subprocess.Popen(["libreoffice", filename])
        else:
            raise OSError("Unsupported operating system")

    def switchWindow(self):
        ...

    def copy(self):
        ...

    def paste(self):
        ...

    def emergencyStop(self):
        ...