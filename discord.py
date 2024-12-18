import os
import discord
from discord import commands
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure bot
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SOUNDCLOUD_AUTH_TOKEN = os.getenv('SOUNDCLOUD_AUTH_TOKEN')  # This is your auth token from browser

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class SoundCloudAPI:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.base_url = "https://api.soundcloud.com"
        self.headers = {
            'Authorization': f'OAuth {auth_token}',
            'Content-Type': 'application/json',
        }

    def resolve_track_url(self, url):
        params = {
            'url': url,
            'client_id': self.get_client_id()
        }
        response = requests.get(f"{self.base_url}/resolve", params=params)
        return response.json()

    def repost_track(self, track_id):
        response = requests.put(
            f"{self.base_url}/users/soundcloud:users:YOUR_USER_ID/reposts/{track_id}",
            headers=self.headers
        )
        return response.status_code == 200

    def get_client_id(self):
        # You'll need to manually get this from the browser
        return "YOUR_CLIENT_ID"

# Initialize SoundCloud client
soundcloud_client = SoundCloudAPI(SOUNDCLOUD_AUTH_TOKEN)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if message is in the soundcloud-reposts channel
    if message.channel.name == 'soundcloud-reposts':
        # Check if message contains a SoundCloud URL
        if 'soundcloud.com' in message.content:
            try:
                # Extract the track URL
                track_url = [url for url in message.content.split() if 'soundcloud.com' in url][0]

                # Resolve the track URL
                track_info = soundcloud_client.resolve_track_url(track_url)
                
                if 'id' in track_info:
                    # Repost the track
                    success = soundcloud_client.repost_track(track_info['id'])
                    
                    if success:
                        await message.channel.send(f'Successfully reposted track: {track_url}')
                    else:
                        await message.channel.send(f'Failed to repost track: {track_url}')
                else:
                    await message.channel.send(f'Could not resolve track URL: {track_url}')

            except Exception as e:
                await message.channel.send(f'Error processing track: {str(e)}')

    await bot.process_commands(message)

# Run the bot
bot.run(DISCORD_TOKEN)