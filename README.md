# A simple Discord bot showing how to use GPT-4's [Vision](https://platform.openai.com/docs/guides/vision/vision) to understand videos

## Overview

This repository contains a simple Discord bot demonstrating the use of [GPT-4 Vision (GPT-4V)](https://platform.openai.com/docs/guides/vision) with the OpenAI API. It can process text, images, and videos (passing 25% of the frames from a video).

https://github.com/kesku/GPT-4V-Discord-Bot-Example/assets/62210496/058564a0-ef84-4483-af55-55df63dd5ecf

## Features

- Every message sent in the chat is passed to the OpenAI model,
- Handles image attachments in formats including PNG, JPG, JPEG, and WEBP.
- Processes video attachments, extracting frames from MP4, MOV, and WEBM files.
- Will never max out model token limit in a discord conversation, as messages are handled seperately from one another.

## Requirements

The following libraries and environments are required:

- Python 3.x
- [Nextcord](https://docs.nextcord.dev/en/stable/)
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [OpenCV (cv2)](https://github.com/opencv/opencv-python)
- [requests](https://github.com/psf/requests)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

## Installation

Follow these steps to set up the bot:

1. Clone or download the source code from the repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `env` file in the project's root directory with your Discord and OpenAI API keys:
   ```
   DISCORD_TOKEN=<your_discord_token>
   OPENAI_API_KEY=<your_openai_api_key>
   ```

## Usage

To use the bot:

1. Run the bot script from your command line:

   ```bash
   python gpt-4v-bot.py
   ```

2. In your Discord server, interact with the bot by sending text, images, or videos.

## Contributing

Contributions for improvements or new features are welcome. Please use the standard workflow of fork, branch, and pull request for contributions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- This bot was inspired by the [GPT-4 Developer Livestream](https://youtu.be/outcGtbnMuQ?t=478) Discord Bot example
- Special thanks for the resources like the OpenAI Cookbook, particularly the example on [GPT with Vision for Video Understanding](https://cookbook.openai.com/examples/gpt_with_vision_for_video_understanding) written by Kai Chen, which guided the development of video processing features in this bot.
