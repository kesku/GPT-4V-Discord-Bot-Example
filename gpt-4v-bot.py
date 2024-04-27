import discord
from openai import OpenAI
import os
import cv2
import requests
from dotenv import load_dotenv
import base64

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
base64_prefix = "data:image/jpeg;base64,"


class Bot(discord.Client):
    async def on_ready(self):
        print(f"{self.user} is connected to Discord!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if not (
            self.user in message.mentions
            or (message.reference and message.reference.resolved.author == self.user)
        ):
            return

        content = [{"type": "text", "text": message.content}]

        if message.attachments:
            content = await self.handle_attachments(message, content)

        async with message.channel.typing():
            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=1000,
                )
                assistant_response = response.choices[0].message.content
                await message.channel.send(assistant_response)

            except Exception as e:
                await message.channel.send(f"An error occurred: {str(e)}")
                print(f"An error occurred: {str(e)}")

    async def handle_attachments(self, message, content):
        for attachment in message.attachments:
            if any(
                attachment.filename.lower().endswith(ext)
                for ext in [".png", ".jpg", ".jpeg", ".webp"]
            ):
                image_url = attachment.url
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            elif any(
                attachment.filename.lower().endswith(ext)
                for ext in [".mp4", ".mov", ".webm", ".gif", ".vgif"]
            ):
                await message.add_reaction("⏳")
                content = await self.handle_video_gif_attachments(attachment, content)
                await message.remove_reaction("⏳", self.user)
                await message.add_reaction("✅")

        return content

    async def handle_video_gif_attachments(self, attachment, content):
        is_video_or_gif = any(
            attachment.filename.lower().endswith(ext)
            for ext in [".mp4", ".mov", ".webm"]
        )
        print(
            f"Processing {attachment.filename}\n URL: {attachment.url}\n Type: {'video/gif' if is_video_or_gif else 'other'}"
        )
        video_url = attachment.url
        video_data = requests.get(video_url).content
        temp_video_path = "temp_video_scan.mp4"
        with open(temp_video_path, "wb") as scan_file:
            scan_file.write(video_data)
        video_stream = cv2.VideoCapture("temp_video_scan.mp4")
        fps = video_stream.get(cv2.CAP_PROP_FPS)
        print(f"Video FPS: {fps}")
        base64Frames = []
        while video_stream.isOpened():
            success, frame = video_stream.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        print(f"{len(base64Frames)} frames read.")
        video_stream.release()
        os.remove(temp_video_path)
        if is_video_or_gif:
            video_length = len(base64Frames) / fps
            percentage_to_process_map = {5: 100, 10: 50, 20: 25}
            percentage_to_process = next(
                (
                    value
                    for key, value in percentage_to_process_map.items()
                    if video_length < key
                ),
                25,
            )
            frames_to_process = len(base64Frames) * (percentage_to_process / 100)
            frame_interval = int(len(base64Frames) / frames_to_process)
            base64Frames = base64Frames[0::frame_interval]
        for x in base64Frames:
            base64_image_url = f"{base64_prefix}{x}"
            content.append(
                {"type": "image_url", "image_url": {"url": base64_image_url}}
            )
        return content


intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)
bot.run(DISCORD_TOKEN)
