# 🚀 DEPLOY UHAKIX — Free, 24/7 Citizen Access Guide
## Deploy the platform for KES 0/month

---

## 🌐 HOW CITIZENS WILL ACCESS IT

### 1. Web Dashboard (Primary)
- **URL:** `https://uhakix.vercel.app` (or GitHub Pages)
- **Access:** Open any browser (Chrome, Safari, Firefox) on phone or computer
- **Features:** Full dashboard, chat with UHAKIX, voice input, civic education
- **Cost:** **FREE**

### 2. Telegram Bot (Voice + Text)
- **Action:** Open Telegram → Search `@UhakixBot` → Click "Start"
- **Features:** Text questions, send voice notes, get responses
- **Cost:** **FREE** (Telegram covers all costs)

### 3. WhatsApp (Coming Soon)
- **Action:** Text `+254 7XX XXX XXX`
- **Features:** Same as Telegram
- **Cost:** Free for citizens (you pay ~$0.005 per message via WhatsApp Business API)

---

## 🛠️ HOW TO DEPLOY FOR FREE (Step-by-Step)

### STEP 1: Deploy Frontend (Dashboard + Chat)
**Platform: Vercel (free forever, 100GB bandwidth/month)**

1. Go to [https://vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project" → Import your `uhakix` repo
4. Set Root Directory: `frontend`
5. Build Command: `npm install && npm run build`
6. Click "Deploy"

**Result:** `https://uhakix.vercel.app` — live in < 60 seconds!

---

### STEP 2: Deploy Backend (API + AI Agents)
**Platform: Render (free tier, 750 hours/month = always on)**

1. Go to [https://render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service" → Connect `uhakix` repo
4. Set Root Directory: `backend`
5. Install Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add Environment Variables:
   ```
   NVIDIA_API_KEY=nvapi-your-key-here
   TELEGRAM_BOT_TOKEN=8570592603:AAH8cj-HSRXWZZCJOvRPtM5vQmP0uwAlwCA
   DATABASE_URL=postgresql://user:pass@db-host/db
   ```

**Result:** `https://uhakix-api.onrender.com` — live in ~5 minutes!

---

### STEP 3: Set Up Free Database
**Platform: Neon (free PostgreSQL, 0.5GB storage)**

1. Go to [https://neon.tech](https://neon.tech)
2. Sign up with GitHub
3. Create new project → Get connection string
4. Copy the connection string → Update `.env` in Render

**Cost:** FREE forever (0.5GB = millions of records)

---

### STEP 4: Add Uptime Monitoring (Keeps It Awake 24/7)
**Platform: UptimeRobot (free, monitors every 5 minutes)**

1. Go to [https://uptimerobot.com](https://uptimerobot.com)
2. Sign up (free)
3. Add monitor → URL: `https://uhakix-api.onrender.com/api/v1/health`
4. Set interval: Every 5 minutes

**Result:** Render free tier sleeps after 15 minutes of inactivity. UptimeRobot pings it every 5 minutes → keeps it awake forever!

---

### STEP 5: Deploy Telegram Bot
**Cost: $0 forever**

The Telegram bot runs ON the same Render backend. Once deployed, citizens can:
1. Open Telegram → Search `@UhakixBot`
2. Click "Start"
3. They can text, send voice notes, upload photos (Form 34A), ask questions

---

## 📊 COMPLETE FREE STACK

| Component | Platform | Cost | 24/7? |
|-----------|----------|------|-------|
| Frontend | Vercel | FREE (100GB/mo) | ✅ Always on |
| Backend API | Render + UptimeRobot | FREE (750hrs) | ✅ Kept alive |
| Database | Neon | FREE (0.5GB) | ✅ Always on |
| Cache | Upstash | FREE (10k/day) | ✅ Always on |
| Graph DB | Neo4j Aura | FREE (50k nodes) | ✅ Always on |
| AI Models | NVIDIA API | Free credits | ✅ |
| Voice STT | Whisper (Open-Source) | $0 forever | ✅ |
| Voice TTS | MMS-TTS (Open-Source) | $0 forever | ✅ |
| Blockchain | Polygon (Public) | ~$0.01 deploy | ✅ Decentralized |
| Telegram Bot | Telegram | $0 forever | ✅ Always on |

**Total Monthly Cost: KES 0** 🇰🇪

---

## 🔗 CITIZEN ACCESS LINKS (After Deploy)

```
🌐 Web Dashboard:  https://uhakix.vercel.app
📱 Telegram Bot:    t.me/uhakixbot (create this in @BotFather)
📧 Contact:         Contact us on the dashboard
🗣️ Voice:           Available on all channels
```

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] 1. Deploy frontend to Vercel
- [ ] 2. Deploy backend to Render
- [ ] 3. Set up Neon database
- [ ] 4. Set Up UptimeRobot
- [ ] 5. Create @UhakixBot on Telegram (@BotFather)
- [ ] 6. Add Telegram token to Render `.env`
- [ ] 7. Test the dashboard
- [ ] 8. Test the Telegram bot
- [ ] 9. Share link everywhere!

## 📱 How Citizens Access (After Deploy)

**Phone (Android/Samsung/iPhone/Any):**
- Open browser → Go to `uhakix.vercel.app`
- Use it like a real app — it works like an app
- Add to Home Screen for instant access

**Phone (Feature Phone/Basic):**
- Wait for USSD (`*XXX#`) — coming in Phase 3

**WhatsApp:**
- Coming in Phase 2 (needs Business API setup)

**All channels support:**
- ✅ Text (English, Kiswahili, Sheng)
- ✅ Voice (send voice note → get voice response)
- ✅ Photos (upload Form 34A, project photos)
- ✅ Free, 24/7, no registration required

---

## 🦁 MISSION

Every Kenyan deserves to know where their money goes.
Every citizen deserves transparency.
Every vote deserves verification.

**UHAKIX makes this possible — at ZERO cost to citizens.** 🇰🇪
