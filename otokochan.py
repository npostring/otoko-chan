import os
import discord
from discord import app_commands
from pathlib import Path
import toml
from otokochancore import OtokoChanCore


class OtokoChan(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.all()
client = OtokoChan(intents=intents)
occore = OtokoChanCore()


@client.tree.command(description='コード進行からMP3を出力します')
@app_commands.describe(
    chords='スペース区切りのコード進行(C F G Am...など)',
)
async def chord2mp3(interaction: discord.Interaction, chords: str):
    # コード進行を音声出力
    MIDI_PATH = str(TMP_DIR / f'{chords}.mid')
    MP3_PATH = str(TMP_DIR / f'{chords}.mp3')
    AUDIO_PATH = str(TMP_DIR / f'{chords}.wav')

    try:
        occore.create_text_to_midi(chords, MIDI_PATH)
        occore.create_midi_to_mp3(SOUNDFONT, MIDI_PATH, AUDIO_PATH)
        await interaction.response.send_message(file=discord.File(MP3_PATH))
    except ValueError as e:
        await interaction.response.send_message(f"`{', '.join([str(chord) for chord in e.args[0]])}`の書き方が間違ってるよ～。\n使える書き方はプロフのリンク先を見てね～。")
    finally:
        try:
            os.remove(MIDI_PATH)
            os.remove(MP3_PATH)
            os.remove(AUDIO_PATH)
        except FileNotFoundError:
            pass


@client.tree.command(description='コード進行からMIDIを出力します')
@app_commands.describe(
    chords='スペース区切りのコード進行(C F G Am...など)',
)
async def chord2mid(interaction: discord.Interaction, chords: str):
    # コード進行をMIDI出力
    MIDI_PATH = str(TMP_DIR / f'{chords}.mid')

    try:
        occore.create_text_to_midi(chords, MIDI_PATH)
        await interaction.response.send_message(file=discord.File(MIDI_PATH))
    except ValueError as e:
        await interaction.response.send_message(f"`{', '.join([str(chord) for chord in e.args[0]])}`の書き方が間違ってるよ～。\n使える書き方はプロフのリンク先を見てね～。")
    finally:
        try:
            os.remove(MIDI_PATH)
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    TMP_DIR = Path(os.path.dirname(__file__)) / 'tmp'
    ASSETS_DIR = Path(os.path.dirname(__file__)) / 'assets'

    with open(str(ASSETS_DIR / 'settings.toml'), 'r') as f:
        tomlobj = toml.load(f)
    TOKEN = tomlobj['token']
    MY_GUILD = discord.Object(tomlobj['guild'])
    SOUNDFONT = tomlobj['soundfont']

    client.run(TOKEN)
