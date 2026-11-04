#Ellipsus Automaton - Created by Kaia Aydelotte, 09.02.26, using ChatGPT and modified personally
#Python file designed to automate copy/paste odt file transfer into Ellipsus
#Last updated 09.09.26

"""
IMPORT:
    1. Opens the selected LibreOffice document.
    2. Starts at the specified Writer page.
    3. Copies one physical Writer page.
    4. Pastes it into Ellipsus.
    5. Inserts an Ellipsus divider immediately after it.
    6. Repeats until the end of the Writer document.

REMOVE:
    Removes previously imported Ellipsus "pages" one at a time.
    The user manually places the cursor at the END of the page they want
    removed, then the program searches backward for the previous divider
    and deletes that page.

SAFETY:
    F12 immediately stops the automation.
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

# F12 is the emergency stop key.
STOP_KEY = "f12"

# Ellipsus Markdown divider. Ellipsus recognizes this Markdown pattern as a Divider.
ELLIPSUS_DIVIDER = "----***___"


# ============================================================
# GLOBAL STATE
# ============================================================

stopEvent = threading.Event()         #initialize emergency stop thread that listens for the F12 key
automationRunning = False


# ============================================================
# EMERGENCY STOP AND SLEEP FUNCTIONS
# ============================================================

def emergencyStop():                    #Multi-OS
    """Immediately request that the current automation stop."""
    stopEvent.set()                     #trigger thread - F12 was pressed


def checkStop():                        #Multi-OS
    """return True if the user has requested an emergency stop."""
    return stopEvent.is_set()           #check the stopEvent thread, return True or False


def safeSleep(seconds):                  #Multi-OS
    """sleep while checking for an emergency stop (F12 stays responsive)"""

    endTime = time.time() + seconds      #set endTime to current time + desired seconds
    while time.time() < endTime:         #while the current time is less than the endTime....
        if checkStop():                  #if the user pressed the F12 key...
            return False                 #...STOP THE LOOP (now the program can run emergency stop protocols)
        time.sleep(0.05)                 #...but if they haven't pressed the key, run for .05 more seconds

    return True                          #Otherwise, return True


def countdown(updateStatus):                             #Multi-OS
    """Give the user a countdown before automation begins."""

    for remaining in range(COUNTDOWN_SECONDS, 0, -1):    #if there is still time left in the countdown...
        if checkStop():                                  #...first, check if the user has pressed F12
            return False                                 #...if so, STOP the function
        updateStatus(                                    #otherwise, display time left and remind user no touchie
            f"Starting in {remaining}... "
            f"DO NOT TOUCH THE MOUSE OR KEYBOARD."
        )
        if not safeSleep(1):                             #...Pause for a second....
            return False                                 #(But still STOP if user keys F12)

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
    if not safeSleep(DEFAULT_DELAY):                             #Pause to load. If safeSleep returns False (i.e. F12 was pressed)
        return False                                             #...HALT. Return False and end function.

    for _ in range(pageNumber - 1):                              #otherise, loop the number of pages we need to advance (one less than total)
        if checkStop():                                          #For each loop, check if F12 has been pressed...
            return False                                         #...if so, stop loop!

        pyautogui.hotkey("ctrl", "pagedown")                     #otherwise, advance one page (program uses ctrl/pagedown shortcut)
        if not safeSleep(0.08):                                  #...pause .08 seconds for LibreOffice to catch up...
            return False                                         #...but if user presses F12 during the pause, stop anyways

    pyautogui.hotkey("ctrl", "pageup")                           #automate ctrl/pageup to go to top of the right page...

    return safeSleep(DEFAULT_DELAY)                              #return a delay to load. Finished!


def selectCurrentPage(updateStatus):                #Multi-OS
    """Select current page text"""

    updateStatus("Selecting current page...")       #Display message that program is selecting page...
    pyautogui.hotkey("ctrl", "pageup")              #...Go to top of page...
    if not safeSleep(0.2):                          #...pause to load. If F12 is pressed...
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
    if not safeSleep(0.2):                            #pause to load - if user presses F12...
        return False                                  #...STOP function here

    pyautogui.press("enter")                          #automate key ENTER

    return safeSleep(DEFAULT_DELAY)                   #return delay - finished!


# ============================================================
# IMPORT MODE
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
            return                                             #...(careful to check for F12)
        if checkStop():                                        #...check if user pressed F12 again...
            return                                             #...(and end function if they did)
        if not openEllipsus(url, updateStatus):                #...then open to the Ellipsus document...
            return                                             #...(still checking for F12)
        if checkStop():                                        #...and check if they pressed F12 again
            return                                             #...(still end function if they did)
        if not countdown(updateStatus):                        #Now start the countdown...
            return                                             #...(And check for F12 again)
        if not goToPage(startingPage, updateStatus):           #...And go to the page the user selected!
            return                                             #...(Still check for F12)
        
        currentPage = startingPage                             #Initialize the currentPage var and set it to the starting page

        #MAIN LOOP
        while not checkStop():                                 #While the F12 button hasn't been keyed...

            updateStatus(f"Processing page {currentPage}...")  #Update the user that we are starting on page currentPage
            if not selectCurrentPage(updateStatus):            #Select the page text...
                break                                          #...(Check for F12)
            if not copyCurrentPage(updateStatus):              #...copy the text...
                break                                          #...(Check for F12)

            pyautogui.hotkey("alt", "tab")                     #Use alt/tab to switch to Ellipsus.

            if not safeSleep(DEFAULT_PAGE_DELAY):              #Pause to load...
                break                                          #...(Check for F12)
            if not pasteIntoEllipsus(updateStatus):            #...and paste the text
                break                                          #...(Check for F12)
            if not insertEllipsusDivider(updateStatus):        #...insert divider...
                break

            updateStatus(f"Page {currentPage} transferred successfully.") #Alert user that the page was transferred

            if testMode:                                       #Test mode intentionally stops after ONE page.
                updateStatus(f"TEST COMPLETE — page {currentPage} transferred.") #Alert user that Test concluded
                break                                          #...(Check F12)

            pyautogui.hotkey("alt", "tab")                     #Switch back to LibreOffice.
            if not safeSleep(DEFAULT_PAGE_DELAY):              #Pause to load...
                break                                          #...(Check F12)
            pyautogui.hotkey("ctrl", "pagedown")               #...and move to next page.
            if not safeSleep(DEFAULT_DELAY):                   #...Pause to load...
                break                                          #...(Check F12)

            currentPage += 1                                   #...and add one to currentPage. We are moving to next page

        if checkStop():                                        #once loop is complete...
            updateStatus(                                      #...if the loop was prematurely killed by F12...
                f"STOPPED by emergency command. "              #...alert the user that program was stopped prematurely...
                f"Last attempted page: {currentPage}"          #...and what page it stopped on
            )
        else:                                                  #...if instead the loop completed successfully...
            updateStatus("Import finished.")                   #...tell the user that it worked


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
        return False                                          #...(while still checking for F12)
    

    return True                                               #...then conclude the function


def removePages(
    numberOfPages,
    testMode,
    updateStatus,
):
    """
    Remove multiple previously imported pages.

    The user should have the correct Ellipsus document open before
    starting this operation.
    """

    global automationRunning                            #access the automationRunning var from outside function

    automationRunning = True                            #Set automationRunning to True - Automation has started
    stopEvent.clear()                                   #And reset the Emergency Stop function in preperation

    try:                                                #try the following...
        if not countdown(updateStatus):                       #Start the countdown
            return                                            #    (Still watching for F12)

        for count in range(1, numberOfPages + 1):             #For each page specified (Adding one so Python doesn't stop one short)...
            if checkStop():                                   #...check for F12
                break                                         #...(If F12 has been keyed, abort function)
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
           -Connecting F12 to Emergency Stop
        """
        super().__init__()                       #access initialization behavior from parent class, CustomTkinter, to create the initial window

        self.title("Ellipsus Automaton")         #Title the window
        self.geometry("720x650")                 #Set the window size to 720 x 650 pixels...
        self.resizable(False, False)             #...and prevent user from resizing the window

        self.libreOfficeDoc = ""                 #Create a variable to hold the path to the LibreOffice file

        #APPEARANCE
        ctk.set_appearance_mode("dark")          #Set the window to dark mode...
        ctk.set_default_color_theme("purple")    #...and set the color theme

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

        self.file_label = ctk.CTkLabel(          #write out a label...
            fileFrame,                           #...put it in the file frame, but...
            text="No document selected",         #...this one can be changed!
            wraplength=500
        )
        self.file_label.pack(                    #...also put this one in the window
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

        self.url_entry = ctk.CTkEntry(           #Now, create the textbox to enter the URL...
            urlFrame,                            #...put said textbox in the URL frame...
            placeholder_text="Paste the Ellipsus document URL here..."
        )
        self.url_entry.pack(                     #...and put that in the window
            padx=15,
            pady=(0, 15),
            fill="x"                             #...have it fill horizontally
        )


        #IMPORT CONTROLS
        importFrame = ctk.CTkFrame(self)         #Now create the Import Controls box...
        importFrame.pack(                        #...put that in the window...
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(
            importFrame,
            text="IMPORT FROM LIBREOFFICE",
            font=("Arial", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        page_row = ctk.CTkFrame(importFrame)

        page_row.pack(
            padx=15,
            pady=5,
            fill="x"
        )

        ctk.CTkLabel(
            page_row,
            text="Starting Writer page:"
        ).pack(
            side="left"
        )

        self.start_page_entry = ctk.CTkEntry(
            page_row,
            width=80
        )

        self.start_page_entry.insert(
            0,
            "1"
        )

        self.start_page_entry.pack(
            side="left",
            padx=10
        )

        self.test_import_var = tk.BooleanVar(
            value=True
        )

        ctk.CTkCheckBox(
            page_row,
            text="Test mode (1 page only)",
            variable=self.test_import_var
        ).pack(
            side="left",
            padx=15
        )

        ctk.CTkButton(
            importFrame,
            text="START IMPORT",
            height=40,
            command=self.start_import
        ).pack(
            padx=15,
            pady=(10, 15),
            fill="x"
        )

        # ----------------------------------------------------
        # Removal controls
        # ----------------------------------------------------

        remove_frame = ctk.CTkFrame(self)

        remove_frame.pack(
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(
            remove_frame,
            text="REMOVE PREVIOUSLY IMPORTED PAGES",
            font=("Arial", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            remove_frame,
            text=(
                "Removal mode is intentionally disabled until the "
                "Ellipsus selection behavior is calibrated safely."
            ),
            wraplength=620
        ).pack(
            padx=15,
            pady=5
        )

        # ----------------------------------------------------
        # Emergency stop
        # ----------------------------------------------------

        ctk.CTkButton(
            self,
            text="EMERGENCY STOP  —  F12",
            fg_color="darkred",
            hover_color="red",
            height=45,
            command=emergencyStop
        ).pack(
            padx=25,
            pady=(10, 5),
            fill="x"
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Ready",
            font=("Arial", 13)
        )

        self.status_label.pack(
            pady=10
        )

        # ----------------------------------------------------
        # F12 emergency stop
        # ----------------------------------------------------

        self.bind(
            "<F12>",
            lambda event: emergencyStop()
        )

    # ========================================================
    # GUI METHODS
    # ========================================================

    def choose_file(self):

        filename = filedialog.askopenfilename(
            title="Choose LibreOffice document",
            filetypes=[
                ("LibreOffice Writer",
                 "*.odt *.docx"),
                ("All files",
                 "*.*")
            ]
        )

        if filename:

            self.libreoffice_file = filename

            self.file_label.configure(
                text=filename
            )

            self.update_status(
                "LibreOffice document selected."
            )

    def update_status(self, message):

        self.after(
            0,
            lambda: self.status_label.configure(
                text=f"Status: {message}"
            )
        )

    def start_import(self):

        if automation_running:
            messagebox.showwarning(
                "Already Running",
                "Automation is already running."
            )
            return

        if not self.libreoffice_file:

            messagebox.showerror(
                "Missing File",
                "Choose your LibreOffice document first."
            )

            return

        ellipsus_url = self.url_entry.get().strip()

        if not ellipsus_url:

            messagebox.showerror(
                "Missing URL",
                "Enter the Ellipsus document URL."
            )

            return

        try:

            starting_page = int(
                self.start_page_entry.get()
            )

            if starting_page < 1:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Page",
                "Starting page must be a positive whole number."
            )

            return

        test_mode = self.test_import_var.get()

        self.update_status(
            "Preparing import..."
        )

        worker = threading.Thread(
            target=exportPages,
            args=(
                self.libreoffice_file,
                ellipsus_url,
                starting_page,
                test_mode,
                self.update_status,
            ),
            daemon=True
        )

        worker.start()


# ============================================================
# MAIN
# ============================================================

def main():

    app = EllipsusTransferApp()

    app.mainloop()


if __name__ == "__main__":
    main()
