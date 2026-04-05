# UHAKIX — Voice Agent Skill
## OpenClaw Integration for Voice-Based Citizen Interaction

### Purpose
Enables UHAKIX agents to:
1. Receive voice notes from citizens (WhatsApp/Telegram)
2. Transcribe (Whisper large-v3): Swahili, English, Sheng
3. Process via NVIDIA AI agents
4. Respond with text AND/OR audio (MMS-TTS)

### How It Works
```
Citizen voice note (Telegram/WhatsApp)
   ↓
UHAKIX Voice Service:
   - Downloads audio file
   - Detects language (auto: Swahili/English)
   - Detects Sheng code-switching
   → Whispers transcribes
   → Sheng normalizes
   ↓
NVIDIA AI Agent (Nemotron-4 / Llama-3.1):
   → Processes question
   → Checks Constitution database
   → Checks Manipulation database
   → Generates response
   ↓
UHAKIX Voice Service:
   → MMS-TTS synthesizes Swahili audio
   → Sends audio response to citizen
```

### Model Specs
| Model | Task | Size | Speed | License |
|-------|------|------|-------|---------|
| openai/whisper-large-v3 | Speech-to-Text | 3.1GB | Fast (GPU), Medium (CPU) | MIT |
| facebook/mms-tts | Text-to-Speech | 300MB | Fast | CC BY-NC 4.0 |

### Sheng Glossary
Located at: `/root/.openclaw/workspace/side-projects/uhakix/data/sheng-glossary.csv`
30+ common terms mapped to standard Swahili/English.
Expand over time with more terms from beta users.

### API Endpoints
```
POST /api/v1/voice/transcribe  →  Audio → Transcribed text
POST /api/v1/voice/speak       →  Text → Audio response (WAV)
POST /api/v1/citizen/ask       →  Text/voice → Full UHAKIX response
```

### Integration Channels
| Channel | Voice Support | How |
|---------|--------------|-----|
| Telegram | ✅ Full | Voice notes → transcribe → respond with audio |
| WhatsApp | ✅ Full | Same as Telegram via Business API |
| Web | ✅ Partial | Microphone button → record → transcribe |
| USSD | ❌ No | Text-only menu-driven (future) |
