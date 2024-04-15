import nextcord
from openai import OpenAI
import os
import cv2
import requests
from dotenv import load_dotenv
import base64

# Load environment variables from the .env file
load_dotenv()

# Load Discord token and OpenAI API key from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create an instance of the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
# Prefix for base64 encoded images
base64_prefix = "data:image/jpeg;base64,"


class Bot(nextcord.Client):
    async def on_ready(self):
        print(f"{self.user} is connected to Discord!")

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Check if the bot is mentioned or replied to
        if not (
            self.user in message.mentions
            or (message.reference and message.reference.resolved.author == self.user)
        ):
            return

        # Prepare the content for the API request
        content = [{"type": "text", "text": message.content}]

        # Handle image attachments if there are any
        if message.attachments:
            for attachment in message.attachments:
                # If the attachment is an image, add it to the content directly
                if any(
                    attachment.filename.lower().endswith(ext)
                    for ext in [".png", ".jpg", ".jpeg", ".webp"]
                ):
                    image_url = attachment.url
                    content.append(
                        {"type": "image_url", "image_url": {"url": image_url}}
                    )
                # If the attachment is a video, extract frames from it and add them to the content
                elif any(
                    attachment.filename.lower().endswith(ext)
                    for ext in [".mp4", ".mov", ".webm"]
                ):
                    type = "video"
                elif any(
                    attachment.filename.lower().endswith(ext)
                    for ext in [".gif", ".vgif"]
                ):
                    type = "gif"

                print(
                    f"Processing {attachment.filename}\n URL: {attachment.url}\n Type: {type}"
                )
                video_url = attachment.url
                video_data = requests.get(video_url).content
                temp_video_path = "temp_video_scan.mp4"
                with open(temp_video_path, "wb") as scan_file:
                    scan_file.write(video_data)
                video_stream = cv2.VideoCapture("temp_video_scan.mp4")
                fps = video_stream.get(cv2.CAP_PROP_FPS)
                print(f"Video FPS: {fps}")
                # List to store base64 encoded frames
                base64Frames = []
                # Read frames from the video file and encode them as base64
                while video_stream.isOpened():
                    success, frame = video_stream.read()
                    if not success:
                        # Stop if no frame is found
                        break
                    _, buffer = cv2.imencode(".jpg", frame)
                    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
                print(f"{len(base64Frames)} frames read.")
                video_stream.release()
                os.remove(temp_video_path)
                frame_limit = base64Frames
                if type == "video":
                    percentage_to_process = 50  # 25%
                    frames_to_process = len(base64Frames) * (
                        percentage_to_process / 100
                    )
                    frame_interval = int(len(base64Frames) / frames_to_process)
                    # Process a quarter of the frames
                    frame_limit = base64Frames[0::frame_interval]
                elif type == "gif":
                    # Usually need to limit number of processed frames for a GIF
                    frame_limit = base64Frames
                else:
                    frame_limit = base64Frames[0::25]
                for x in frame_limit:
                    base64_image_url = f"{base64_prefix}{x}"
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": base64_image_url},
                        }
                    )
        try:
            # Send the user message to the OpenAI API for completion
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": content}],
                max_tokens=1000,
            )
            # Get the response from the OpenAI API and send it back to the Discord channel
            assistant_response = response.choices[0].message.content
            await message.channel.send(assistant_response)

        except Exception as e:
            # Handle any errors that occur during the API request
            await message.channel.send(f"An error occurred: {str(e)}")
            print(f"An error occurred: {str(e)}")


# Create instance of the Discord bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)
# Run the Discord bot with provided token
bot.run(DISCORD_TOKEN)
