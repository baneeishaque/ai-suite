# NVIDIA Build Models: Audio/Video Transcription Analysis

**Task:** Transcribe Malayalam meeting recordings  
**Date:** June 29, 2026  
**Source:** [nvidia-build-free-models.md](nvidia-build-free-models.md) - 144 free models total

---

## Models with Audio/Video Input Support

### Multimodal LLMs (Chat Models)

| # | Model | Provider | Audio | Video | Malayalam | Free |
|---|-------|----------|-------|-------|-----------|------|
| 1 | `nemotron-3-nano-omni-30b-a3b-reasoning` | NVIDIA | ✓ | ✓ | ❌ | ✓ |
| 2 | `phi-4-multimodal-instruct` | Microsoft | ✓ | ✗ | ❌ | ✓ |
| 3 | `gemma-3n-e4b-it` | Google | ✓ | ✓ | ✅ | ✓ |
| 4 | `gemma-3n-e2b-it` | Google | ✓ | ✓ | ✅ | ✓ |
| 5 | `kimi-k2.6` | Moonshot | ✓ | ✓ | ❓ | ✓ |
| 6 | `nemotron-nano-12b-v2-vl` | NVIDIA | ✗ | ✓ | ❌ | ✓ |
| 7 | `nemotron-voicechat` | NVIDIA | ⚠️ | ✗ | ❌ | ✓ |

### Dedicated ASR Models (Speech-to-Text)

| # | Model | Provider | Malayalam | Languages | Free |
|---|-------|----------|-----------|-----------|------|
| 8 | `canary-1b-asr` | NVIDIA | ❌ | 25 European | ✓ |
| 9 | `parakeet-1.1b-rnnt-multilingual-asr` | NVIDIA | ❌ | 25 (Indic: Hindi, Tamil, Bengali) | ✓ |
| 10 | `nemotron-asr-streaming` | NVIDIA | ❌ | English | ✓ |
| 11 | `whisper-large-v3` | OpenAI | ✅ | 99 languages | ✓ |
| 12 | `parakeet-ctc-0.6b-asr` | NVIDIA | ❌ | English | ✓ |
| 13 | `parakeet-ctc-0.6b-es` | NVIDIA | ❌ | Spanish-English | ✓ |
| 14 | `parakeet-ctc-0.6b-vi` | NVIDIA | ❌ | Vietnamese-English | ✓ |
| 15 | `parakeet-ctc-0.6b-zh-cn` | NVIDIA | ❌ | Mandarin-English | ✓ |
| 16 | `parakeet-ctc-0.6b-zh-tw` | NVIDIA | ❌ | Mandarin Taiwanese-English | ✓ |
| 17 | `parakeet-ctc-1.1b-asr` | NVIDIA | ❌ | English | ✓ |
| 18 | `parakeet-tdt-0.6b-v2` | NVIDIA | ❌ | English | ✓ |

---

## Detailed Analysis

### 1. nemotron-3-nano-omni-30b-a3b-reasoning (NVIDIA)

| Aspect | Details |
|--------|---------|
| Parameters | 30B total / 3B active (MoE) |
| Audio Encoder | Parakeet-TDT-0.6B-v2 |
| Audio Support | ✓ Speech, video audio |
| Context Window | 256K tokens |
| Word Timestamps | ✓ Yes |
| Malayalam Support | ❌ Not explicitly supported |
| Training Data | English-focused (all benchmarks in English) |
| WER (English) | 5.95% (OpenASR) |
| Max Audio Length | Up to 1 hour |
| API | OpenAI-compatible |

**Architecture:**
- Hybrid Mamba-2 + Attention MoE
- C-RADIOv4-H vision encoder
- Parakeet audio encoder
- Unified encoder-projector-decoder design

**Benchmarks:**
| Benchmark | Score |
|-----------|-------|
| VoiceBench | 89.4 |
| HF OpenASR | 5.95 WER |
| Video MME | 72.2 |
| World Sense | 55.4 |
| DailyOmni | 74.5 |

**Verdict:** Best architecture for transcription, but **English-only**. Will likely fail on Malayalam.

---

### 2. phi-4-multimodal-instruct (Microsoft)

| Aspect | Details |
|--------|---------|
| Parameters | 14B |
| Audio Support | ✓ Speech |
| Audio Languages | English, Chinese, German, French, Italian, Japanese, Spanish, Portuguese |
| Malayalam Support | ❌ Not supported |
| Max Audio Length | 40 seconds (quality), 30 minutes (summarization) |
| WER (English) | 6.14% (OpenASR #1) |
| API | OpenAI-compatible |

**Architecture:**
- Mixture-of-LoRAs for different modalities
- Single model for text, vision, audio
- 128K context length

**Supported Audio Languages:**
English, Chinese, German, French, Italian, Japanese, Spanish, Portuguese

**Verdict:** Excellent for supported languages, but **Malayalam not in list**. Won't work.

---

### 3. gemma-3n-e4b-it (Google) ⭐ RECOMMENDED

| Aspect | Details |
|--------|---------|
| Parameters | 5B total / ~2B effective |
| Audio Support | ✓ Speech |
| Audio Languages | **140+ spoken languages** |
| Malayalam Support | ✅ Likely supported (in 140+) |
| Max Audio Length | 30 seconds per clip |
| Context Window | 32K tokens |
| Architecture | Edge-optimized, streaming audio |
| API | OpenAI-compatible |

**Architecture:**
- MatFormer flexible architecture
- Per-Layer Embedding (PLE) parameter caching
- Streaming audio encoder
- Parameter skipping for efficiency

**Key Features:**
- Trained on 140+ spoken languages
- Optimized for low-resource devices
- Can process audio, image, video, text
- Dynamic parameter loading

**Limitation:** 30-second audio clips. Longer recordings need chunking.

**Verdict:** **Best chance for Malayalam** - only model explicitly supporting 140+ languages.

---

### 4. gemma-3n-e2b-it (Google)

| Aspect | Details |
|--------|---------|
| Parameters | 2B effective |
| Audio Languages | 140+ (same as E4B) |
| Malayalam Support | ✅ Likely supported |
| Max Audio Length | 30 seconds |
| Capability | Less than E4B |

**Verdict:** Same language support as E4B but **less capable**. Use E4B instead.

---

### 5. kimi-k2.6 (Moonshot)

| Aspect | Details |
|--------|---------|
| Parameters | 1T total |
| Audio Support | ✓ |
| Malayalam Support | ❓ Unknown |
| Focus | Coding, agentic tasks |
| Video Support | ✓ |
| Context Window | 262K tokens |

**Architecture:**
- 1T total parameters
- Native multimodal architecture
- MoE with 32 experts
- MoonViT vision encoder

**Verdict:** Primarily a **coding model**. Audio is secondary. Unlikely to be good at Malayalam transcription.

---

### 6. nemotron-nano-12b-v2-vl (NVIDIA)

| Aspect | Details |
|--------|---------|
| Parameters | 12B |
| Input Modalities | Image, Video, Text |
| Audio Support | ❌ No audio input |
| Language | English only |
| Context | 128K tokens |

**Verdict:** **No audio support** despite being listed. Video-only visual understanding.

---

### 7. nemotron-voicechat (NVIDIA)

| Aspect | Details |
|--------|---------|
| Parameters | 12B |
| Type | Speech-to-speech (not transcription) |
| Purpose | Real-time voice agents |
| Output | Audio (not text) |
| Status | Early access |
| Latency | Sub-300ms |

**Architecture:**
- End-to-end speech model
- Full-duplex (simultaneous input/output)
- Parakeet encoder + TTS decoder
- Streaming LLM architecture

**Verdict:** **Not for transcription** - it's a voice chatbot that outputs audio.

---

### 8. canary-1b-asr (NVIDIA)

| Aspect | Details |
|--------|---------|
| Parameters | 1B |
| Type | Encoder-decoder ASR |
| Malayalam Support | ❌ **Not supported** |
| Supported Languages | 25 European languages |
| Features | Punctuation, timestamps, translation |

**Supported Languages:**
Bulgarian, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, German, Greek, Hungarian, Italian, Latvian, Lithuanian, Maltese, Polish, Portuguese, Romanian, Russian, Slovak, Slovenian, Spanish, Swedish, Ukrainian

**Verdict:** European languages only. **No Malayalam.**

---

### 9. parakeet-1.1b-rnnt-multilingual-asr (NVIDIA)

| Aspect | Details |
|--------|---------|
| Parameters | 1.1B |
| Type | Streaming ASR |
| Malayalam Support | ❌ **Not supported** |
| Model Types | Default, Prompt, Indic |
| Features | Streaming, punctuation, timestamps |

**Supported Languages (Indic type):**
- Hindi (hi-IN) ✓
- Bengali (bn-IN) ✓
- Tamil (ta-IN) ✓
- **Malayalam (ml-IN) ❌ NOT listed**

**Verdict:** Has Indic type but **Malayalam not included**. Only Hindi, Bengali, Tamil.

---

### 10. nemotron-asr-streaming (NVIDIA)

| Aspect | Details |
|--------|---------|
| Type | Streaming ASR |
| Malayalam Support | ❌ **Not supported** |
| Model Types | English-only, Multilingual |
| Supported Locales | 40 |

**Supported Languages (40 locales):**
Arabic, Bulgarian, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, German, Greek, Hebrew, Hindi, Hungarian, Italian, Japanese, Korean, Latvian, Lithuanian, Maltese, Norwegian, Polish, Portuguese, Romanian, Russian, Slovak, Slovenian, Spanish, Swedish, Thai, Turkish, Ukrainian, Vietnamese

**Verdict:** Hindi is supported but **Malayalam not included**.

---

### 11. whisper-large-v3 (OpenAI via NVIDIA)

| Aspect | Details |
|--------|---------|
| Type | ASR + Translation |
| Malayalam Support | ✅ **Supported** |
| Supported Languages | 99 languages |
| Features | Translation, timestamps |

**Supported Languages:** All 99 Whisper languages including Malayalam (ml)

**Verdict:** **Best for Malayalam transcription** - dedicated ASR model with 99 language support.

---

## Comparison Matrix

### Multimodal LLMs

| Feature | nemotron-omni | phi-4-multimodal | gemma-3n-e4b | gemma-3n-e2b | kimi-k2.6 | nemotron-vl | voicechat |
|---------|---------------|------------------|--------------|--------------|-----------|-------------|-----------|
| Audio Input | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Video Input | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Malayalam | ❌ | ❌ | ✅ | ✅ | ❓ | ❌ | ❌ |
| Max Audio | 1hr | 40sec | 30sec | 30sec | Unknown | N/A | Real-time |
| Params | 30B/3B | 14B | 5B/2B | 2B | 1T | 12B | 12B |
| Word Timestamps | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Context | 256K | 128K | 32K | 32K | 262K | 128K | N/A |
| Free Tier | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Early Access |

### Dedicated ASR Models

| Feature | canary-1b | parakeet-rnnt | nemotron-asr | whisper-large-v3 |
|---------|-----------|---------------|--------------|------------------|
| Type | ASR+Translation | Streaming ASR | Streaming ASR | ASR+Translation |
| Malayalam | ❌ | ❌ | ❌ | ✅ |
| Languages | 25 European | 25 (Indic type) | English | 99 |
| Streaming | ✗ | ✓ | ✓ | ✗ |
| Word Timestamps | ✓ | ✓ | ✓ | ✓ |
| Free Tier | ✓ | ✓ | ✓ | ✓ |

---

## Recommendation

### Primary Choice: `whisper-large-v3` ⭐

**Why:**
1. **Dedicated ASR model** - purpose-built for speech recognition
2. **99 languages** including Malayalam
3. **Best accuracy** for transcription tasks
4. **Word-level timestamps** available
5. **Free on NVIDIA build**

**Limitation:** Not streaming (batch processing only). Max audio length varies.

---

### Alternative: `gemma-3n-e4b-it`

**Why:**
1. **140+ spoken languages** including Malayalam
2. **Multimodal** - can process audio, video, image, text
3. **Edge-optimized** = fast inference
4. **Free on NVIDIA build**

**Limitation:** 30-second audio clips. Longer recordings need chunking.

---

### For Streaming (Real-time): `nemotron-asr-streaming`

**Why:**
1. **Streaming support** - real-time transcription
2. **40 locales** including Hindi
3. **Auto language detection**

**Limitation:** Malayalam not supported. Only Hindi among Indic languages.

---

### Fallback Options:

1. **If whisper-large-v3 fails on Malayalam:**
   - Use `gemma-3n-e4b-it` with chunking
   - Or use `nemotron-3-nano-omni` with English translation prompt

2. **If you need word-level timestamps:**
   - Use `whisper-large-v3` (has word timestamps)
   - Or use `nemotron-3-nano-omni` (has word timestamps)

3. **If you need Indic languages (Hindi, Tamil, Bengali):**
   - Use `parakeet-1.1b-rnnt-multilingual` with Indic type
   - Optimized for Indic languages

---

## Implementation Notes

### For whisper-large-v3 (Recommended):

1. **Audio format:** WAV, MP3, FLAC, M4A
2. **Max audio:** Varies (typically 30 min - 1 hour)
3. **API endpoint:** `https://integrate.api.nvidia.com/v1`
4. **Model ID:** `openai/whisper-large-v3`

### Example API Call:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-nvidia-api-key"
)

# For file upload
response = client.audio.transcriptions.create(
    model="openai/whisper-large-v3",
    file=open("meeting.wav", "rb"),
    language="ml"  # Malayalam
)

print(response.text)
```

### For gemma-3n-e4b-it (Alternative):

1. **Audio format:** WAV, MP3, FLAC (single channel)
2. **Chunk size:** 30 seconds max
3. **API endpoint:** `https://integrate.api.nvidia.com/v1`
4. **Model ID:** `google/gemma-3n-e4b-it`

### Example API Call:

```python
from openai import OpenAI
import base64

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-nvidia-api-key"
)

# Read and encode audio
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

## References

- [NVIDIA Build Free Models](nvidia-build-free-models.md) - 144 free models
- [Nemotron 3 Nano Omni Docs](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-omni-30b-a3b-reasoning)
- [Phi-4 Multimodal HuggingFace](https://huggingface.co/microsoft/Phi-4-multimodal-instruct)
- [Gemma 3n Overview](https://ai.google.dev/gemma/docs/gemma-3n)
- [Kimi K2.6 Docs](https://platform.kimi.ai/docs/guide/kimi-k2-6-quickstart)
- [Canary 1B ASR](https://build.nvidia.com/nvidia/canary-1b-asr)
- [Parakeet RNNT Multilingual](https://build.nvidia.com/nvidia/parakeet-1_1b-rnnt-multilingual-asr)
- [Nemotron ASR Streaming](https://docs.nvidia.com/nim/speech/latest/asr/deploy-asr-models/nemotron-asr-streaming.html)
- [Whisper Large v3](https://build.nvidia.com/openai/whisper-large-v3)
- [NVIDIA ASR Support Matrix](https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/asr.html)
