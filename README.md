# 🐱 Cat AI Generator Bot

A Telegram bot that generates unique AI cat images using Perplexity API with TON blockchain payments.

## Features

- 🤖 **AI-Powered Generation**: Uses Perplexity API to generate creative cat descriptions
- 💎 **TON Payments**: Secure payment processing via TON blockchain
- ⚡ **Fast & Reliable**: Built with aiogram 3.x for optimal performance
- 🚀 **Railway Deployment**: Easy deployment configuration included

## Project Structure

```
cat-ai-gen-bot/
├── src/
│   ├── bot.py          # Aiogram handlers and bot logic
│   ├── ai_gen.py       # Perplexity API integration
│   └── ton_pay.py      # TON blockchain payments
├── requirements.txt    # Python dependencies
├── railway.toml        # Railway deployment config
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Malahit/cat-ai-gen-bot.git
cd cat-ai-gen-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `BOT_TOKEN`: Your Telegram bot token from [@BotFather](https://t.me/botfather)
- `PERPLEXITY_API_KEY`: Your Perplexity API key
- `TON_WALLET_ADDRESS`: Your TON wallet address for receiving payments
- `PAYMENT_AMOUNT`: Price per image generation (default: 1.0 TON)

### 4. Run the bot

```bash
python src/bot.py
```

## Usage

1. Start the bot: `/start`
2. Generate a cat image: `/generate`
3. Pay with TON using the provided payment link
4. Check payment status to receive your AI-generated cat image

## TON Payment

Send payment to the following wallet:

**TON Wallet Address**: `EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c`

### Payment QR Code

```
█████████████████████████████████████
█████████████████████████████████████
████ ▄▄▄▄▄ █▀ █▀▀██▀█▀▀▄█ ▄▄▄▄▄ ████
████ █   █ █▀ █ ▄▄▀ ▀ ▀▄█ █   █ ████
████ █▄▄▄█ █▀█  ██▀▄█▀ ▄█ █▄▄▄█ ████
████▄▄▄▄▄▄▄█▄▀ ▀▄█ █▄▀ █▄▄▄▄▄▄▄▄████
████▄▄  ▀ ▄ ▄▀▄ ▀▄▄█▄█▀▀▀▄█▄▀▀▄▀████
████▄ █▀█▀▄▀▀▄▀▀ ▄▄ ▀▄▀▀▀  ██▀▄ ████
█████▄  ▄ ▄█▀ ██▀▄▄▀▀▀█▄▀▀ ▀▄▀ ▀████
████ ██▀  ▄▀▄██▀ ▄▀▀█▀  ▀▄█▄▀   ████
████▀ ▀▀▀ ▄  ▄▀▄█▄▄  ▀ █▄ ██▀▀▄▀████
████ █▄█ ▀▄█▀ ██ ▄▀ █▀▀▀  ▀▄  ▄ ████
████▄███▄▄▄█ ▄▀▀▄▄▄▀▀█ ▄▄▄ ▀   ▀████
████ ▄▄▄▄▄ █▄▄  █▀▄▀▀  █▄█ ██▄▀ ████
████ █   █ █  ██▀ ▄▀▀█ ▄▄▄▄▀ ▄▀▀████
████ █▄▄▄█ █ ▄▀█▄▄▄▄▀  ▀▀▀▀▀█ ▀ ████
████▄▄▄▄▄▄▄█▄▄███▄█▄██▄█▄▄██▄██▄████
█████████████████████████████████████
█████████████████████████████████████
```

Scan with TON wallet app or use: `ton://transfer/EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c`

## Deployment

### Railway

1. Fork this repository
2. Connect your Railway account to GitHub
3. Create a new project from your fork
4. Add environment variables in Railway dashboard
5. Deploy! Railway will automatically use `railway.toml` configuration

### Manual Deployment

The bot can run on any platform that supports Python:
- VPS (DigitalOcean, Linode, etc.)
- Cloud platforms (AWS, GCP, Azure)
- Container platforms (Docker, Kubernetes)

## Commands

- `/start` - Start the bot and see welcome message
- `/generate` - Generate a new AI cat image (requires payment)
- `/help` - Show help information

## Technologies

- **aiogram 3.4.1**: Modern Telegram Bot framework
- **Perplexity API**: AI-powered content generation
- **TON Blockchain**: Decentralized payment processing
- **Railway**: Deployment platform

## Demo

Try the bot: [@CatAIGenBot](https://t.me/CatAIGenBot) *(example link)*

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues and questions, please open an issue on GitHub.

---

Made with 🐱 and ❤️