#Ellipsus Automaton - Created by Kaia Aydelotte, 09.02.26, using ChatGPT and modified personally
#Python file designed to automate copy/paste odt file transfer into Ellipsus
#Last updated 09.09.26

"""
EXPORT:
    1. Opens the selected LibreOffice document.
    2. Starts at the specified Writer page.
    3. Copies one physical Writer page.
    4. Pastes it into Ellipsus.
    5. Inserts an Ellipsus divider immediately after it.
    6. Repeats until the end of the Writer document.

REMOVE:
    Removes previously exported Ellipsus "pages" one at a time.
    The user manually places the cursor at the END of the page they want
    removed, then the program searches backward for the previous divider
    and deletes that page.

SAFETY:
    ESC immediately stops the automation.
    The program includes a countdown before automation begins.

Requirements:
    pip install pyautogui pyperclip customtkinter

IMPORTANT:
    This program controls your mouse and keyboard.
    Do not touch the keyboard/mouse while automation is running.
"""

#IMPORTS AND VARIABLES
import platform                             #helps program detect which operating system is in use
import time                                 #allows program to utilize and measure time
import threading                            #allows program to run threads
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import pyperclip
import customtkinter as ctk

from OSTask import OSTask                  #import OSTask class to handle the OS the computer is currently on

thisOS = OSTask()                          #initialize instance of OSTask to handle OS differences

DEFAULT_DELAY = 0.75
DEFAULT_PAGE_DELAY = 1.5
COUNTDOWN_SECONDS = 5

# ESC is the emergency stop key.
STOP_KEY = "ESC"

# Ellipsus Markdown divider. Ellipsus recognizes this Markdown pattern as a Divider.
ELLIPSUS_DIVIDER = "----***___"


# ============================================================
# GLOBAL STATE
# ============================================================

stopEvent = threading.Event()         #initialize emergency stop thread that listens for the ESC key
automationRunning = False


# ============================================================
# EMERGENCY STOP AND SLEEP FUNCTIONS
# ============================================================

def emergencyStop():                    #Multi-OS
    """Immediately request that the current automation stop."""
    stopEvent.set()                     #trigger thread - ESC was pressed


def checkStop():                        #Multi-OS
    """return True if the user has requested an emergency stop."""
    return stopEvent.is_set()           #check the stopEvent thread, return True or False


def safeSleep(seconds):                  #Multi-OS
    """sleep while checking for an emergency stop (ESC stays responsive)"""

    endTime = time.time() + seconds      #set endTime to current time + desired seconds
    while time.time() < endTime:         #while the current time is less than the endTime....
        if checkStop():                  #if the user pressed the ESC key...
            return False                 #...STOP THE LOOP (now the program can run emergency stop protocols)
        time.sleep(0.05)                 #...but if they haven't pressed the key, run for .05 more seconds

    return True                          #Otherwise, return True


def countdown(updateStatus):                             #Multi-OS
    """Give the user a countdown before automation begins."""

    for remaining in range(COUNTDOWN_SECONDS, 0, -1):    #if there is still time left in the countdown...
        if checkStop():                                  #...first, check if the user has pressed ESC
            return False                                 #...if so, STOP the function
        updateStatus(                                    #otherwise, display time left and remind user no touchie
            f"Starting in {remaining}... "
            f"DO NOT TOUCH THE MOUSE OR KEYBOARD."
        )
        if not safeSleep(1):                             #...Pause for a second....
            return False                                 #(But still STOP if user keys ESC)

    updateStatus("Automation started.")                  #Once loop has finished, display that Automation has started...
    return True                                          #...and return true. Showtime, suckers!



# ============================================================
# LIBREOFFICE
# ============================================================

def openLibreofficeFile(filename, updateStatus):     #Multi-OS
    """Opens the selected LibreOffice document."""

    updateStatus("Opening LibreOffice document...")   #tell user the file is opening by displaying message on GUI...
    thisOS.openFile(filename)                         #...then call OSTask function to open the right LibreOffice file
    return safeSleep(5)                               #...then pause for five seconds


def goToPage(pageNumber, updateStatus):                         #Multi-OS
    """
    Starts at the beginning of document and navigates to desired page 
    using page-navigation shortcuts
    """

    updateStatus(f"Navigating to page {pageNumber}...")          #Display that we are navigating to desired page...
    pyautogui.hotkey("ctrl", "home")                             #Put cursor at beginning of document.
    if not safeSleep(DEFAULT_DELAY):                             #Pause to load. If safeSleep returns False (i.e. ESC was pressed)
        return False                                             #...HALT. Return False and end function.

    for _ in range(pageNumber - 1):                              #otherise, loop the number of pages we need to advance (one less than total)
        if checkStop():                                          #For each loop, check if ESC has been pressed...
            return False                                         #...if so, stop loop!

        pyautogui.hotkey("ctrl", "pagedown")                     #otherwise, advance one page (program uses ctrl/pagedown shortcut)
        if not safeSleep(0.08):                                  #...pause .08 seconds for LibreOffice to catch up...
            return False                                         #...but if user presses ESC during the pause, stop anyways

    pyautogui.hotkey("ctrl", "pageup")                           #automate ctrl/pageup to go to top of the right page...

    return safeSleep(DEFAULT_DELAY)                              #return a delay to load. Finished!


def selectCurrentPage(updateStatus):                #Multi-OS
    """Select current page text"""

    updateStatus("Selecting current page...")       #Display message that program is selecting page...
    pyautogui.hotkey("ctrl", "pageup")              #...Go to top of page...
    if not safeSleep(0.2):                          #...pause to load. If ESC is pressed...
        return False                                #STOP the function
    pyautogui.hotkey("ctrl", "shift", "pagedown")   #...Use ctrl/pagedown to navigate to the bottom while holding shift to select text

    return safeSleep(DEFAULT_DELAY)                 #...and return delay. Finished!


def copyCurrentPage(updateStatus):                  #Multi-OS
    """Copy currently selected page."""

    updateStatus("Copying selected page...")        #Display message that program is copying selected page...
    pyautogui.hotkey("ctrl", "c")                   #...use ctrl/c to copy text...

    return safeSleep(DEFAULT_DELAY)                 #...then return delay. Finished!


# ============================================================
# ELLIPSUS
# ============================================================

def openEllipsus(url, updateStatus):                    #Multi-OS
    """
    Opens the specified Ellipsus document in the default browser.
    (The user must already be signed into Ellipsus in that browser.)
    """
    updateStatus("Opening Ellipsus document...")        #display message that program is opening Ellipsus doc
    webbrowser.open(url)                                #open Ellipsus doc from the URL

    return safeSleep(5)                                 #return delay - Finished!


def pasteIntoEllipsus(updateStatus):               #Multi-OS
    """Pastes the copied page into Ellipsus."""

    updateStatus("Pasting page into Ellipsus...")  #display message that program is pasting copied page
    pyautogui.hotkey("ctrl", "v")                  #automate ctrl/v and paste page

    return safeSleep(DEFAULT_PAGE_DELAY)           #return delay - Finished!


def insertEllipsusDivider(updateStatus):              #Multi-OS
    """
    Inserts an Ellipsus divider.

    Ellipsus supports the Markdown divider shortcut:

        ----***___

    Typing this on a new line and pressing Enter causes Ellipsus
    to convert it into a Divider when Markdown shortcuts are enabled.
    """

    updateStatus("Inserting Ellipsus divider...")     #display message that program is inserting devider
    pyautogui.write(ELLIPSUS_DIVIDER, interval=0.01)  #have pyautogui type out Markdown divider shortcut
    if not safeSleep(0.2):                            #pause to load - if user presses ESC...
        return False                                  #...STOP function here

    pyautogui.press("enter")                          #automate key ENTER

    return safeSleep(DEFAULT_DELAY)                   #return delay - finished!


# ============================================================
# EXPORT MODE
# ============================================================

def exportPages(
    file,
    url,
    startingPage,
    testMode,
    updateStatus,
):
    """
    Pulls up LibreOffice and copies/pastes pages into Ellipsus
    until done
    """

    global automationRunning                              #access the automationRunning var from outside function...
    automationRunning = True                              #...and set that variable to True. Automation is now running
    stopEvent.clear()                                     #Then reset the Emergency Stop Sensor

    try:                                                  #try the below...
        if not openLibreofficeFile(file, updateStatus):        #open the LibreOffice File...
            return                                             #...(careful to check for ESC)
        if checkStop():                                        #...check if user pressed ESC again...
            return                                             #...(and end function if they did)
        if not openEllipsus(url, updateStatus):                #...then open to the Ellipsus document...
            return                                             #...(still checking for ESC)
        if checkStop():                                        #...and check if they pressed ESC again
            return                                             #...(still end function if they did)
        if not countdown(updateStatus):                        #Now start the countdown...
            return                                             #...(And check for ESC again)
        if not goToPage(startingPage, updateStatus):           #...And go to the page the user selected!
            return                                             #...(Still check for ESC)
        
        currentPage = startingPage                             #Initialize the currentPage var and set it to the starting page

        #MAIN LOOP
        while not checkStop():                                 #While the ESC button hasn't been keyed...

            updateStatus(f"Processing page {currentPage}...")  #Update the user that we are starting on page currentPage
            if not selectCurrentPage(updateStatus):            #Select the page text...
                break                                          #...(Check for ESC)
            if not copyCurrentPage(updateStatus):              #...copy the text...
                break                                          #...(Check for ESC)

            pyautogui.hotkey("alt", "tab")                     #Use alt/tab to switch to Ellipsus.

            if not safeSleep(DEFAULT_PAGE_DELAY):              #Pause to load...
                break                                          #...(Check for ESC)
            if not pasteIntoEllipsus(updateStatus):            #...and paste the text
                break                                          #...(Check for ESC)
            if not insertEllipsusDivider(updateStatus):        #...insert divider...
                break

            updateStatus(f"Page {currentPage} transferred successfully.") #Alert user that the page was transferred

            if testMode:                                       #Test mode intentionally stops after ONE page.
                updateStatus(f"TEST COMPLETE — page {currentPage} transferred.") #Alert user that Test concluded
                break                                          #...(Check ESC)

            pyautogui.hotkey("alt", "tab")                     #Switch back to LibreOffice.
            if not safeSleep(DEFAULT_PAGE_DELAY):              #Pause to load...
                break                                          #...(Check ESC)
            pyautogui.hotkey("ctrl", "pagedown")               #...and move to next page.
            if not safeSleep(DEFAULT_DELAY):                   #...Pause to load...
                break                                          #...(Check ESC)

            currentPage += 1                                   #...and add one to currentPage. We are moving to next page

        if checkStop():                                        #once loop is complete...
            updateStatus(                                      #...if the loop was prematurely killed by ESC...
                f"STOPPED by emergency command. "              #...alert the user that program was stopped prematurely...
                f"Last attempted page: {currentPage}"          #...and what page it stopped on
            )
        else:                                                  #...if instead the loop completed successfully...
            updateStatus("Emport finished.")                   #...tell the user that it worked


    except Exception as error:                            #Unless some sort of issue occured...
        updateStatus(f"ERROR: {error}")                        #...then tell the user what error 
        messagebox.showerror(                                  #...and display a pop-up window with said error
            "Automation Error",
            str(error)
        )


    finally:                                              #Whatever happened above...
        automationRunning = False                              #...turn off the automation



# ============================================================
# REMOVE MODE
# ============================================================

def removePreviousPage(updateStatus):
    """
    Remove one manually delineated Ellipsus page.

    IMPORTANT:
        The user must place the cursor somewhere INSIDE the page
        they want removed before starting this operation.

    The routine:

        1. Moves to the beginning of the current page.
        2. Searches backward for the preceding divider.
        3. Selects the page.
        4. Deletes it.

    Because Ellipsus is a live web editor, this is intentionally
    conservative and should be tested manually first.
    """

    updateStatus("Preparing to remove one Ellipsus page...")

    pyautogui.hotkey("ctrl", "home")                          #Move to beginning of current page/document region.
    if not safeSleep(DEFAULT_DELAY):                          #Pause to load...
        return False                                          #...(while still checking for ESC)
    

    return True                                               #...then conclude the function


def removePages(
    numberOfPages,
    testMode,
    updateStatus,
):
    """
    Remove multiple previously exported pages.

    The user should have the correct Ellipsus document open before
    starting this operation.
    """

    global automationRunning                            #access the automationRunning var from outside function

    automationRunning = True                            #Set automationRunning to True - Automation has started
    stopEvent.clear()                                   #And reset the Emergency Stop function in preperation

    try:                                                #try the following...
        if not countdown(updateStatus):                       #Start the countdown
            return                                            #    (Still watching for ESC)

        for count in range(1, numberOfPages + 1):             #For each page specified (Adding one so Python doesn't stop one short)...
            if checkStop():                                   #...check for ESC
                break                                         #...(If ESC has been keyed, abort function)
            updateStatus(                                     #...Update user on which page we are on 
                f"Removal {count} of {numberOfPages}"
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Ellipsus supports Find and Replace, including
            # regular expressions. We use the divider as the
            # boundary between pages.
            #
            # The first version intentionally pauses here
            # rather than blindly deleting large amounts of
            # manuscript text.
            # ------------------------------------------------

            updateStatus(                                     #Update user that it is ready for the next deletion
                "Removal mode is ready for the next deletion."
            )

            # TODO:
            # The exact browser/editor selection behavior needs
            # to be calibrated against the user's Ellipsus
            # document before making this destructive.
            #
            # We deliberately refuse to guess here.

            if testMode:
                updateStatus(
                    "TEST MODE: no text was deleted."
                )
                break

            # Safety stop until the deletion mechanism has been
            # calibrated.
            updateStatus(
                "Deletion paused: selection calibration required."
            )
            break

    finally:
        automationRunning = False




# ============================================================
# GUI
# ============================================================

class EllipsusAutomaton(ctk.CTk):

    def __init__(self):                          #Run automatically when program creates an instance of this class
        """
        This function builds the program window itself, and runs automatically
        upon creating an instance of the class. This means it is responsible for:
           -Building the controls
           -Configuring the window, including what goes where
           -Connecting buttons to the right code
           -Connecting ESC to Emergency Stop
        """
        super().__init__()                       #access initialization behavior from parent class, CustomTkinter, to create the initial window

        self.title("Ellipsus Automaton")         #Title the window
        self.geometry("720x650")                 #Set the window size to 720 x 650 pixels...
        self.resizable(False, False)             #...and prevent user from resizing the window

        self.libreOfficeDoc = ""                 #Create a variable to hold the path to the LibreOffice file

        #APPEARANCE
        ctk.set_appearance_mode("dark")          #Set the window to dark mode...
        ctk.set_default_color_theme("dark-blue")  #...and set the color theme          [JSON STYLE FILE HERE]

        #TITLE
        title = ctk.CTkLabel(                    #Write the title out...
            self,
            text="ELLIPSUS AUTOMATON",
            font=("Arial", 26, "bold")
        )
        title.pack(pady=(25, 5))                 #... and put it in the window

        subtitle = ctk.CTkLabel(                 #Then write the subtitle out...
            self,
            text="LibreOffice Writer → Ellipsus",
            font=("Arial", 14)
        )
        subtitle.pack(pady=(0, 20))              #...and also put it in the window


        #FILE SELECTION CONTROLS
        fileFrame = ctk.CTkFrame(self)           #Now make a "frame", or a box to put file controls in...
        fileFrame.pack(                          #...and also put that into the window
            padx=25,
            pady=10,
            fill="x"                             #...set that box to fill horizontally
        )

        ctk.CTkLabel(                            #Write out a label...
            fileFrame,                           #...and put it in the file frame box
            text="LibreOffice document"
        ).pack(                                  #...Put it in the window...
            anchor="w",                          #...and anchor it "west", or to the left
            padx=15,
            pady=(10, 5)
        )

        self.fileLabel = ctk.CTkLabel(           #write out a label...
            fileFrame,                           #...put it in the file frame, but...
            text="No document selected",         #...this one can be changed!
            wraplength=500
        )
        self.fileLabel.pack(                     #...also put this one in the window
            padx=15,
            pady=5
        )

        ctk.CTkButton(                           #Make the "Choose File" button...
            fileFrame,                           #...(which goes in the file frame)
            text="Choose File",
            command=self.chooseFile              #...and have it call chooseFile when pressed
        ).pack(                                  #...and also put this one in the window
            pady=(5, 15)
        )


        #ELLIPSUS URL CONTROLS
        urlFrame = ctk.CTkFrame(self)            #Now create a frame to hold the URL controls...
        urlFrame.pack(                           #...and put that in the window
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(                            #Now make a label for the text box...
            urlFrame,                            #...put it in the URL frame...
            text="Ellipsus Document URL"
        ).pack(                                  #...and put it in the window
            anchor="w",                          #...also anchor this to the left
            padx=15,
            pady=(10, 5)
        )

        self.urlEntry = ctk.CTkEntry(           #Now, create the textbox to enter the URL...
            urlFrame,                            #...put said textbox in the URL frame...
            placeholder_text="Paste the Ellipsus document URL here..."
        )
        self.urlEntry.pack(                     #...and put that in the window
            padx=15,
            pady=(0, 15),
            fill="x"                             #...have it fill horizontally
        )


        #EXPORT CONTROLS
        exportFrame = ctk.CTkFrame(self)         #Now create the Export Controls box...
        exportFrame.pack(                        #...put that in the window...
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(                            #Label the controls...
            exportFrame,                         #...(Put that in the export box)
            text="EXPORT FROM LIBREOFFICE",
            font=("Arial", 16, "bold")
        ).pack(                                  #...and put that in the window
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        pageRow = ctk.CTkFrame(exportFrame)      #Make another frame within the first frame, to hold a few controls...
        pageRow.pack(                            #...and put it in the window
            padx=15,
            pady=5,
            fill="x"
        )

        ctk.CTkLabel(                            #now put another label, for the starting page textbox...
            pageRow,                             #...put that in the pageRow frame
            text="Start Page:"
        ).pack(                                  #...then put it in the window
            side="left"
        )


        self.startPageEntry = ctk.CTkEntry(    #Now make a small textbox to put the start page in...
            pageRow,                             #...put it in the pageRow...
            width=80
        )
        self.startPageEntry.insert(            #...insert '1' (for page 1) at "position 0" of the textbox...
            0,
            "1"
        )
        self.startPageEntry.pack(              #...then put it in the window on the left side.
            side="left",
            padx=10
        )


        self.testCheckbox = tk.BooleanVar(    #Import the boolean value for Test Mode checkbox
            value=False                          #...and set the default value to false...
        )
        ctk.CTkCheckBox(                         #...Create the checkbox itself...
            pageRow,                             #...Put it in the pageRow frame...
            text="Test Mode (1 page only)",      #...label it...
            variable=self.testCheckbox
        ).pack(                                  #...then put it in the window on the left side
            side="left",
            padx=15
        )

        ctk.CTkButton(                           #Now create the export button...
            exportFrame,                         #...put it in the Export Controls frame...
            text="START EXPORT",                 #...label it...
            height=40,
            command=self.startExport
        ).pack(                                  #...then put it into the window
            padx=15,
            pady=(10, 15),
            fill="x"
        )


        #REMOVAL CONTROLS
        removalFrame = ctk.CTkFrame(self)        #Create the Removal Controls box...
        removalFrame.pack(                       #...and put it in the window
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(                            #Label the Removal Controls... 
            removalFrame,                        #...put it in the Removal Controls box...
            text="REMOVE PREVIOUSLY EXPORTED PAGES",
            font=("Arial", 16, "bold")
        ).pack(                                  #...and put it in the window
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        ctk.CTkLabel(                            #PLACEHOLDER LABEL
            removalFrame,
            text=(
                "Removal mode is intentionally disabled until the "
                "Ellipsus selection behavior is calibrated safely."
            ),
            wraplength=620
        ).pack(
            padx=15,
            pady=5
        )


        #EMERGENCY STOP
        ctk.CTkButton(                           #Create the Emergency Stop Button....
            self,
            text="EMERGENCY STOP  —  ESC",       #...label it...
            fg_color="darkred",
            hover_color="red",
            height=45,
            command=emergencyStop                #...and key the button to the emergencyStop command
        ).pack(                                  #...then put it in the window
            padx=25,
            pady=(10, 5),
            fill="x"
        )


        #STATUS
        self.statusLabel = ctk.CTkLabel(
            self,
            text="Status: Ready",
            font=("Arial", 13)
        )

        self.statusLabel.pack(
            pady=10
        )


        #EMERGENCY STOP = ESC
        self.bind(                              #bind this event to the program window, which is...
            "<Escape>",                         #...pressing ESC
            lambda event: emergencyStop()       #If keyed, 
        )



    # ========================================================
    # GUI METHODS
    # ========================================================

    def chooseFile(self):
        """Funtion called when user chooses a file"""

        filename = filedialog.askopenfilename(     #open file window for user to browse files, copy file path of selected file
            title="Choose Document (.odt, .docx)", #...title the file selection window...
            filetypes=[                            #...and restrict possible filetypes to .odt and .docx
                ("LibreOffice Doc",
                 "*.odt *.docx"),
                ("All files",                      #...Still show all files though (* means "anything before this")
                 "*.*")
            ]
        )
        if filename:                              #if the user actually selected a file...
            self.libreOfficeDoc = filename        #...store this to the application window, so we can access it later

            self.fileLabel.configure(             #...then change the fileLabel we created earlier...
                text = filename                   #...to the name of the file selected...
            )
            self.updateStatus(                    #...then alert the user that we have selected the file
                "LibreOffice document selected."
            )


    def updateStatus(self, message):
        self.after(                               
            0,                                     #as soon as automatonEllipsus can process this...
            lambda: self.statusLabel.configure(    #...configure the status widget...
                text=f"Status: {message}"          #...to show the desired text
            )
        )

    def startExport(self):
        """Function called when Start Export button is clicked"""

        if automationRunning:                         #Check if the automation is running. If so...
            messagebox.showwarning(                   #...tell the user that...
                "Already Running",
                "Automation is already running."
            )
            return                                    #...and stop export attempt
        if not self.libreOfficeDoc:                   #Next, is there a document saved? If not...
            messagebox.showerror(                     #...tell the user that...
                "Missing File",
                "Choose your document first."
            )
            return                                    #...and stop the export function

        ellipsusURL = self.urlEntry.get().strip()     #Retrieve the URL from the URL box and strip any white space off the ends        

        if not ellipsusURL:                           #If there is no URL waiting in the box...
            messagebox.showerror(                     #...tell the user they need to enter a URL...
                "Missing URL",
                "Enter the Ellipsus document URL."
            )
            return                                    #...and stop the export function

        try:
            startingPage = int(                       #Retrieve the contents of the startPageEntry box and turn it into an integer...
                self.startPageEntry.get()
            )
            if startingPage < 1:                      #If that page is less than one, or they didn't enter a page...
                raise ValueError                      #...raise ValueError...
            
        except ValueError:
            messagebox.showerror(                     #...and tell the user to give us a real start page
                "Invalid Page",
                "Starting page must be a positive whole number."
            )
            return

        testMode = self.testCheckbox.get()           #Check if "test mode" is checked...
        self.updateStatus(                           #...and alert user we are preparing for export
            "Preparing export..."
        )

        exporting = threading.Thread(                #create a new thread...
            target = exportPages,                    #...and have it execute the exportPages function...
            args = (                                 #...passing the following arguements through the function
                self.libreOfficeDoc,
                ellipsusURL,
                startingPage,
                testMode,
                self.updateStatus,                  #...including the updateStatus function, so exportPages can use updateStatus
            ),
            daemon = True                           #...then mark this as a daemon thread, so the user can close the window mid-function
        )
        exporting.start()                           #Now start the thread. 


# ============================================================
# MAIN
# ============================================================

def main():
    """Function designed to initialize application"""
    app = EllipsusAutomaton()                           #Create an instance of EllipsusAutomaton
    app.mainloop()                                      #Start the GUI event loop


if __name__ == "__main__":                              #only execute main function if the user is executing this file
    main()
