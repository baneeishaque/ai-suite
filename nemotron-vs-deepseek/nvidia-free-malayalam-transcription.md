# NVIDIA Build Free Models: Malayalam Audio Transcription Analysis

**Task:** Transcribe Malayalam meeting recordings  
**Date:** June 29, 2026  
**Source:** [build.nvidia.com free models](https://build.nvidia.com/models?filters=nimType%3Anim_type_preview) - 144 free models total

---

## Free Models with Audio Support

All models below are **FREE** on the free tier (no credits consumed):

| # | Model | Provider | Audio | Malayalam | Notes |
|---|-------|----------|-------|-----------|-------|
| 1 | `whisper-large-v3` | OpenAI | ✓ | ✅ | Dedicated ASR, 99 languages |
| 2 | `gemma-3n-e4b-it` | Google | ✓ | ✅ | 140+ languages, 30-sec chunks |
| 3 | `gemma-3n-e2b-it` | Google | ✓ | ✅ | 140+ languages, smaller |
| 4 | `kimi-k2.6` | Moonshot | ✓ | ❓ | Coding focus, unknown Malayalam |
| 5 | `nemotron-3-nano-omni` | NVIDIA | ✓ | ❌ | English-only |
| 6 | `phi-4-multimodal-instruct` | Microsoft | ✓ | ❌ | 8 languages only |

---

## Detailed Analysis

### 1. whisper-large-v3 (OpenAI) ⭐ BEST FOR MALAYALAM

| Aspect | Details |
|--------|---------|
| Type | Dedicated ASR (Speech-to-Text) |
| Parameters | 1.5B |
| Languages | **99 languages including Malayalam** |
| Audio Format | WAV, MP3, FLAC, M4A |
| Max Audio | Varies (typically 30 min - 1 hour) |
| Features | Translation, word timestamps |
| Free | ✅ YES |

**Why Best:**
- Purpose-built for speech recognition
- Explicitly supports Malayalam (ml)
- Word-level timestamps available
- High accuracy for transcription

**Limitation:** Batch processing only (not streaming)

---

### 2. gemma-3n-e4b-it (Google) ⭐ BEST MULTIMODAL

| Aspect | Details |
|--------|---------|
| Type | Multimodal LLM |
| Parameters | 5B total / ~2B effective |
| Languages | **140+ spoken languages** |
| Audio Format | WAV, MP3, FLAC (single channel) |
| Max Audio | **30 seconds per clip** |
| Context | 32K tokens |
| Free | ✅ YES |

**Why Good:**
- Only model with 140+ language support
- Can process audio, video, image, text
- Edge-optimized = fast inference

**Limitation:** 30-second audio chunks. Longer recordings need splitting.

---

### 3. gemma-3n-e2b-it (Google)

| Aspect | Details |
|--------|---------|
| Type | Multimodal LLM |
| Parameters | 2B effective |
| Languages | 140+ (same as E4B) |
| Max Audio | 30 seconds |
| Free | ✅ YES |

**Verdict:** Same language support as E4B but **less capable**. Use E4B instead.

---

### 4. kimi-k2.6 (Moonshot)

| Aspect | Details |
|--------|---------|
| Type | Multimodal LLM |
| Parameters | 1T total |
| Audio Support | ✓ |
| Malayalam | ❓ Unknown |
| Focus | Coding, agentic tasks |
| Free | ✅ YES |

**Verdict:** Primarily a **coding model**. Audio is secondary. Unlikely to be good at Malayalam transcription.

---

### 5. nemotron-3-nano-omni-30b-a3b-reasoning (NVIDIA)

| Aspect | Details |
|--------|---------|
| Type | Multimodal LLM |
| Parameters | 30B / 3B active |
| Audio Support | ✓ Speech |
| Malayalam | ❌ English-only |
| Free | ✅ YES |

**Verdict:** Best architecture but **English-only**. Won't work for Malayalam.

---

### 6. phi-4-multimodal-instruct (Microsoft)

| Aspect | Details |
|--------|---------|
| Type | Multimodal LLM |
| Parameters | 14B |
| Audio Languages | English, Chinese, German, French, Italian, Japanese, Spanish, Portuguese |
| Malayalam | ❌ Not supported |
| Free | ✅ YES |

**Verdict:** **Malayalam not in list**. Won't work.

---

## Free ASR Models (Speech-to-Text)

| Model | Languages | Malayalam | Free |
|-------|-----------|-----------|------|
| `whisper-large-v3` | 99 | ✅ | ✅ |
| `canary-1b-asr` | 25 European | ❌ | ✅ |
| `parakeet-1.1b-rnnt-multilingual-asr` | 25 (Indic: Hindi, Tamil, Bengali) | ❌ | ✅ |
| `nemotron-asr-streaming` | English | ❌ | ✅ |
| `parakeet-ctc-0.6b-asr` | English | ❌ | ✅ |
| `parakeet-ctc-0.6b-es` | Spanish-English | ❌ | ✅ |
| `parakeet-ctc-0.6b-vi` | Vietnamese-English | ❌ | ✅ |
| `parakeet-ctc-0.6b-zh-cn` | Mandarin-English | ❌ | ✅ |
| `parakeet-ctc-0.6b-zh-tw` | Mandarin Taiwanese-English | ❌ | ✅ |
| `parakeet-ctc-1.1b-asr` | English | ❌ | ✅ |
| `parakeet-tdt-0.6b-v2` | English | ❌ | ✅ |

---

## Recommendation

### Primary Choice: `whisper-large-v3`

**Why:**
1. **Dedicated ASR** - purpose-built for speech recognition
2. **99 languages** including Malayalam
3. **High accuracy** for transcription
4. **Word-level timestamps** available
5. **FREE** on the free tier

**How to use:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-nvidia-api-key"
)

# Transcribe Malayalam audio
response = client.audio.transcriptions.create(
    model="openai/whisper-large-v3",
    file=open("meeting.wav", "rb"),
    language="ml"  # Malayalam
)

print(response.text)
```

---

### Alternative: `gemma-3n-e4b-it`

**Why:**
1. **140+ languages** including Malayalam
2. **Multimodal** - can process audio, video, image, text
3. **FREE** on the free tier

**Limitation:** 30-second audio chunks. Need to split longer recordings.

**How to use:**
```python
from openai import OpenAI
import base64

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-nvidia-api-key"
)

# Read and encode audio (30-sec chunk)
with open("chunk.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="google/gemma-3n-e4b-it",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcribe this Malayalam audio."},
                {"type": "audio_url", "audio_url": {"url": f"data:audio/wav;base64,{audio_data}"}}
            ]
        }
    ],
    max_tokens=4096
)

print(response.choices[0].message.content)
```

---

## Summary

| Model | Malayalam | Type | Recommendation |
|-------|-----------|------|----------------|
| **`whisper-large-v3`** | **✅** | **Dedicated ASR** | **Best choice** |
| `gemma-3n-e4b-it` | ✅ | Multimodal LLM | Alternative (30-sec chunks) |
| `gemma-3n-e2b-it` | ✅ | Multimodal LLM | Weaker than E4B |
| `kimi-k2.6` | ❓ | Multimodal LLM | Coding focus |
| `nemotron-3-nano-omni` | ❌ | Multimodal LLM | English-only |
| `phi-4-multimodal-instruct` | ❌ | Multimodal LLM | 8 languages only |

**All models above are FREE on the free tier.**

---

## References

- [NVIDIA Build Free Models](https://build.nvidia.com/models?filters=nimType%3Anim_type_preview) - 144 free models
- [Whisper Large v3](https://build.nvidia.com/openai/whisper-large-v3)
- [Gemma 3n Overview](https://ai.google.dev/gemma/docs/gemma-3n)
- [NVIDIA ASR Support Matrix](https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/asr.html)
