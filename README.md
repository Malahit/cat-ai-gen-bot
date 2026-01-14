# 🐱 KittyKodakAI Bot v1.0

Telegram bot (@KittyKodakAI_bot) that generates AI cat images with freemium limits and TON payments.

## Features
- 🤖 `/start` - Welcome message with bot introduction
- 🎨 `/cat {prompt}` - Generate AI cat image (3 free/day/user, reset daily)
- 💎 `/pay` - Inline TON Connect buttons (0.5 TON/gen or 5 TON/month) with callback verification
- 📊 `/stats` - Shows current usage and Pro expiry
- ⚡ English-only interface, webhook-ready for Railway
- 🔒 Secure with aiohttp 3.13.3 (patches CVE vulnerabilities)

## Quick start
1) Create `.env` from template:
```
cp .env.example .env
```
Fill BOT_TOKEN, PERPLEXITY_KEY, TON_WALLET, REDIS_URL, WEBHOOK_BASE.

2) Install dependencies (Python 3.12):
```
pip install -r requirements.txt
```

3) Run locally (webhook):
```
python src/main.py
```

## Deployment (Railway)
- Uses `railway.toml` (NIXPACKS) and `Procfile` (`web: python src/main.py`)
- Automatic restart on failure with max 10 retries
- Set environment variables in Railway dashboard
- WEBHOOK_BASE should be your Railway domain (e.g., https://your-app.up.railway.app)

## Folder structure
```
src/
 ├── main.py          # aiogram dispatcher, webhook server
 ├── handlers.py      # /start, /cat, /pay, /stats
 ├── ai_generator.py  # Perplexity API call
 ├── ton_payments.py  # TON Connect helpers and checks
 └── database.py      # Redis limits and Pro status
requirements.txt
.env.example
railway.toml
Procfile
```

## Usage examples
- `/cat astronaut` → Cute astronaut cat 🚀
- `/cat vaporwave neon beach` → Vibrant neon cat 🌊
- `/pay` → TON payment options 💎
- `/stats` → Usage info and limits 📊

## Technologies
- **aiogram 3.13.1**: Modern Telegram Bot framework
- **Perplexity API**: AI-powered cat image generation
- **TON Blockchain**: Decentralized payment processing
- **Redis**: Session storage and rate limiting
- **Railway**: Cloud deployment platform

## License
MIT License - feel free to use this project for your own purposes.
