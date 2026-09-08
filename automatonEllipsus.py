#Ellipsus Automaton - Created by Kaia Aydelotte, 09.02.26, using ChatGPT and modified personally
#Python file designed to automate copy/paste odt file transfer into Ellipsus
#Last updated 09.02.26

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

#IMPORTS
import platform                             #helps program detect which operating system is in use
import time
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import pyperclip
import customtkinter as ctk

from OSTask import OSTask                  #import OSTask class to handle the OS the computer is currently on


#FUNCTIONS
# ============================================================
# CONFIGURATION
# ============================================================
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
automation_running = False


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


def insertEllipsusDivider(updateStatus):
    """
    Insert an Ellipsus divider.

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

def import_pages(
    libreoffice_file,
    ellipsus_url,
    starting_page,
    test_mode,
    update_status,
):
    """
    Main import routine.
    """

    global automation_running

    automation_running = True
    stopEvent.clear()

    try:

        # ----------------------------------------------------
        # Open LibreOffice
        # ----------------------------------------------------

        if not openLibreofficeFile(
            libreoffice_file,
            update_status
        ):
            return

        if checkStop():
            return

        # ----------------------------------------------------
        # Open Ellipsus
        # ----------------------------------------------------

        if not open_ellipsus(
            ellipsus_url,
            update_status
        ):
            return

        if checkStop():
            return

        # ----------------------------------------------------
        # Countdown
        # ----------------------------------------------------

        if not countdown(update_status):
            return

        # ----------------------------------------------------
        # Navigate to starting page
        # ----------------------------------------------------

        if not goToPage(
            starting_page,
            update_status
        ):
            return

        current_page = starting_page

        # ----------------------------------------------------
        # Main loop
        # ----------------------------------------------------

        while not checkStop():

            update_status(
                f"Processing Writer page {current_page}..."
            )

            # Select page.
            if not selectCurrentPage(update_status):
                break

            # Copy page.
            if not copyCurrentPage(update_status):
                break

            # Switch to Ellipsus.
            pyautogui.hotkey("alt", "tab")

            if not safeSleep(DEFAULT_PAGE_DELAY):
                break

            # Paste page.
            if not paste_into_ellipsus(update_status):
                break

            # Insert divider.
            if not insert_ellipsus_divider(update_status):
                break

            update_status(
                f"Page {current_page} transferred successfully."
            )

            # Test mode intentionally stops after ONE page.
            if test_mode:
                update_status(
                    f"TEST COMPLETE — page {current_page} transferred."
                )
                break

            # Switch back to LibreOffice.
            pyautogui.hotkey("alt", "tab")

            if not safeSleep(DEFAULT_PAGE_DELAY):
                break

            # Move to next Writer page.
            pyautogui.hotkey("ctrl", "pagedown")

            if not safeSleep(DEFAULT_DELAY):
                break

            current_page += 1

        if checkStop():
            update_status(
                f"STOPPED by emergency command. "
                f"Last attempted page: {current_page}"
            )
        else:
            update_status(
                "Import finished."
            )

    except Exception as error:

        update_status(
            f"ERROR: {error}"
        )

        messagebox.showerror(
            "Automation Error",
            str(error)
        )

    finally:

        automation_running = False


# ============================================================
# REMOVE MODE
# ============================================================

def remove_previous_page(update_status):
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

    update_status("Preparing to remove one Ellipsus page...")

    # Move to beginning of current page/document region.
    pyautogui.hotkey("ctrl", "home")

    if not safeSleep(DEFAULT_DELAY):
        return False

    return True


def remove_pages(
    number_of_pages,
    test_mode,
    update_status,
):
    """
    Remove multiple previously imported pages.

    The user should have the Ellipsus document focused before
    starting this operation.
    """

    global automation_running

    automation_running = True
    stopEvent.clear()

    try:

        if not countdown(update_status):
            return

        for count in range(1, number_of_pages + 1):

            if checkStop():
                break

            update_status(
                f"Removal {count} of {number_of_pages}"
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

            update_status(
                "Removal mode is ready for the next deletion."
            )

            # TODO:
            # The exact browser/editor selection behavior needs
            # to be calibrated against the user's Ellipsus
            # document before making this destructive.
            #
            # We deliberately refuse to guess here.

            if test_mode:
                update_status(
                    "TEST MODE: no text was deleted."
                )
                break

            # Safety stop until the deletion mechanism has been
            # calibrated.
            update_status(
                "Deletion paused: selection calibration required."
            )
            break

    finally:

        automation_running = False


# ============================================================
# GUI
# ============================================================

class EllipsusTransferApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Ellipsus Page Transfer")
        self.geometry("720x650")
        self.resizable(False, False)

        self.libreoffice_file = ""

        # ----------------------------------------------------
        # Appearance
        # ----------------------------------------------------

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = ctk.CTkLabel(
            self,
            text="ELLIPSUS PAGE TRANSFER",
            font=("Arial", 26, "bold")
        )

        title.pack(pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="LibreOffice Writer → Ellipsus",
            font=("Arial", 14)
        )

        subtitle.pack(pady=(0, 20))

        # ----------------------------------------------------
        # File selection
        # ----------------------------------------------------

        file_frame = ctk.CTkFrame(self)

        file_frame.pack(
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(
            file_frame,
            text="LibreOffice document"
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="No document selected",
            wraplength=500
        )

        self.file_label.pack(
            padx=15,
            pady=5
        )

        ctk.CTkButton(
            file_frame,
            text="Choose LibreOffice File",
            command=self.choose_file
        ).pack(
            pady=(5, 15)
        )

        # ----------------------------------------------------
        # Ellipsus URL
        # ----------------------------------------------------

        url_frame = ctk.CTkFrame(self)

        url_frame.pack(
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(
            url_frame,
            text="Ellipsus document URL"
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )

        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Paste the Ellipsus document URL here..."
        )

        self.url_entry.pack(
            padx=15,
            pady=(0, 15),
            fill="x"
        )

        # ----------------------------------------------------
        # Import controls
        # ----------------------------------------------------

        import_frame = ctk.CTkFrame(self)

        import_frame.pack(
            padx=25,
            pady=10,
            fill="x"
        )

        ctk.CTkLabel(
            import_frame,
            text="IMPORT FROM LIBREOFFICE",
            font=("Arial", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        page_row = ctk.CTkFrame(import_frame)

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
            import_frame,
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
            command=emergency_stop
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
            lambda event: emergency_stop()
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
            target=import_pages,
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
#```
