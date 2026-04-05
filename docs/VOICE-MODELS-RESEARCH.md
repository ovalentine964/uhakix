# UHAKIX — Voice Model Research Report
## Best Open-Source Voice Models for Kiswahili, Sheng, English

---

## 🗣️ SPEECH-TO-TEXT (Voice → Text)

### 1. openai/whisper-large-v3 ⭐ RECOMMENDED
| Property | Detail |
|----------|--------|
| **Type** | Open-source (weights available) |
| **Swahili Support** | ✅ Excellent — trained on massive multilingual dataset |
| **English Support** | ✅ Best in class |
| **Sheng Support** | ⚠️ Implicit — handles code-switching (Swahili↔English) well. No explicit Sheng training but captures mixed speech patterns |
| **Size** | ~3.1GB |
| **License** | MIT (free for commerical use) |
| **Why Best for UHAKIX** | • Handles Swahili+English code-switching seamlessly<br>• Zero-shot language detection (no need to specify)<br>• Works on CPU (slow) or GPU (fast)<br>• Open-source — no API costs<br>• Supports voice notes of any length |

### 2. openai/whisper-large-v3-turbo
| Property | Detail |
|----------|--------|
| **Advantage** | 3x faster than large-v3 with similar accuracy |
| **Size** | ~1.5GB (half the size) |
| **Trade-off** | Slightly less accurate on Swahili |
| **Recommendation** | Use for real-time USSD/WhatsApp where speed matters more |

### 3. Coqui/whisperXT
| Property | Detail |
|----------|--------|
| **Advantage** | Word-level timestamps, better punctuation |
| **Swahili** | Same as Whisper (same base model) |
| **Recommendation** | Use if we need word-level timing (e.g., karaoke-style subtitles) |

---

## 📢 TEXT-TO-SPEECH (Text → Voice Response)

### 1. facebook/mms-tts (Massively Multilingual Speech) ⭐ RECOMMENDED
| Property | Detail |
|----------|--------|
| **Type** | Open-source |
| **Swahili Support** | ✅ Yes — ISO 639-3 code: `swh` |
| **Sheng Support** | ❌ Not explicitly trained, but can approximate |
| **Languages** | 1000+ languages |
| **License** | CC BY-NC 4.0 (free for non-commercial, needs license for commercial) |
| **Quality** | Natural-sounding, not robotic |

### 2. Coqui/TTS (VITS models)
| Property | Detail |
|----------|--------|
| **Type** | Open-source |
| **Swahili Models** | Community-trained VITS Swahili checkpoint available |
| **Quality** | Better than MMS for languages with community models |
| **Recommendation** | Find best community Swahili model |

### 3. Piper TTS
| Property | Detail |
|----------|--------|
| **Type** | Open-source, optimized for CPU |
| **Speed** | Real-time on CPU (very fast) |
| **Swahili** | ❌ No official Swahili model yet |
| **Recommendation** | Best for English responses if we can fine-tune on Swahili |

---

## 🎯 FINAL RECOMMENDATION FOR UHAKIX

### Speech-to-Text Pipeline:
```
Citizen voice note (WhatsApp/Telegram)
   ↓
whisper-large-v3 (open-source, MIT license)
   ↓
Output Text: "Nataka kujua pesa za kaunti zinaenda wapi"
   ↓
SHENG PREPROCESSING (custom layer):
   → Normalizes common Sheng terms → Standard Swahili/English
   → e.g. "pesa" → "money/funds", "ni" → "is/are"
   ↓
NVIDIA LLM processes the normalized text
```

### Text-to-Speech Pipeline:
```
NVIDIA LLM generates response
   ↓
MMS-TTS (Swahili checkpoint) converts text → audio
   ↓
Citizen receives voice response on WhatsApp/Telegram
```

### Sheng Handling Strategy:
Since no open-source model explicitly handles Sheng:

1. **Build a Sheng Glossary** — 1000+ common Sheng terms mapped to Swahili/English
   - "Form ni gani?" → "How are you doing?"
   - "Sema ukweli" → "Tell the truth"
   - "Pesa imeenda wapi?" → "Where did the money go?"
   - "Wakubwa wanafanya hii" → "The politicians are doing this"

2. **Use Whisper large-v3-turbo** for real-time — it handles code-switching naturally
3. **Fine-tune Whisper on Kenyan Sheng** over time (collect voice data from beta users)

---

## 📊 COMPARISON: All Open-Source Voice Models

| Model | STT/TTS | Swahili | Sheng | English | Size | Speed | License |
|-------|---------|---------|-------|---------|------|-------|---------|
| Whisper large-v3 | STT | ✅ Excellent | ⚠️ Code-switching | ✅ Best | 3.1GB | Fast | MIT |
| Whisper large-v3-turbo | STT | ✅ Good | ⚠️ Code-switching | ✅ Best | 1.5GB | Very Fast | MIT |
| MMS-TTS | TTS | ✅ Available | ❌ No | ✅ Good | 300MB | Medium | CC BY-NC |
| Coqui VITS Swahili | TTS | ⚠️ Community | ❌ No | ❌ No | 100MB | Fast | MIT |
| Piper TTS | TTS | ❌ No | ❌ No | ✅ Excellent | 50MB | Very Fast | MIT |

---

## 💰 COST COMPARISON

| Approach | Cost | Pros | Cons |
|----------|------|------|------|
| **Open-Source Whisper + MMS** | **$0 FOREVER** | No API costs, works offline, unlimited usage | Needs GPU server ($20-50/month for GPU hosting) |
| **NVIDIA NIM Audio API** | ~$0.006/minute | Highest quality, no infrastructure | Ongoing cost at scale |
| **OpenAI Whisper API** | ~$0.006/minute | Same quality, hosted | Ongoing cost, closed source |

**Recommendation: Self-host Whisper + MMS on a GPU server ($20-50/month)**
- Unlimited voice processing
- No per-message costs
- Works even if APIs go down
- Critical for election day reliability
