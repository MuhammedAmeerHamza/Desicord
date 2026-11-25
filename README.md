# Desicord 🇵🇰

A Pakistani-style Discord entertainment bot with desi jokes, chai humour, friendly roasts, Urdu/Roman Urdu responses, trivia and a number-guessing game.

## Features (v0.1.0)

- `/joke` — Pakistani/desi jokes (Roman Urdu and English).
- `/chai` — a fresh chai-themed response.
- `/roast` — friendly, light-hearted roasts (never intended to target protected traits).
- `/trivia` and `/answer` — Pakistani/general knowledge trivia.
- `/guess_start` and `/guess` — a number-guessing mini-game.
- `/help` — command guide.

## Requirements

- Python 3.10 or newer
- A Discord application and bot token

## Setup

1. Create an application at https://discord.com/developers/applications.
2. Under **Bot**, create/reset the bot token. Keep it private.
3. Under **OAuth2 → URL Generator**, select `bot` and `applications.commands`. Give it the permissions to send messages and use application commands. Open the generated URL to invite it to your server.
4. Download/clone this repository.
5. Install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\\Scripts\\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env` and add your bot token:

   ```env
   DISCORD_TOKEN=put_your_bot_token_here
   ```

7. Start the bot:

   ```bash
   python bot.py
   ```

The bot syncs global slash commands on startup. Discord may take some time to display global commands after the first sync.

## Security

- Never share your bot token or commit `.env`.
- If a token is exposed, reset it immediately in the Discord Developer Portal.
- Do not enable privileged intents unless a future feature actually requires them.

## Project status

**v0.1.0 — foundation and first entertainment commands.** This is an initial release candidate; test it in a private server before inviting a larger community.

## License

MIT — see [LICENSE](LICENSE).
