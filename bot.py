"""Desicord — Pakistani-flavoured Discord fun bot.

Requires Python 3.10+, discord.py 2.x and a DISCORD_TOKEN environment variable.
"""
from __future__ import annotations

import logging
import os
import random
import re

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("desicord")

JOKES = [
    "Teacher: Homework kahan hai?\nStudent: Sir, Google Drive mein tha... Google ne hi delete kar diya! 😂",
    "Ammi: Phone side par rakho aur parhai karo.\nMe: Ammi, phone par hi PDF kholi hui hai.\nAmmi: To phir TikTok wali PDF band karo! 💀",
    "Friend: Bhai gym ja raha hai?\nMe: Haan, fridge tak. Wahan se wapas aana bhi cardio hai. 😭",
    "Abu: Bijli ka bill itna kyun aya?\nMe: Abu, fan bhi ghoomta hai aur meter bhi. Dono apna kaam kar rahe hain. 😂",
    "Pakistani ghar mein 'bas 5 minute' ka matlab hota hai: Allah hi jaane kitna time. ☕",
    "Teacher: Late kyun aaye?\nStudent: Sir, khwab mein school aa gaya tha. Uth kar laga attendance lag chuki hai. 😅",
    "Dost: Tera future bright hai.\nMe: Haan, bas present ka bulb fused hai. 💡",
    "Ammi: Mehmaan aa rahe hain, tameez se rehna.\nMe: Theek hai.\nAmmi: Aur Wi-Fi ka password kisi ko mat dena. 😂",
]

CHAI_LINES = [
    "Chai ready hai! ☕ Biscuit apna khud le kar aana, budget tight hai. 😂",
    "Pakistan mein chai sirf drink nahi, har maslay ka emergency solution hai. 🇵🇰",
    "Pehle chai, phir faisla. Warna faisla bhi neend mein ho sakta hai. 😴",
    "Ek cup chai aur thori si gossip — bas weekend complete. ☕",
]

ROASTS = [
    "Teri loading dekh kar 2G bhi apne aap ko fast samajhne laga. 💀",
    "Bhai tera plan itna secret hai ke tujhe khud bhi nahi pata. 😂",
    "Tu group ka notification hai: aata bohat hai, kaam kabhi kabhi. 😭",
    "Teri timing Pakistani traffic jaisi hai — prediction mushkil. 🚗",
    "Bhai tu legend hai... bas category abhi decide nahi hui. 🏆",
]

TRIVIA = [
    {"q": "Pakistan ka national animal kaunsa hai?", "a": ["markhor"]},
    {"q": "Pakistan ka national flower kaunsa hai?", "a": ["jasmine", "chambeli", "chameli"]},
    {"q": "Minar-e-Pakistan kis shehar mein hai?", "a": ["lahore"]},
    {"q": "Pakistan ka Independence Day kis date ko hota hai?", "a": ["14 august", "14th august", "14-august"]},
    {"q": "Cricket mein ek over mein kitni legal balls hoti hain?", "a": ["6", "six"]},
    {"q": "Pakistan ka capital city kya hai?", "a": ["islamabad"]},
]

# Games are per-user and per-server so members do not overwrite each other's games.
active_trivia: dict[tuple[int, int], dict[str, object]] = {}
active_guesses: dict[tuple[int, int], int] = {}


class Desicord(commands.Bot):
    async def setup_hook(self) -> None:
        try:
            synced = await self.tree.sync()
            log.info("Synced %s global application commands.", len(synced))
        except discord.HTTPException:
            log.exception("Could not sync application commands. Check bot permissions and connection.")


intents = discord.Intents.default()
bot = Desicord(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    if bot.user:
        log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)


@bot.tree.command(name="help", description="See Desicord's commands.")
async def help_command(interaction: discord.Interaction) -> None:
    embed = discord.Embed(title="Desicord 🇵🇰 — Command Guide",
                          description="A little desi masti for your server!",
                          color=discord.Color.green())
    embed.add_field(name="/joke", value="Get a Pakistani/desi joke.", inline=False)
    embed.add_field(name="/chai", value="Get a fresh cup of chai humour.", inline=False)
    embed.add_field(name="/roast [member]", value="Give someone a friendly, harmless roast.", inline=False)
    embed.add_field(name="/trivia", value="Start a Pakistan/general knowledge question.", inline=False)
    embed.add_field(name="/answer <answer>", value="Answer your active trivia question.", inline=False)
    embed.add_field(name="/guess_start", value="Start a number guessing game (1–10).", inline=False)
    embed.add_field(name="/guess <number>", value="Make a guess.", inline=False)
    embed.set_footer(text="Keep it friendly. Respect everyone in the server.")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="joke", description="Get a Pakistani-style desi joke.")
async def joke(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(random.choice(JOKES))


@bot.tree.command(name="chai", description="Serve a cup of Pakistani chai humour.")
async def chai(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(random.choice(CHAI_LINES))


@bot.tree.command(name="roast", description="Give a member a friendly, light-hearted roast.")
@app_commands.describe(member="Who should receive the friendly roast? Leave blank for yourself.")
async def roast(interaction: discord.Interaction, member: discord.Member | None = None) -> None:
    target = member or interaction.user
    await interaction.response.send_message(
        f"🔥 **{discord.utils.escape_markdown(target.display_name)}**, {random.choice(ROASTS)}"
    )


@bot.tree.command(name="trivia", description="Start a Pakistani/general knowledge trivia question.")
async def trivia(interaction: discord.Interaction) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("Trivia games work inside a server, yaar! 🇵🇰", ephemeral=True)
        return
    key = (interaction.guild_id, interaction.user.id)
    question = random.choice(TRIVIA)
    active_trivia[key] = question
    await interaction.response.send_message(
        f"🧠 **Desicord Trivia**\n{question['q']}\n\nUse /answer to submit your answer!"
    )


@bot.tree.command(name="answer", description="Submit your answer to your active trivia question.")
@app_commands.describe(answer="Your answer")
async def answer(interaction: discord.Interaction, answer: str) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("Use this game inside a server, yaar!", ephemeral=True)
        return
    key = (interaction.guild_id, interaction.user.id)
    question = active_trivia.get(key)
    if question is None:
        await interaction.response.send_message("Pehle /trivia se question start karo! 😄", ephemeral=True)
        return
    accepted = question["a"]
    normalised = re.sub(r"\s+", " ", answer.strip().casefold())
    if normalised in accepted:
        del active_trivia[key]
        await interaction.response.send_message(
            f"🎉 **Bilkul sahi!** The answer was **{accepted[0].title()}**. Shabash!"
        )
    else:
        await interaction.response.send_message("Not quite, yaar! Ek aur try karo. 😄", ephemeral=True)


@bot.tree.command(name="guess_start", description="Start a number guessing game from 1 to 10.")
async def guess_start(interaction: discord.Interaction) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("Use this game inside a server, yaar!", ephemeral=True)
        return
    key = (interaction.guild_id, interaction.user.id)
    active_guesses[key] = random.randint(1, 10)
    await interaction.response.send_message(
        "🎲 Main ne 1 se 10 ke darmiyan number soch liya hai. /guess se try karo!"
    )


@bot.tree.command(name="guess", description="Guess the number in your active game (1–10).")
@app_commands.describe(number="Enter a whole number from 1 to 10")
async def guess(interaction: discord.Interaction, number: app_commands.Range[int, 1, 10]) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("Use this game inside a server, yaar!", ephemeral=True)
        return
    key = (interaction.guild_id, interaction.user.id)
    answer_number = active_guesses.get(key)
    if answer_number is None:
        await interaction.response.send_message("Pehle /guess_start se game shuru karo! 🎲", ephemeral=True)
        return
    if number == answer_number:
        del active_guesses[key]
        await interaction.response.send_message(f"🎉 Wah ji wah! **{number}** bilkul sahi hai. You won!")
    elif number < answer_number:
        await interaction.response.send_message("Thora bara number try karo! ⬆️", ephemeral=True)
    else:
        await interaction.response.send_message("Thora chhota number try karo! ⬇️", ephemeral=True)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token or token == "your_bot_token_here":
        raise SystemExit("DISCORD_TOKEN is missing. Copy .env.example to .env and add your bot token.")
    bot.run(token)


if __name__ == "__main__":
    main()
