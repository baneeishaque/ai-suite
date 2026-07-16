# NVIDIA build.nvidia.com Free Endpoint Models - Sorted by Context Length

Complete list of **144 free endpoint models** sorted by context length (largest first).

**Free Tier Limits:**
- Credits on signup: 1,000 (up to 5,000)
- Rate limit: 40 requests/min
- Credit card: Not required
- Source: https://build.nvidia.com/models?filters=nimType%3Anim_type_preview (pages 1-2)

---

## 1M Context (1,000,000 tokens)

| # | Model ID | Provider | Parameters | Best For |
|---|----------|----------|------------|----------|
| 1 | `deepseek-v4-pro` | DeepSeek | 1.6T (49B active) | Coding, long-form generation |
| 2 | `deepseek-v4-flash` | DeepSeek | 284B (13B active) | Fast coding, agents |
| 3 | `nemotron-3-ultra-550b-a55b` | NVIDIA | 550B (55B active) | Most capable, coding, reasoning |
| 4 | `nemotron-3-super-120b-a12b` | NVIDIA | 120B (12B active) | Agentic coding, tool calling |
| 5 | `nemotron-3-nano-30b-a3b` | NVIDIA | 30B (3B active) | Efficient coding, instruction following |

## 256k Context (256,000 tokens)

| # | Model ID | Provider | Parameters | Best For |
|---|----------|----------|------------|----------|
| 6 | `kimi-k2.6` | Moonshot | 1T MoE | Long-horizon coding, agentic |
| 7 | `mistral-small-4-119b-2603` | Mistral | 119B MoE | Hybrid MoE, coding |
| 8 | `qwen3.5-397b-a17b` | Alibaba | 397B (17B active) | Multimodal, agentic |
| 9 | `qwen3.5-122b-a10b` | Alibaba | 122B (10B active) | Coding, reasoning |
| 10 | `qwen3-next-80b-a3b-instruct` | Alibaba | 80B (3B active) | Ultra-long context |
| 11 | `step-3.7-flash` | StepFun | 200B MoE | Enterprise, agentic, coding |
| 12 | `step-3.5-flash` | StepFun | 200B MoE | Frontier agentic AI |

## 128k Context (128,000 tokens)

| # | Model ID | Provider | Parameters | Best For |
|---|----------|----------|------------|----------|
| 13 | `llama-4-maverick-17b-128e-instruct` | Meta | 17B (128 experts) | Multimodal, multilingual |
| 14 | `mistral-large-3-675b-instruct-2512` | Mistral | 675B MoE | Largest Mistral |
| 15 | `minimax-m2.7` | MiniMax | 230B | Coding, reasoning |
| 16 | `glm-5.1` | Z.ai | - | Agentic workflows, coding |
| 17 | `nemotron-nano-12b-v2-vl` | NVIDIA | 12B | Multi-image, video understanding |

## 32k Context (32,000 tokens)

| # | Model ID | Provider | Parameters | Best For |
|---|----------|----------|------------|----------|
| 18 | `llama-3.3-70b-instruct` | Meta | 70B | Reasoning, function calling |
| 19 | `llama-3.3-nemotron-super-49b-v1` | NVIDIA | 49B | Reasoning, tool calling |
| 20 | `llama-3.3-nemotron-super-49b-v1.5` | NVIDIA | 49B | Latest version |
| 21 | `llama-3.1-70b-instruct` | Meta | 70B | Conversations, reasoning |
| 22 | `minimax-m3` | MiniMax | MoE | Multimodal, tool calling |
| 23 | `gemma-4-31b-it` | Google | 31B | Frontier reasoning, coding |
| 24 | `gpt-oss-120b` | OpenAI | 120B MoE | MoE reasoning |
| 25 | `dracarys-llama-3.1-70b-instruct` | - | 70B | Code generation, summarization |
| 26 | `mistral-medium-3.5-128b` | Mistral | 128B | Text generation, coding |
| 27 | `stockmark-2-100b-instruct` | Stockmark | 100B | Japanese, business docs |
| 28 | `nemotron-3-nano-omni-30b-a3b-reasoning` | NVIDIA | 30B/3B | Omni-modal reasoning |
| 29 | `seed-oss-36b-instruct` | ByteDance | 36B | Long-context, agentic |

## 16k Context (16,000 tokens)

| # | Model ID | Provider | Parameters | Best For |
|---|----------|----------|------------|----------|
| 30 | `llama-3.1-8b-instruct` | Meta | 8B | Small, fast |
| 31 | `llama-3.1-nemotron-nano-8b-v1` | NVIDIA | 8B | PC and edge |
| 32 | `llama-3.2-11b-vision-instruct` | Meta | 11B | Image reasoning |
| 33 | `llama-3.2-90b-vision-instruct` | Meta | 90B | Image reasoning |
| 34 | `ministral-14b-instruct-2512` | Mistral | 14B | General purpose VLM |
| 35 | `solar-10.7b-instruct` | Upstage | 10.7B | NLP, reasoning, math |
| 36 | `phi-4-multimodal-instruct` | Microsoft | 14B | Multimodal reasoning |
| 37 | `gemma-3n-e4b-it` | Google | 4B | Edge computing |
| 38 | `gemma-3n-e2b-it` | Google | 2B | Edge computing |
| 39 | `diffusiongemma-26b-a4b-it` | Google | 26B | Real-time text apps |
| 40 | `mixtral-8x7b-instruct-v0.1` | Mistral | 8x7B | MoE, instruction following |
| 41 | `llama-3.1-nemotron-nano-vl-8b-v1` | NVIDIA | 8B | Vision-language |
| 42 | `paligemma` | Google | - | Vision-language |

## 8k Context (8,192 tokens)

| # | Model ID | Provider | Parameters | Best For |
|---|----------|----------|------------|----------|
| 43 | `llama-3.2-1b-instruct` | Meta | 1B | Tiny, edge devices |
| 44 | `llama-3.2-3b-instruct` | Meta | 3B | Small, efficient |
| 45 | `gemma-2-2b-it` | Google | 2B | Small, edge applications |
| 46 | `gpt-oss-20b` | OpenAI | 20B MoE | Efficient reasoning, math |
| 47 | `nemotron-mini-4b-instruct` | NVIDIA | 4B | On-device, RAG |
| 48 | `phi-4-mini-instruct` | Microsoft | - | Latency-bound, constrained |
| 49 | `sarvam-m` | Sarvam | - | Indian languages, programming |
| 50 | `nvidia-nemotron-nano-9b-v2` | NVIDIA | 9B | Edge reasoning |

## Embedding Models (Variable Context)

| # | Model ID | Provider | Context | Best For |
|---|----------|----------|---------|----------|
| 51 | `nv-embed-v1` | NVIDIA | 512 | Text embeddings |
| 52 | `nv-embedcode-7b-v1` | NVIDIA | 8k | Code embeddings |
| 53 | `nv-embedqa-e5-v5` | NVIDIA | 512 | QA retrieval |
| 54 | `bge-m3` | BAAI | 8k | Text retrieval |
| 55 | `llama-nemotron-embed-1b-v2` | NVIDIA | 32k | Multilingual embeddings |
| 56 | `llama-nemotron-embed-vl-1b-v2` | NVIDIA | 32k | Multimodal retrieval |
| 57 | `llama-nemotron-rerank-1b-v2` | NVIDIA | 32k | Reranking |
| 58 | `llama-nemotron-rerank-vl-1b-v2` | NVIDIA | 32k | Multimodal reranking |
| 59 | `rerank-qa-mistral-4b` | Mistral | 8k | QA reranking |

## Safety/Moderation Models (Variable Context)

| # | Model ID | Provider | Context | Best For |
|---|----------|----------|---------|----------|
| 60 | `nemotron-3-content-safety` | NVIDIA | 32k | Content moderation |
| 61 | `nemotron-3.5-content-safety` | NVIDIA | 32k | Content moderation |
| 62 | `nemotron-content-safety-reasoning-4b` | NVIDIA | 32k | Safety reasoning |
| 63 | `llama-3.1-nemoguard-8b-content-safety` | Meta | 32k | Safety |
| 64 | `llama-3.1-nemoguard-8b-topic-control` | Meta | 32k | Topic control |
| 65 | `llama-3.1-nemotron-safety-guard-8b-v3` | NVIDIA | 32k | Safety |
| 66 | `llama-guard-4-12b` | Meta | 32k | Safety classification |
| 67 | `nemoguard-jailbreak-detect` | NVIDIA | 32k | Jailbreak detection |

## OCR/Document Models (Variable Context)

| # | Model ID | Provider | Context | Best For |
|---|----------|----------|---------|----------|
| 68 | `nemotron-ocr-v1` | NVIDIA | 32k | OCR, text extraction |
| 69 | `nemotron-ocr-v2` | NVIDIA | 32k | Multilingual OCR |
| 70 | `nemoretriever-ocr` | NVIDIA | 32k | Document parsing |
| 71 | `paddleocr` | PaddlePaddle | 32k | Table extraction |
| 72 | `nemoretriever-page-elements-v2` | NVIDIA | 32k | Document element detection |
| 73 | `nemotron-graphic-elements-v1` | NVIDIA | 32k | Document element detection |
| 74 | `nemotron-page-elements-v3` | NVIDIA | 32k | Document element detection |
| 75 | `nemotron-table-structure-v1` | NVIDIA | 32k | Table detection |
| 76 | `nemoretriever-parse` | NVIDIA | 32k | Text/metadata retrieval |
| 77 | `nemotron-parse` | NVIDIA | 32k | Text/metadata retrieval |

## Image Generation Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 78 | `qwen-image` | Alibaba | Text-to-image |
| 79 | `qwen-image-edit` | Alibaba | Image editing |
| 80 | `FLUX.1-dev` | Black Forest Labs | Image generation |
| 81 | `FLUX.1-Kontext-dev` | Black Forest Labs | In-context image generation |
| 82 | `FLUX.1-schnell` | Black Forest Labs | Fast image generation |
| 83 | `flux.2-klein-4b` | Black Forest Labs | Fast image gen/edit |
| 84 | `stable-diffusion-3.5-large` | Stability AI | Text-to-image |

## TTS/Voice Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 85 | `chatterbox-multilingual-tts` | - | Multilingual TTS |
| 86 | `magpie-tts-multilingual` | - | Multilingual TTS |
| 87 | `magpie-tts-zeroshot` | - | Zero-shot TTS |
| 88 | `studio-voice` | - | Voice enhancement |

## Translation Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 89 | `megatron-1b-nmt` | NVIDIA | 36-language translation |
| 90 | `riva-translate-1.6b` | NVIDIA | 36-language translation |
| 91 | `riva-translate-4b-instruct-v1_1` | NVIDIA | 12-language translation |

## ASR/Speech Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 92 | `whisper-large-v3` | OpenAI | 99 languages including Malayalam |
| 93 | `canary-1b-asr` | NVIDIA | 25 European languages |
| 94 | `parakeet-1.1b-rnnt-multilingual-asr` | NVIDIA | 25 languages |
| 95 | `nemotron-asr-streaming` | NVIDIA | English streaming |
| 96 | `parakeet-ctc-0.6b-asr` | NVIDIA | English |
| 97 | `parakeet-ctc-0.6b-es` | NVIDIA | Spanish-English |
| 98 | `parakeet-ctc-0.6b-vi` | NVIDIA | Vietnamese-English |
| 99 | `parakeet-ctc-0.6b-zh-cn` | NVIDIA | Mandarin-English |
| 100 | `parakeet-ctc-0.6b-zh-tw` | NVIDIA | Mandarin Taiwanese-English |
| 101 | `parakeet-ctc-1.1b-asr` | NVIDIA | English |
| 102 | `parakeet-tdt-0.6b-v2` | NVIDIA | English |

## Video/Animation Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 103 | `LipSync` | - | Lip dubbing |
| 104 | `eyecontact` | - | Gaze redirection |
| 105 | `cosmos3-nano` | NVIDIA | Physics-aware video generation |
| 106 | `cosmos3-nano-reasoner` | NVIDIA | Video understanding |
| 107 | `cosmos-transfer1-7b` | NVIDIA | Video world states |
| 108 | `cosmos-transfer2.5-2b` | NVIDIA | Video world states |
| 109 | `relighting` | - | Video relighting |
| 110 | `synthetic-video-detector` | NVIDIA | AI video detection |

## Audio Enhancement Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 111 | `active-speaker-detection` | - | Speaker detection |
| 112 | `background-noise-removal` | - | Noise removal |

## Scientific/Domain Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 113 | `alphafold2` | DeepMind | Protein structure |
| 114 | `alphafold2-multimer` | DeepMind | Protein structure |
| 115 | `boltz-2` | - | Molecular structure |
| 116 | `bevformer` | - | Autonomous driving perception |
| 117 | `cuopt` | NVIDIA | Route optimization |
| 118 | `diffdock` | - | Molecular docking |
| 119 | `esm2-650m` | Meta | Protein embeddings |
| 120 | `esmfold` | Meta | Protein structure |
| 121 | `evo2-40b` | - | Genomic foundation model |
| 122 | `fidelity` | - | CFD simulations |
| 123 | `fluent` | - | CFD simulations |
| 124 | `fourcastnet` | NVIDIA | Weather prediction |
| 125 | `genmol` | - | Molecular generation |
| 126 | `gliner-pii` | - | PII detection |
| 127 | `molmim` | - | Molecular generation |
| 128 | `msa-search` | - | Protein sequence alignment |
| 129 | `openfold2` | - | Protein structure |
| 130 | `openfold3` | - | Biomolecular structure |
| 131 | `proteinmpnn` | - | Protein sequence prediction |
| 132 | `rfdiffusion` | - | Protein backbone generation |
| 133 | `simcenter-star-ccm+` | Siemens | CFD simulations |
| 134 | `sparsedrive` | - | Autonomous driving |
| 135 | `spectre-x` | - | Chip design verification |
| 136 | `streampetr` | - | 3D object detection |
| 137 | `vista-3d` | - | Medical image segmentation |
| 138 | `trellis` | Microsoft | 3D asset generation |

## Other Models (N/A Context)

| # | Model ID | Provider | Best For |
|---|----------|----------|----------|
| 139 | `ising-calibration-1-35b-a3b` | - | Quantum computer calibration |
| 140 | `nvidia-nemotron-nano-9b-v2` | NVIDIA | Edge reasoning |
| 141 | `reka-flash-3` | Reka | Fast responses |
| 142 | `reka-core-20250501` | Reka | Complex reasoning |
| 143 | `llama-3.2-1b-instruct` | Meta | Tiny, edge devices |
| 144 | `llama-3.2-3b-instruct` | Meta | Small, efficient |

---

## Top 5 Recommendations for Coding (by Context Length)

### Best for Large Codebases (1M context)
1. **`deepseek-v4-pro`** - 1M context, 384k output, highest coding benchmarks
2. **`deepseek-v4-flash`** - 1M context, fastest
3. **`nemotron-3-super-120b-a12b`** - 1M context, tool calling

### Best for Medium Projects (256k context)
4. **`qwen3.5-397b-a17b`** - 256k, multimodal, largest
5. **`mistral-small-4-119b-2603`** - 256k, hybrid MoE
