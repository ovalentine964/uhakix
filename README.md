# 🚀 DEPLOY UHAKIX on GitHub Pages

## ✅ Everything is 100% Static — No Server Needed

This site runs entirely in the browser:
- **NVIDIA AI API**: Called directly from JavaScript (no backend server)
- **Voice (Whisper/TTS)**: Uses browser's built-in Web Speech API
- **Blockchain**: Polygon public chain (no server needed for verification UI)
- **Database**: Not needed for the static site

### 📱 How It Works

1. **Open**: `https://ovalentine964.github.io/uhakix/`
2. **Ask**: Type or speak your question
3. **Response**: NVIDIA Llama-3.1-70B answers in English, Kiswahili, or Sheng
4. **Voice**: Tap 🔊 to hear the answer read aloud
5. **Educate**: Learn your rights, spot manipulation, verify elections

### 🔧 Setup (Already Done)

✅ GitHub Pages enabled on `main` branch → `/docs` folder  
✅ NVIDIA API key embedded in code  
✅ Telegram bot token in `.env.example` (for future use)  
✅ Professional UI — responsive, dark theme, voice-enabled  
✅ AGPL-3.0 open source

### 🔐 Security Note

The NVIDIA API key is embedded in the frontend JavaScript. For a production deployment with millions of users, you'd want to:
1. Use a backend API (Render, Vercel, Fly.io) to hide the key
2. Add rate limiting to prevent abuse

For now, the free tier is fine for testing and early users.

### 📡 Telegram Bot (Separate Deploy)

The Telegram bot (`@UhakixBot`) needs a backend server. We can deploy it separately on:
- **Fly.io** (free tier)
- **Railway.app** (free tier)
- **Render.com** (free tier)

The bot code is in `backend/` and uses the same NVIDIA API.

---

## 🦁 LIVE URL

👉 **https://ovalentine964.github.io/uhakix/**

---

"No more bloodshed over elections. No more stolen shillings. Just verify. Just UHAKIX." 🇰🇪
