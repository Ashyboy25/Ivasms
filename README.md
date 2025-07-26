# IVASMS Telegram Bot

A Telegram bot that monitors the IVASMS portal for new OTP messages and sends formatted alerts to your Telegram group.

## Features

- 🔄 Continuous monitoring of IVASMS portal
- 📱 Automatic OTP extraction from SMS messages
- 🎨 Beautiful formatted alerts for Telegram
- 🔐 Secure environment variable configuration
- 🚀 Ready for deployment on Render

## Quick Setup

### Local Development

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your actual values:
     ```
     BOT_TOKEN=your_telegram_bot_token
     CHAT_ID=your_telegram_chat_id
     IVASMS_EMAIL=avabuz@mailto.plus
     IVASMS_PASSWORD=avabuz@mailto.plus
     ```

4. **Run the bot:**
   ```bash
   python app.py
   ```

### Render Deployment

1. **Push to GitHub:**
   - Create a new GitHub repository
   - Push all files to your repository

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the configuration

3. **Set Environment Variables:**
   In your Render service settings, add these environment variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `CHAT_ID`: Your Telegram group/chat ID
   - `IVASMS_EMAIL`: avabuz@mailto.plus
   - `IVASMS_PASSWORD`: avabuz@mailto.plus

4. **Deploy!**
   Render will automatically build and deploy your bot.

## Getting Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided

## Getting Chat ID

1. Add your bot to your Telegram group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `chat` object and copy the `id` value

## Message Format

The bot sends beautifully formatted OTP alerts:

```
✨ Facebook OTP ALERT ✨

🕐 Time: 2025-07-26 14:30:15
📱 Number: 2250768427143
⚙️ Service: Facebook

🔑 OTP Code: 97029

# 97029 is your Facebook confirmation code

I'm Glad to Help You 😊
```

## Supported Services

The bot automatically detects OTPs from:
- WhatsApp
- Facebook
- Apple/iCloud
- Google/Gmail
- Telegram
- Microsoft
- Amazon
- Twitter
- Instagram
- Discord

## Troubleshooting

### Environment Variable Error
If you see "BOT_TOKEN environment variable is required":
- For local development: Create a `.env` file with your credentials
- For Render: Set environment variables in your service settings

### Chrome/Selenium Issues
The bot uses headless Chrome for web scraping. On Render, this is handled automatically by the Dockerfile.

### Login Issues
If the bot can't log in to IVASMS:
- Verify your email and password are correct
- Check if IVASMS has changed their login page structure

## Support

For issues or questions, please check the troubleshooting section above or review the code comments for technical details.

