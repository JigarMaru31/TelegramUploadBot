import os
from pyrogram import Client, filters
import pyrogram
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time 

# Replace with your own API ID, API HASH, and bot token
API_ID = #Your API_ID
API_HASH = "Your API_HASH"
BOT_TOKEN = "Your BOT_TOKEN"

# Create a Pyrogram client instance
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Variable to track the cancellation status
is_uploading = False

# Default directory path
DEFAULT_DIRECTORY_PATH = "./"
# Variable to store the current directory path
current_directory_path = DEFAULT_DIRECTORY_PATH

# Global list to store upload tasks
upload_tasks = []

# Constants for exponential backoff
INITIAL_WAIT_SECONDS = 5  # Initial wait time in seconds
MAX_WAIT_SECONDS = 300  # Maximum wait time in seconds

def is_valid_file(filename):
    extensions = [
        ".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".csv", ".zip", ".rar",
        ".jpg", ".jpeg", ".png", ".gif", ".JPG", ".mov", ".mp4", ".avi", ".mkv",
        ".MOV", ".DNG", ".MP4"
    ]
    return os.path.isfile(filename) and any(filename.endswith(ext) for ext in extensions)


def get_directory_options():
    # Get the list of subdirectories in the current directory
    directories = [
        entry for entry in os.listdir(current_directory_path)
        if os.path.isdir(os.path.join(current_directory_path, entry))
    ]
    return directories


def get_back_button():
    return InlineKeyboardButton("⬅️ Back", callback_data="set_dir:..")


# Progress bar utility function
def update_progress(progress_text, current, total):
    progress = current / total * 100
    progress_text.edit_text(f"Uploading progress: {current}/{total} ({progress:.1f}%)")


# Handle the /start command
@app.on_message(filters.command("start"))
def start_command(client, message):
    start_msg = (
        "Welcome! I am a file uploader bot.\n\n"
        "Use the following commands to upload files:\n"
        "/doc - Upload documents\n"
        "/image - Upload images\n"
        "/iad - Upload files as documents\n"
        "/setdir - Set the current directory\n"
        "/cancel - Cancel ongoing file uploads"
    )
    message.reply_text(start_msg)


# Handle the /doc command
@app.on_message(filters.command("doc"))
def send_documents(client, message):
    # Set the uploading status to True
    global is_uploading
    is_uploading = True

    # Scan the directory for files with the specified extension
    files = [
        entry for entry in os.listdir(current_directory_path)
        if is_valid_file(os.path.join(current_directory_path, entry))
    ]

    total_files = len(files)
    count = 0
    wait_seconds = INITIAL_WAIT_SECONDS

    progress_text = message.reply_text("Uploading progress: 0/0 (0.0%)")

    # Upload each file as a document, including video files
    for file in files:
        # Check if uploading is canceled
        if not is_uploading:
            break

        try:
            app.send_document(
                chat_id=message.chat.id,
                document=os.path.join(current_directory_path, file)
            )
            count += 1
            update_progress(progress_text, count, total_files)
            wait_seconds = INITIAL_WAIT_SECONDS  # Reset backoff upon successful upload

        except pyrogram.errors.exceptions.flood_420.FloodWait as e:
            print(f"Rate limited, waiting for {wait_seconds} seconds...")
            time.sleep(wait_seconds)
            wait_seconds = min(2 * wait_seconds, MAX_WAIT_SECONDS)  # Exponential backoff

    # Reset the uploading status
    is_uploading = False

    progress_text.edit_text("Documents uploaded successfully!")


# Handle the /image command
@app.on_message(filters.command("image"))
def send_images(client, message):
    # Set the uploading status to True
    global is_uploading
    is_uploading = True

    # Scan the directory for files with the specified extension
    files = [
        entry for entry in os.listdir(current_directory_path)
        if is_valid_file(os.path.join(current_directory_path, entry))
    ]

    total_files = len(files)
    count = 0
    wait_seconds = INITIAL_WAIT_SECONDS

    progress_text = message.reply_text("Uploading progress: 0/0 (0.0%)")

    # Upload each file as a photo
    for file in files:
        # Check if uploading is canceled
        if not is_uploading:
            break

        try:
            app.send_photo(
                chat_id=message.chat.id,
                photo=os.path.join(current_directory_path, file)
            )
            count += 1
            update_progress(progress_text, count, total_files)
            wait_seconds = INITIAL_WAIT_SECONDS  # Reset backoff upon successful upload

        except pyrogram.errors.exceptions.flood_420.FloodWait as e:
            print(f"Rate limited, waiting for {wait_seconds} seconds...")
            time.sleep(wait_seconds)
            wait_seconds = min(2 * wait_seconds, MAX_WAIT_SECONDS)  # Exponential backoff

    # Reset the uploading status
    is_uploading = False

    progress_text.edit_text("Images uploaded successfully!")

# Handle the /iad command
@app.on_message(filters.command("iad"))
def send_files_as_documents(client, message):
    # Set the uploading status to True
    global is_uploading
    is_uploading = True

    # Scan the directory for all files
    files = [
        entry for entry in os.listdir(current_directory_path)
        if is_valid_file(os.path.join(current_directory_path, entry))
    ]

    total_files = len(files)
    count = 0
    wait_seconds = INITIAL_WAIT_SECONDS

    progress_text = message.reply_text("Uploading progress: 0/0 (0.0%)")

    # Upload each file as a document
    for file in files:
        # Check if uploading is canceled
        if not is_uploading:
            break

        try:
            app.send_document(
                chat_id=message.chat.id,
                document=os.path.join(current_directory_path, file)
            )
            count += 1
            update_progress(progress_text, count, total_files)
            wait_seconds = INITIAL_WAIT_SECONDS  # Reset backoff upon successful upload

        except pyrogram.errors.exceptions.flood_420.FloodWait as e:
            print(f"Rate limited, waiting for {wait_seconds} seconds...")
            time.sleep(wait_seconds)
            wait_seconds = min(2 * wait_seconds, MAX_WAIT_SECONDS)  # Exponential backoff

    # Reset the uploading status
    is_uploading = False

    progress_text.edit_text("Files uploaded as documents successfully!")


# Handle the /cancel command
@app.on_message(filters.command("cancel"))
def cancel_upload(client, message):
    # Set the uploading status to False
    global is_uploading
    is_uploading = False

    message.reply_text("Uploading canceled successfully!")


# Handle the /setdir command
@app.on_message(filters.command("setdir"))
def set_directory(client, message):
    directories = get_directory_options()
    buttons = [
        [InlineKeyboardButton(directory, callback_data=f"set_dir:{directory}")]
        for directory in directories
    ]
    if current_directory_path != DEFAULT_DIRECTORY_PATH:
        buttons.append([get_back_button()])
    reply_markup = InlineKeyboardMarkup(buttons)
    message.reply_text("Select a directory:", reply_markup=reply_markup)


# Handle the directory selection callback
@app.on_callback_query(filters.regex(r"set_dir:(.*)"))
def change_directory(client, callback_query):
    global current_directory_path
    directory = callback_query.matches[0].group(1)

    if directory == "..":
        # Go to the parent directory
        current_directory_path = os.path.dirname(current_directory_path)
    else:
        # Enter the selected subdirectory
        current_directory_path = os.path.join(current_directory_path, directory)

    # Check if the selected directory contains subdirectories
    subdirectories = get_directory_options()
    if subdirectories:
        buttons = [
            [InlineKeyboardButton(directory, callback_data=f"set_dir:{directory}")]
            for directory in subdirectories
        ]
        if current_directory_path != DEFAULT_DIRECTORY_PATH:
            buttons.append([get_back_button()])
        reply_markup = InlineKeyboardMarkup(buttons)
        callback_query.message.edit_text(
            f"Current directory set to `{current_directory_path}`. Select a subdirectory:",
            reply_markup=reply_markup
        )
    else:
        callback_query.message.edit_text(
            f"Current directory set to `{current_directory_path}` ✅"
        )


# Run the client
app.run()
