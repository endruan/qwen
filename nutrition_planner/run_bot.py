"""
Run the Nutrition Planner Telegram Bot.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.telegram_bot import run_bot

if __name__ == "__main__":
    # Replace with your actual Telegram bot token
    # Get token from @BotFather on Telegram
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❗ Please set your Telegram bot token in run_bot.py")
        print("Get a token from @BotFather on Telegram")
        print("\nTo create a bot:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot command")
        print("3. Follow the instructions")
        print("4. Copy the token and paste it in run_bot.py")
        sys.exit(1)
    
    print("🤖 Starting Nutrition Planner Telegram Bot...")
    print("Press Ctrl+C to stop the bot\n")
    
    try:
        asyncio.run(run_bot(BOT_TOKEN))
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
