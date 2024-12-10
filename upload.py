import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import time
from pyrogram.errors.exceptions.flood_420 import FloodWait
from datetime import timedelta

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
# Store the current directory path for each channel
current_directory_paths = {}

# Constants for exponential backoff
INITIAL_WAIT_SECONDS = 5  # Initial wait time in seconds

def is_valid_file(filename):
    extensions = [
        ".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".csv", ".zip", ".rar",
        ".jpg", ".jpeg", ".png", ".gif", ".JPG", ".mov", ".mp4", ".avi", ".mkv",
        ".MOV", ".DNG", ".MP4", ".JPEG" , ".JPG" , ".mp3" , ".MP3"
    ]
    base_filename, extension = os.path.splitext(filename.lower())
    return (
        os.path.isfile(filename) 
        and extension in extensions 
        and (any(filename.endswith(ext) for ext in extensions) 
            or re.match(r"^\.zip\.00\d+$", base_filename))
    )

def get_directory_options(directory_path):
    # Get the list of subdirectories in the specified directory
    directories = [
        entry for entry in os.listdir(directory_path)
        if os.path.isdir(os.path.join(directory_path, entry))
    ]
    return directories

def get_back_button():
    return InlineKeyboardButton("⬅️ Back", callback_data="set_dir:..")

def get_file_size(file_path):
    return os.path.getsize(file_path)

def bytes_to_mb(size_bytes):
    return size_bytes / (1024 ** 2)

def bytes_to_mbps(size_bytes_per_sec):
    return (size_bytes_per_sec * 8) / (10 ** 6)

def bytes_to_gb(size_bytes):
    return size_bytes / (1024 ** 3)

def format_time(seconds):
    """Format time in seconds into hh:mm:ss."""
    return str(timedelta(seconds=seconds))

def format_speed(speed_bytes_per_sec):
    """Format speed in Mbps."""
    return f"{bytes_to_mbps(speed_bytes_per_sec):.2f} Mbps"

# Progress bar utility function
def update_progress(progress_text, current, total, uploaded_size, total_size, est_time_formatted, avg_speed):
    percentage = (current / total) * 100
    total_size_gb = bytes_to_gb(total_size)
    uploaded_size_gb = bytes_to_gb(uploaded_size)
    progress_text.edit_text(
        f"Files to Upload: {current}/{total} ({percentage:.1f}%)\n"
        f"Total Upload: {uploaded_size_gb:.2f} GB/{total_size_gb:.2f} GB\n"
        f"Est. time to upload: {est_time_formatted}\n"
        f"Avg. upload speed: {avg_speed}"
    )

def process_files(files, upload_function, message, file_type):
    global is_uploading
    total_files = len(files)
    count = 0
    total_size = sum(get_file_size(os.path.join(current_directory_paths[message.chat.id], file)) for file in files)
    uploaded_size = 0
    wait_seconds = INITIAL_WAIT_SECONDS

    # Initial progress message
    progress_text = message.reply_text(f"Uploading {file_type} progress: 0/0 (0.0%)")

    # Track upload times and speeds
    upload_times = []
    upload_speeds = []

    # Upload files in batches
    batch_size = 5  # Adjust batch size as needed
    for i in range(0, total_files, batch_size):
        batch = files[i:i + batch_size]

        for file in batch:
            # Check if uploading is canceled
            if not is_uploading:
                progress_text.edit_text("Uploading canceled!")
                return  # Exit the function if cancellation is requested

            file_path = os.path.join(current_directory_paths[message.chat.id], file)
            file_size = get_file_size(file_path)

            # Check if the file size is 0 bytes
            if file_size == 0:
                # Send a message with the file name and skip this file
                message.reply_text(f"Skipping file {file} because its size is 0 bytes.")
                continue

            start_time = time.time()

            try:
                # Upload the file
                upload_function(
                    chat_id=message.chat.id,
                    document=file_path
                )
                count += 1
                uploaded_size += file_size

                # Calculate upload speed
                upload_duration = time.time() - start_time
                upload_speed = file_size / upload_duration
                upload_speeds.append(upload_speed)
                avg_upload_speed = sum(upload_speeds) / len(upload_speeds)

                # Calculate estimated time
                remaining_files = total_files - count
                avg_upload_time = sum(upload_times) / len(upload_times) if upload_times else upload_duration
                est_time = avg_upload_time * remaining_files
                est_time_formatted = format_time(est_time)
                avg_speed_formatted = format_speed(avg_upload_speed)

                # Update progress
                update_progress(progress_text, count, total_files, uploaded_size, total_size, est_time_formatted, avg_speed_formatted)

                # Reset wait time after successful upload
                wait_seconds = INITIAL_WAIT_SECONDS

                # Add a 3-second interval between each file upload
                time.sleep(3)

            except FloodWait as e:
                wait_time = e.x  # Extract wait time from the exception

                # Send a message about the rate limit
                rate_limit_message = message.reply_text(f"Rate limited, waiting for {wait_time} seconds...")

                # Update the message with remaining time every 3 seconds
                for remaining in range(wait_time, 0, -3):
                    time.sleep(3)
                    rate_limit_message.edit_text(f"Rate limited, waiting for {remaining} seconds...")

                # Final wait
                time.sleep(wait_time % 3)  # Sleep for the remaining seconds if less than 3

                # Delete the rate limit message after waiting
                rate_limit_message.delete()

                wait_seconds = wait_time  # Update wait time for further use

        # Wait before processing the next batch
        time.sleep(2)


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
    global is_uploading
    is_uploading = True

    files = [
        entry for entry in os.listdir(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH))
        if is_valid_file(os.path.join(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH), entry))
    ]
    process_files(files, app.send_document, message, "documents")

    is_uploading = False
    message.reply_text("Documents uploaded successfully!")

# Handle the /image command
@app.on_message(filters.command("image"))
def send_images(client, message):
    global is_uploading
    is_uploading = True

    files = [
        entry for entry in os.listdir(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH))
        if is_valid_file(os.path.join(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH), entry))
    ]
    process_files(files, app.send_photo, message, "images")

    is_uploading = False
    message.reply_text("Images uploaded successfully!")

# Handle the /iad command
@app.on_message(filters.command("iad"))
def send_files_as_documents(client, message):
    global is_uploading
    is_uploading = True

    files = [
        entry for entry in os.listdir(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH))
        if is_valid_file(os.path.join(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH), entry))
    ]
    process_files(files, app.send_document, message, "files")

    is_uploading = False
    message.reply_text("Files uploaded as documents successfully!")

# Command to cancel ongoing file uploads
@app.on_message(filters.command("cancel"))
def cancel_upload(client, message):
    global is_uploading
    is_uploading = False
    message.reply_text("Uploading canceled successfully!")

# Command to set the current directory for uploading
@app.on_message(filters.command("setdir"))
def set_directory(client, message):
    directories = get_directory_options(current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH))
    buttons = [
        [InlineKeyboardButton(directory, callback_data=f"set_dir:{directory}")]
        for directory in directories
    ]
    if current_directory_paths.get(message.chat.id, DEFAULT_DIRECTORY_PATH) != DEFAULT_DIRECTORY_PATH:
        buttons.append([get_back_button()])
    reply_markup = InlineKeyboardMarkup(buttons)
    message.reply_text("Select a directory:", reply_markup=reply_markup)

# Callback function to handle directory selection
@app.on_callback_query(filters.regex(r"set_dir:(.*)"))
def change_directory(client, callback_query):
    global current_directory_paths
    directory = callback_query.matches[0].group(1)
    chat_id = callback_query.message.chat.id

    if directory == "..":
        current_directory_paths[chat_id] = os.path.dirname(current_directory_paths.get(chat_id, DEFAULT_DIRECTORY_PATH))
    else:
        current_directory_paths[chat_id] = os.path.join(current_directory_paths.get(chat_id, DEFAULT_DIRECTORY_PATH), directory)

    subdirectories = get_directory_options(current_directory_paths[chat_id])
    if subdirectories:
        buttons = [
            [InlineKeyboardButton(directory, callback_data=f"set_dir:{directory}")]
            for directory in subdirectories
        ]
        if current_directory_paths[chat_id] != DEFAULT_DIRECTORY_PATH:
            buttons.append([get_back_button()])
        reply_markup = InlineKeyboardMarkup(buttons)
        callback_query.message.edit_text(
            f"Current directory set to {current_directory_paths[chat_id]}. Select a subdirectory:",
            reply_markup=reply_markup
        )
    else:
        callback_query.message.edit_text(
            f"Current directory set to {current_directory_paths[chat_id]} ✅"
        )

# Run the client
app.run()
