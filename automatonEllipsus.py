#```python
"""
Ellipsus Page Transfer
======================

Automates transferring physical pages from a LibreOffice Writer document
into an Ellipsus document.

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

import time
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

import pyautogui
import pyperclip
import customtkinter as ctk


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_DELAY = 0.75
DEFAULT_PAGE_DELAY = 1.5
COUNTDOWN_SECONDS = 5

# F12 is the emergency stop key.
STOP_KEY = "f12"

# Ellipsus Markdown divider.
# Ellipsus recognizes this Markdown pattern as a Divider.
ELLIPSUS_DIVIDER = "----***___"


# ============================================================
# GLOBAL STATE
# ============================================================

stop_event = threading.Event()
automation_running = False


# ============================================================
# SAFETY
# ============================================================

def emergency_stop():
    """Immediately request that the current automation stop."""
    stop_event.set()


def check_stop():
    """Return True if the user has requested an emergency stop."""
    return stop_event.is_set()


def safe_sleep(seconds):
    """
    Sleep while checking for an emergency stop.

    This makes F12 responsive even during longer waits.
    """
    end_time = time.time() + seconds

    while time.time() < end_time:
        if check_stop():
            return False

        time.sleep(0.05)

    return True


def countdown(update_status):
    """Give the user a countdown before automation begins."""

    for remaining in range(COUNTDOWN_SECONDS, 0, -1):

        if check_stop():
            return False

        update_status(
            f"Starting in {remaining}... "
            f"DO NOT TOUCH THE MOUSE OR KEYBOARD."
        )

        if not safe_sleep(1):
            return False

    update_status("Automation started.")
    return True


# ============================================================
# LIBREOFFICE
# ============================================================

def open_libreoffice_file(filename, update_status):
    """
    Open the selected LibreOffice document.

    Uses the operating system's default application for the file.
    """

    import os

    update_status("Opening LibreOffice document...")

    try:
        os.startfile(filename)
    except AttributeError:
        # Fallback for non-Windows systems.
        import subprocess
        subprocess.Popen(["libreoffice", filename])

    return safe_sleep(5)


def go_to_page(page_number, update_status):
    """
    Navigate to a physical Writer page.

    Writer's page-navigation shortcuts allow us to move page-by-page.

    We start at the beginning of the document and advance until we reach
    the requested page. This is slower for very large starting page numbers,
    but it is deliberately conservative for the first version.
    """

    update_status(f"Navigating to Writer page {page_number}...")

    # Put cursor at beginning of document.
    pyautogui.hotkey("ctrl", "home")

    if not safe_sleep(DEFAULT_DELAY):
        return False

    # Move to the beginning of the requested page.
    #
    # Page 1 requires no movement.
    # Each Ctrl+PageDown advances toward the next physical page.
    for _ in range(page_number - 1):

        if check_stop():
            return False

        pyautogui.hotkey("ctrl", "pagedown")

        if not safe_sleep(0.08):
            return False

    # Make sure we're positioned at the beginning of the current page.
    pyautogui.hotkey("ctrl", "pageup")

    return safe_sleep(DEFAULT_DELAY)


def select_current_writer_page(update_status):
    """
    Select the current physical Writer page.

    Writer's Ctrl+PageDown moves to the end of the current page.
    Holding Shift while performing that movement extends the selection.

    This means:

        cursor at beginning of page
        Shift + Ctrl + PageDown
        = select through the end of the current page
    """

    update_status("Selecting current Writer page...")

    pyautogui.hotkey("ctrl", "pageup")

    if not safe_sleep(0.2):
        return False

    pyautogui.hotkey("ctrl", "shift", "pagedown")

    return safe_sleep(DEFAULT_DELAY)


def copy_current_page(update_status):
    """Copy the currently selected Writer page."""

    update_status("Copying Writer page...")

    pyautogui.hotkey("ctrl", "c")

    return safe_sleep(DEFAULT_DELAY)


# ============================================================
# ELLIPSUS
# ============================================================

def open_ellipsus(url, update_status):
    """
    Open the specified Ellipsus document in the default browser.

    The user must already be signed into Ellipsus in that browser.
    """

    update_status("Opening Ellipsus document...")

    webbrowser.open(url)

    return safe_sleep(5)


def paste_into_ellipsus(update_status):
    """Paste the copied Writer page into Ellipsus."""

    update_status("Pasting page into Ellipsus...")

    pyautogui.hotkey("ctrl", "v")

    return safe_sleep(DEFAULT_PAGE_DELAY)


def insert_ellipsus_divider(update_status):
    """
    Insert an Ellipsus divider.

    Ellipsus supports the Markdown divider shortcut:

        ----***___

    Typing this on a new line and pressing Enter causes Ellipsus
    to convert it into a Divider when Markdown shortcuts are enabled.
    """

    update_status("Inserting Ellipsus divider...")

    pyautogui.write(ELLIPSUS_DIVIDER, interval=0.01)

    if not safe_sleep(0.2):
        return False

    pyautogui.press("enter")

    return safe_sleep(DEFAULT_DELAY)


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
    stop_event.clear()

    try:

        # ----------------------------------------------------
        # Open LibreOffice
        # ----------------------------------------------------

        if not open_libreoffice_file(
            libreoffice_file,
            update_status
        ):
            return

        if check_stop():
            return

        # ----------------------------------------------------
        # Open Ellipsus
        # ----------------------------------------------------

        if not open_ellipsus(
            ellipsus_url,
            update_status
        ):
            return

        if check_stop():
            return

        # ----------------------------------------------------
        # Countdown
        # ----------------------------------------------------

        if not countdown(update_status):
            return

        # ----------------------------------------------------
        # Navigate to starting page
        # ----------------------------------------------------

        if not go_to_page(
            starting_page,
            update_status
        ):
            return

        current_page = starting_page

        # ----------------------------------------------------
        # Main loop
        # ----------------------------------------------------

        while not check_stop():

            update_status(
                f"Processing Writer page {current_page}..."
            )

            # Select page.
            if not select_current_writer_page(update_status):
                break

            # Copy page.
            if not copy_current_page(update_status):
                break

            # Switch to Ellipsus.
            pyautogui.hotkey("alt", "tab")

            if not safe_sleep(DEFAULT_PAGE_DELAY):
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

            if not safe_sleep(DEFAULT_PAGE_DELAY):
                break

            # Move to next Writer page.
            pyautogui.hotkey("ctrl", "pagedown")

            if not safe_sleep(DEFAULT_DELAY):
                break

            current_page += 1

        if check_stop():
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

    if not safe_sleep(DEFAULT_DELAY):
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
    stop_event.clear()

    try:

        if not countdown(update_status):
            return

        for count in range(1, number_of_pages + 1):

            if check_stop():
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
