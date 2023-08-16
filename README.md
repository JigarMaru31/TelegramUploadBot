# TelegramUploadBot

# File Uploader Bot

This repository contains a simple Python bot script that enables you to upload documents, images, and files as documents to a Telegram chat using the Pyrogram library. The bot provides various commands to handle different types of file uploads and allows you to navigate through directories to select files for uploading.

## Requirements

- Python 3.7 or higher
- [Pyrogram](https://docs.pyrogram.org/intro/setup#installing-pyrogram)

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/JigarMaru31/TelegramUploadBot.git
   cd your-repo
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```
3. Replace the following placeholders in the script with your own values:

   `API_ID`: Your Telegram API ID
   `API_HASH`: Your Telegram API hash
   `BOT_TOKEN`: Your bot's token

## Usage

1. Run the script:
```
   python script.py
```
2. Start a chat with your bot on Telegram.

Use the following commands to interact with the bot:

```
/start: Displays the welcome message and available commands.
/doc: Uploads documents from the specified directory.
/image: Uploads images from the specified directory.
/iad: Uploads files as documents from the specified directory.
/setdir: Sets the current directory for uploading.
/cancel: Cancels ongoing file uploads.
```

## How It Works
The bot uses the Pyrogram library to interact with the Telegram API. It provides commands to upload documents, images, and files as documents. The script allows you to navigate through directories to select files for uploading. It also includes a progress bar to show the upload progress.

When you run the script and start a chat with the bot, you can use the commands mentioned above to perform various file upload actions.

## Note
This script is a basic example and may require further customization and error handling for production use.
Be cautious when handling user data and tokens. Keep your API credentials and bot token secure.
The exponential backoff mechanism is used to handle rate limiting issues during file uploads.
License
This project is licensed under the MIT License.
