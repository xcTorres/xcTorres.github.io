---
title: "VLM Notes"
subtitle: "Vision-Language Models · Diffusion · Video Understanding"
topic: vlm
category: summary
order: 1
lang: en
pair: vlm-summary
source: "VLM知识总结.md"
mathjax: true
---

* TOC
{:toc .llm-toc-list}

> **Scope**: vision-language models · diffusion generation · video understanding. Every entry runs **core answer → how it works → trade-offs / follow-ups → references**; ⭐ marks the points worth digging into.
>
> **See also**: [LLM Notes](/llm/summary/) · [Agent Notes](/agent/summary/)

---

# Part IV: Vision-Language Models

### 19. How CLIP works and why it mattered ⭐ `#multimodal #core`
**【Core answer】** A two-tower design (an image encoder and a text encoder) trained by **contrastive learning** on a vast pile of image-text pairs: pull matched image and text representations together, push mismatched ones apart (InfoNCE / symmetric cross-entropy). What comes out is strong zero-shot classification and image-text retrieval.

**【How it works】**
- A batch of N image-text pairs forms an N×N similarity matrix. The diagonal holds the positives, everything else is a negative, and cross-entropy is applied along both rows and columns.
- Zero-shot classification: write each class name as a text prompt ("a photo of a {class}") and take whichever is most similar to the image.
- The vision encoder it learns became the visual backbone for a great many later VLMs, LLaVA among them.

**【Trade-offs / follow-ups】**
- The limits: it is good at *matching and classifying* but **cannot generate** a text answer, and it is weak on fine detail, counting and spatial relations.
- A common follow-up is **why contrastive learning rather than classification**: contrastive training can consume enormous amounts of weakly labelled data (web image-text pairs) without committing to a fixed label set, which is where the generalisation and zero-shot ability come from.

📖 Reference: CLIP — [https://arxiv.org/abs/2103.00020](https://arxiv.org/abs/2103.00020)

---

### 19b. How vision encoders evolved: CLIP → SigLIP → SigLIP2 ⭐ `#multimodal #core`
**【Core answer】** A VLM's "eyes" have gone **CLIP → SigLIP → SigLIP2**, along one line: **a more efficient loss, stronger features, more native resolution**. SigLIP swaps CLIP's **softmax contrastive loss for a sigmoid** one (each image-text pair is an independent binary decision), dropping global normalisation so it trains well at small batch sizes and does more with the same compute. SigLIP2 then layers on self-supervision, captioning, multilingual data and native dynamic resolution for more general features. LLaVA-OneVision uses SigLIP, replacing the CLIP of earlier LLaVA.

**【How it works】**
- **CLIP (softmax contrastive)**: compute the N×N similarity matrix and **normalise globally over all negatives** (InfoNCE), which makes it dependent on a **very large batch** and hungry for memory.
- **SigLIP (sigmoid)**: treat each image-text pair as an **independent binary classification** (match = 1, no match = 0) with a sigmoid loss, so **no global normalisation is needed**. It trains well at small batch sizes, costs less, scales more easily, and is more accurate under equal conditions. The intuition: CLIP makes a whole batch compete for one best match, while SigLIP asks each pair to judge itself.
- **SigLIP2**: on top of the sigmoid loss it adds (1) **self-supervision** (self-distillation plus masked prediction) for stronger local and dense features, which helps detection, segmentation and grounding; (2) **caption-style pretraining** (a decoder describing the image) for finer semantic alignment; (3) **multilingual** data; and (4) **native dynamic resolution (NaFlex)**, supporting arbitrary aspect ratios and variable resolution instead of forcing a resize.

**【Trade-offs / follow-ups】**
- A common follow-up is **why sigmoid removes the large-batch dependency**: softmax has to normalise across the batch's negatives, so a bigger batch means more negatives and a better estimate. Sigmoid decouples each pair into an independent judgement, so no batch-wide view is required.
- A common follow-up is **how this relates to codec-based encoders**: SigLIP2 already pushes native dynamic resolution, but it still feeds video as sampled frames. LLaVA-OneVision-2 goes further and builds its own **OneVision-Encoder** (codec-aligned sparsity plus 3D RoPE, [2602.08683](https://arxiv.org/abs/2602.08683)), beating SigLIP2 and Qwen3-ViT on 16 benchmarks with fewer tokens.

📖 Reference: SigLIP — [https://arxiv.org/abs/2303.15343](https://arxiv.org/abs/2303.15343) ｜ SigLIP2 — [https://arxiv.org/abs/2502.14786](https://arxiv.org/abs/2502.14786)

---

### 20. How do mainstream VLMs attach vision to an LLM? ⭐ `#multimodal #core`
**【Core answer】** The usual three stages: **vision encoder (a CLIP ViT, say) → connector (projector) → LLM**. What differs between systems is mostly the connector.

**【How it works】**
- **LLaVA**: an **MLP projector** maps visual features straight into the LLM's word-embedding space as "visual tokens", prepended to the text tokens. The simplest option, data-efficient, and currently the default.
- **BLIP-2**: a **Q-Former** — a set of learnable queries that cross-attend to a frozen vision encoder and extract a fixed number of visual tokens (32, for instance), which then go into a frozen LLM. Parameter-efficient.
- **Flamingo**: **gated cross-attention layers inserted into a frozen LLM** carry the visual information, with a Perceiver Resampler squeezing variable-length visual features into a fixed token count. Strong at few-shot and interleaved image-text input.
- **Qwen-VL / InternVL**: emphasise **high and dynamic resolution** (tiling the image), which lifts OCR, document and fine-detail understanding markedly.

**【Trade-offs / follow-ups】**
- The MLP route (LLaVA) is simple but produces many visual tokens and eats context; the Q-Former (BLIP-2) uses few tokens but is harder to train and can lose detail.
- A common follow-up is **whether to unfreeze the vision encoder**: early work froze it, while later high-quality VLMs often unfreeze it or move to a larger vision tower to recover detail.

📖 Reference: LLaVA — [https://arxiv.org/abs/2304.08485](https://arxiv.org/abs/2304.08485) ｜ BLIP-2 — [https://arxiv.org/abs/2301.12597](https://arxiv.org/abs/2301.12597) ｜ Flamingo — [https://arxiv.org/abs/2204.14198](https://arxiv.org/abs/2204.14198)

---

### 21. LLaVA's two training stages ⭐ `#multimodal`
**【Core answer】** (1) **Feature-alignment pretraining**: freeze both the vision encoder and the LLM and train only the projector, using image-text pairs to align visual features into the LLM's semantic space. (2) **Instruction tuning**: unfreeze the projector and the LLM and train on multimodal instruction data (VQA, reasoning, dialogue) to produce an assistant that can actually converse about images.

**【How it works】**
- Stage one only learns a translation — turning visual features into "foreign-language tokens" the LLM understands — which is why nothing but the projector moves.
- Stage two's instruction data is the real innovation: LLaVA had a text-only GPT-4 generate varied multimodal instruction-response pairs from image captions and bounding boxes, in the spirit of self-instruct.

**【Trade-offs / follow-ups】** A common follow-up is **why the LLM stays frozen in stage one**: a small alignment dataset would otherwise damage the language ability the LLM already has. Build the bridge between modalities first, then fine-tune jointly.

📖 Reference: Visual Instruction Tuning (LLaVA) — [https://arxiv.org/abs/2304.08485](https://arxiv.org/abs/2304.08485)

---

### 22. Too many visual tokens — how do you handle high resolution? `#multimodal`
**【Core answer】** Tiling a high-resolution image produces a flood of visual tokens that eats context and compute. The options: compress or merge tokens (resampler, pooling, pixel shuffle), use a fixed number of queries as in the Q-Former, or allocate tokens on demand with dynamic resolution.

**【How it works】**
- LLaVA-1.5/NeXT handles high resolution by tiling into sub-images plus a thumbnail, so token count grows with resolution.
- Pixel shuffle and token merging combine neighbouring visual tokens to cut the count.
- Video is the extreme case: frame sampling and token compression have to happen along the time axis as well.

**【Trade-offs / follow-ups】** A common follow-up is **what compression costs**: fewer tokens save compute, but OCR and fine-grained tasks degrade. It is the resolution-versus-efficiency trade-off.

---

### 23. Where VLMs fall short, and how they are measured `#multimodal`
**【Core answer】** The weak spots: fine-grained OCR, counting, spatial and directional relations, long-video temporal order, and object-level hallucination (describing things that are not in the image). Benchmarks: MMMU, MMBench, MME, DocVQA, TextVQA, ChartQA, with POPE dedicated to hallucination.

**【How it works】**
- Object hallucination usually comes from an overly strong language prior — the model *guesses* a common co-occurrence instead of actually looking.
- Evaluation should separate **perception** (can it see?) from **cognition and reasoning** (did it understand?).

**【Trade-offs / follow-ups】** A common follow-up is **how to reduce object hallucination**: raise visual resolution, train against negative samples, and penalise ungrounded descriptions during alignment (POPE-style probing).

---

### 24. Contrastive vs. generative multimodal training — which one? `#multimodal`
**【Core answer】** Contrastive training (CLIP) yields aligned image-text representations, which is what you want for retrieval and classification but cannot hold a conversation. Generative training (the LLaVA family) can look at an image, talk about it and reason — the current mainstream for "multimodal LLMs" — and it usually *starts* from a contrastively trained encoder. The two divide the labour between representation and generation, and are normally combined.

**【How it works】** The practical pipeline is almost always CLIP-style pretraining for a strong vision encoder, then attach an LLM and instruction-tune generatively. Complementary, not competing.

---

# Part IV (continued): Diffusion models and text-to-image

> Questions 19–24 covered **understanding** — looking at an image and talking about it. This section covers **generation**: producing images and video from text or noise, the paradigm underneath Stable Diffusion and Sora.

### 25. The core idea behind diffusion models ⭐ `#multimodal #generation #core`
**【Core answer】** A pair of opposite processes. The **forward (diffusion)** process gradually adds Gaussian noise to a real image until nothing but noise is left. The **reverse (denoising)** process trains a network to predict and strip that noise step by step, recovering an image. In essence the model learns to denoise; to sample, start from random noise and denoise repeatedly.

**【How it works】**
- The forward process is a **fixed, parameter-free** Markov chain with a closed form — any $x_t$ can be sampled in one shot from the original $x_0$ ($\bar\alpha_t$ is the cumulative coefficient of the noise schedule and $\epsilon\sim\mathcal{N}(0,I)$):

  $$x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon$$

- The reverse process uses a network $\epsilon_\theta(x_t,t)$ to **predict the noise that was added** (DDPM showed predicting noise is more stable than predicting the mean directly). The training objective is about as simple as it gets:

  $$\mathcal{L} = \mathbb{E}_{x_0,t,\epsilon}\big[\,\Vert \epsilon - \epsilon_\theta(x_t,t)\Vert ^2\,\big]$$

  That is: draw an image, a timestep $t$ and a noise sample, and have the network recover that noise.
- The denoising backbone is usually a **U-Net** with timestep embeddings and self-attention; the newer generation switches to a Transformer (**DiT**, question 28).

**【Trade-offs / follow-ups】**
- A common follow-up is **why it trains more easily than a GAN**: there is no adversarial discriminator, so training is stable and mode coverage is good (little mode collapse). The price is **slow sampling** — dozens to a thousand iterations.
- A common follow-up is **how it relates to VAEs and GANs**: all are generative models. Diffusion can be read as a multi-step, hierarchical denoising autoencoder that trades compute for quality and stability.

📖 Reference: DDPM — [https://arxiv.org/abs/2006.11239](https://arxiv.org/abs/2006.11239)

---

### 26. Why is diffusion sampling slow, and what is DDIM? `#multimodal #generation`
**【Core answer】** DDPM sampling walks the Markov chain one denoising step at a time, often a thousand of them. **DDIM** makes sampling **deterministic and non-Markovian**, so it can take big jumps, produce an image in a few dozen steps, and reproduce results. Higher-order ODE solvers such as **DPM-Solver** push that to roughly 10–20 steps, and the **distillation route (LCM, consistency models)** gets down to a handful of steps or even one.

**【How it works】**
- View the reverse process as solving a **probability-flow ODE/SDE**, which lets you bring standard numerical solvers to bear.
- DDIM reuses the same trained model and only changes the update rule at inference, so steps and quality can be traded freely.
- Consistency models and LCM learn a direct one-shot mapping, which is what makes real-time generation possible.

**【Trade-offs / follow-ups】** A common follow-up is **what it costs**: fewer steps are faster, but detail and fidelity drop — the usual speed-quality trade-off.

---

### 27. Why is Latent Diffusion / Stable Diffusion so effective, and how does text control it? ⭐ `#multimodal #generation #core`
**【Core answer】** Stable Diffusion *is* **Latent Diffusion**, and it turns on three things: (1) **do not diffuse in pixel space** — compress the image into a low-dimensional latent with a VAE first, which slashes compute; (2) encode the prompt with a **CLIP text encoder** and inject it into the U-Net through **cross-attention**; (3) sharpen adherence to the text with **classifier-free guidance (CFG)**.

**【How it works】**
- The VAE encoder squeezes a 512×512 image into a 64×64 latent, all diffusion happens there, and the decoder restores pixels — **one to two orders of magnitude less compute**, which is exactly why SD runs on consumer GPUs.
- Text conditioning: `prompt → CLIP text encoder → used as K/V in cross-attention` at every U-Net layer.
- Other controls: **ControlNet** (structural conditioning on edges, depth, pose), **LoRA** (lightweight style fine-tuning), **IP-Adapter** (image references).

**【Trade-offs / follow-ups】**
- A common follow-up is **how CFG works**: drop the text randomly during training so the model learns both a conditional branch $\epsilon_\theta(x_t,c)$ and an unconditional one $\epsilon_\theta(x_t,\varnothing)$; at sampling time, extrapolate along the conditional direction ($w$ is the guidance scale):

  $$\hat\epsilon = \epsilon_\theta(x_t,\varnothing) + w\,\big(\epsilon_\theta(x_t,c) - \epsilon_\theta(x_t,\varnothing)\big)$$

  Larger $w$ hews closer to the prompt, at the cost of diversity and naturalness.
- A common follow-up is **why the latent space suffices**: the VAE has already removed pixel redundancy while keeping semantics and structure, so diffusion only has to model what is perceptually relevant.

📖 Reference: Latent Diffusion / Stable Diffusion — [https://arxiv.org/abs/2112.10752](https://arxiv.org/abs/2112.10752) ｜ Classifier-Free Guidance — [https://arxiv.org/abs/2207.12598](https://arxiv.org/abs/2207.12598)

---

### 28. The frontier: DiT, flow matching, and the argument with autoregression `#multimodal #generation`
**【Core answer】** Three trends: (1) the backbone shifts from U-Net to a **Transformer (DiT)**, which scales more gracefully and is what Sora and SD3 use; (2) the objective moves from DDPM's noise prediction to **flow matching / rectified flow** (straighter paths, fewer sampling steps — adopted by SD3 and others); (3) diffusion still dominates image and video generation, but **next-token autoregressive generation** (VAR, natively multimodal models) is closing the gap.

**【How it works】**
- **DiT**: cut the latent into patches, treat them as tokens, and denoise with a Transformer. Friendly to scaling laws.
- **Flow matching / rectified flow**: learn a near-straight probability path from noise to data, so sampling needs fewer steps.
- **Video generation (Sora)** = spatio-temporal patches + DiT + diffusion.

**【Trade-offs / follow-ups】** A common follow-up is **diffusion vs. autoregression for images**: diffusion denoises in parallel and reaches high quality but needs many steps; autoregression goes token by token and unifies architecture with the LLM, but is slow over long sequences.

📖 Reference: DiT — [https://arxiv.org/abs/2212.09748](https://arxiv.org/abs/2212.09748) ｜ Flow Matching — [https://arxiv.org/abs/2210.02747](https://arxiv.org/abs/2210.02747)

---

# Part V: Video Understanding

> Video = images + **a time axis**. The difficulty is not understanding one frame; it is that (1) token count explodes as frames pile up and hits the context limit, (2) **temporal structure** has to be modelled — actions, event order, causality — and (3) online and streaming settings demand answers while the video is still playing. This section is question 22's token problem, amplified.

### 29. How does video get into an LLM? The basic recipe and its central tension ⭐ `#multimodal #video #core`
**【Core answer】** The mainstream recipe is **sample frames → encode each frame with a vision encoder → compress and aggregate tokens → feed the resulting video-token sequence to the LLM**. The central tension: a clip yields tens to thousands of frames, each worth tens to hundreds of tokens, so **total tokens = frames × tokens per frame** — enough to blow straight through the LLM's context limit. **How to compress tokens** is therefore the first question any video VLM has to answer.

**【How it works】**
- **Frame sampling**: uniform sampling (a frame every few seconds) is simplest; long videos usually scale the rate by duration (1 fps for short clips, 0.2 fps for long ones). More advanced systems pick **keyframes or key segments** by relevance to the question, so uniform sampling does not miss the decisive moment.
- **Per-frame encoding**: reuse the image-VLM machinery (CLIP ViT, SigLIP), encoding each frame independently into a group of tokens.
- **Aggregating into video tokens**: straight concatenation (most tokens), pooling over time, a Q-Former or resampler squeezing each frame or the whole clip into a fixed token count, or merging tokens between adjacent frames.
- Representative systems: **Video-LLaVA / LLaVA-NeXT-Video** (the image recipe extended to video), **VideoLLaMA** (joint audio-video), **Qwen2.5-VL / InternVL** (dynamic resolution plus dynamic frame rate, handling hour-long video and event localisation).

**【Trade-offs / follow-ups】**
- A common follow-up is **why you cannot just concatenate tokens as with images**: one minute at 30 fps is 1,800 frames; at 256 tokens each that is roughly 460,000 tokens, far past any context window. Sampling and compression are not optional.
- A common follow-up is **what sparse sampling costs**: sample too sparsely and fast actions or brief events vanish (temporal information is lost); sample too densely and tokens explode. The usual coverage-versus-efficiency trade-off.

📖 Reference: Video-LLaVA — [https://arxiv.org/abs/2311.10122](https://arxiv.org/abs/2311.10122) ｜ Qwen2.5-VL — [https://arxiv.org/abs/2502.13923](https://arxiv.org/abs/2502.13923)

---

### 30. Solving token explosion on long video, and keeping temporal information ⭐ `#multimodal #video #core`
**【Core answer】** Two lines of attack: **(1) spatio-temporal token compression** — exploit video's redundancy (static backgrounds, repeated scenes) to push token retention very low; and **(2) temporal position encoding** — tell the LLM which frame or second each visual token came from, or it cannot tell what happened first.

**【How it works】**
- **Token compression** (question 22, in video form):
  - Prune spatio-temporal redundancy: adjacent frames repeat heavily, so merge or prune tokens across space and time and keep only what changed.
  - Extreme compression: squeeze each frame to a few tokens or even **one** (STORM aggregates over time with Mamba; the "one token per frame" line of work), so an entire long video fits in a finite context.
  - Training-free variants merge tokens at inference by tree structure or similarity, with no extra training (FlashVid and others).
- **Temporal position encoding**: the point is to make the model feel *time*. Qwen2-VL's **M-RoPE (multimodal rotary position embedding)** splits position into time, height and width, with video tokens advancing along the time axis to preserve frame order and absolute timestamps — the foundation for its accurate **temporal grounding**.

**【Trade-offs / follow-ups】**
- A common follow-up is **what one-token-per-frame loses**: spatial detail within the frame (OCR, small objects). It keeps temporal coverage instead — a good bargain when seeing the whole span matters more than seeing any single frame clearly.
- A common follow-up is **why temporal encoding matters**: without it, "did he open the door before turning off the light?" is pure guesswork driven by visual priors.

📖 Reference: STORM — [https://arxiv.org/abs/2503.04130](https://arxiv.org/abs/2503.04130) ｜ Qwen2-VL (M-RoPE) — [https://arxiv.org/abs/2409.12191](https://arxiv.org/abs/2409.12191)

---

### 31. Streaming / online video understanding vs. offline `#multimodal #video`
**【Core answer】** Offline means the whole video is in hand before answering. **Streaming means processing as it arrives, being interruptible by a question at any moment, and responding in real time** — live broadcast, embodied robots, AR assistants. The key differences: future frames are unknown, the entire history cannot be held in context, so a **memory mechanism** has to maintain history incrementally, and the system must be able to speak up at the right moment.

**【How it works】**
- The core challenges: (1) history grows without bound, so the past must be compressed into **memory or summary tokens** (segment-level memory, KV-cache pruning); and (2) knowing *when* to speak — the model has to judge whether now is the moment to answer or raise an alert (anticipatory / proactive behaviour).
- Representative directions: VideoLLM-online, Flash-VStream (streaming memory), StreamAgent (anticipatory agents), and segment-level memory for multi-turn video reasoning.

**【Trade-offs / follow-ups】** A common follow-up is **why an offline model cannot simply be used for streaming**: offline models assume global visibility and reason once. Streaming demands incremental decisions under incomplete information and is latency-sensitive — a different problem setting.

📖 Reference: StreamingBench — [https://arxiv.org/abs/2411.03628](https://arxiv.org/abs/2411.03628)

---

### 32. Evaluating video understanding: benchmarks and blind spots `#multimodal #video`
**【Core answer】** Organised by video length and capability: **short-video QA** (MSRVTT, ActivityNet-QA), **broad and long video** (Video-MME, MLVU, LongVideoBench, with EgoSchema leaning on long-horizon temporal reasoning), and **streaming** (StreamingBench). The blind spots cluster around long-range causality, event order and counting, associations across distant frames, and fine-grained action recognition.

**【How it works】**
- **Video-MME**: full-spectrum, 900 videos (11 s to 60 min) across six domains, separating perception, reasoning and information extraction.
- **LongVideoBench**: interleaved image-text (subtitles included) long-context understanding, up to an hour.
- **EgoSchema**: first-person long video, built around very-long-horizon reasoning that requires watching the whole thing.
- **StreamingBench**: 18 tasks in three families (real-time, omni-source, contextual) aimed squarely at streaming ability.

**【Trade-offs / follow-ups】**
- A common follow-up is **how VLMs typically fail on long video**: because sampling is sparse, models degenerate into looking at a handful of frames and guessing from language priors, never doing genuine full-span temporal reasoning. If shuffling frame order does not change the answer, the model was not using time.
- A common follow-up is **how to check the model really uses time**: shuffle or reverse the frames and see whether the answer moves, and test on tasks that cannot be faked, such as temporal localisation ("at what second does the event occur?").

📖 Reference: Video-MME — [https://arxiv.org/abs/2405.21075](https://arxiv.org/abs/2405.21075) ｜ EgoSchema — [https://arxiv.org/abs/2308.09126](https://arxiv.org/abs/2308.09126)

---

# Appendix A: Core paper index (multimodal / VLM)

**Understanding-oriented VLMs**
- ✅ CLIP — [https://arxiv.org/abs/2103.00020](https://arxiv.org/abs/2103.00020)
- ✅ SigLIP — [https://arxiv.org/abs/2303.15343](https://arxiv.org/abs/2303.15343) ｜ SigLIP2 — [https://arxiv.org/abs/2502.14786](https://arxiv.org/abs/2502.14786)
- ✅ Flamingo — [https://arxiv.org/abs/2204.14198](https://arxiv.org/abs/2204.14198)
- ✅ BLIP-2 — [https://arxiv.org/abs/2301.12597](https://arxiv.org/abs/2301.12597)
- ✅ LLaVA (Visual Instruction Tuning) — [https://arxiv.org/abs/2304.08485](https://arxiv.org/abs/2304.08485)

**Generative / diffusion**
- ✅ DDPM — [https://arxiv.org/abs/2006.11239](https://arxiv.org/abs/2006.11239)
- ✅ Latent Diffusion / Stable Diffusion — [https://arxiv.org/abs/2112.10752](https://arxiv.org/abs/2112.10752)
- ✅ Classifier-Free Guidance — [https://arxiv.org/abs/2207.12598](https://arxiv.org/abs/2207.12598)
- ✅ DiT (Scalable Diffusion with Transformers) — [https://arxiv.org/abs/2212.09748](https://arxiv.org/abs/2212.09748)
- ✅ Flow Matching — [https://arxiv.org/abs/2210.02747](https://arxiv.org/abs/2210.02747)

**Video understanding**
- ✅ Video-LLaVA — [https://arxiv.org/abs/2311.10122](https://arxiv.org/abs/2311.10122)
- ✅ Qwen2-VL (M-RoPE) — [https://arxiv.org/abs/2409.12191](https://arxiv.org/abs/2409.12191) ｜ Qwen2.5-VL — [https://arxiv.org/abs/2502.13923](https://arxiv.org/abs/2502.13923)
- ✅ STORM (token-efficient long video) — [https://arxiv.org/abs/2503.04130](https://arxiv.org/abs/2503.04130)
- ✅ Video-MME (evaluation) — [https://arxiv.org/abs/2405.21075](https://arxiv.org/abs/2405.21075) ｜ StreamingBench — [https://arxiv.org/abs/2411.03628](https://arxiv.org/abs/2411.03628) ｜ EgoSchema — [https://arxiv.org/abs/2308.09126](https://arxiv.org/abs/2308.09126)

---

# Appendix B: A map of the VLM family (2023–2026)

> Two axes give the clearest view: **(1) how vision is attached** (the most explanatory one) and **(2) which family it comes from**. Future closed-source model numbers and benchmark scores are left out — second-hand and quick to rot — keeping only the stable facts about architecture and lineage.

## B.1 By how vision is attached (the main axis)

| Attachment | Representative | In one line |
|---|---|---|
| **MLP projector (shallow alignment)** | The whole LLaVA line, Qwen-VL, InternVL, Yi-VL | The mainstream: simple and scalable (question 20) |
| **Q-Former (query compression)** | BLIP-2 / InstructBLIP | Fixed queries extract few visual tokens, saving context |
| **Gated cross-attention** | Flamingo, Idefics | Visual attention layers inserted into a frozen LLM; good at interleaved input and few-shot |
| **Deep fusion (per-layer vision experts)** | CogVLM / CogAgent | Deeper alignment, strong grounding, but heavy |
| **Encoder-free** | Fuyu (Adept) | No separate ViT; patches are linearly projected into the LLM |
| **Codec-aligned sparsity** | LLaVA-OneVision-2 / OneVision-Encoder | Reads the codec to decide where to look (see the paper notes) |

## B.2 The open-weight families you will actually meet

| Model | Organisation | Why it is interesting |
|---|---|---|
| InternVL (1 → 2.5 → 3) | Shanghai AI Lab / OpenGVLab | Its own **InternViT-6B** vision tower; front rank among open models |
| Qwen-VL (2 / 2.5 / 3-VL) | Alibaba | **M-RoPE** plus dynamic resolution; strong on documents and video |
| Pixtral 12B / Large | Mistral | Native resolution, interleaved image-text, Apache-2.0 |
| Gemma 3 / PaliGemma | Google | Built on Gemma with a **SigLIP** encoder |
| Llama 3.2-Vision / Llama 4 | Meta | Native image understanding folded into Llama |
| Phi-3.5-V / Phi-4-multimodal | Microsoft | Small but capable; Phi-4 adds audio for an omni model |
| DeepSeek-VL2 / Janus-Pro | DeepSeek | VL2 is MoE; Janus targets unified understanding and generation |
| MiniCPM-V / -o | OpenBMB | Strong on-device; the -o variant adds audio |
| GLM-4V / CogVLM / CogAgent | Zhipu | CogAgent specialises in GUI agents (deep fusion) |
| Ovis2 / Idefics2-3 | Alibaba AIDC / Hugging Face | Ovis aligns visual and text embeddings tightly; Idefics is fully open |

## B.3 Fully open (weights, data and training code — for reproducible research)
- **Molmo** · Allen AI — strong pointing and grounding (it can point at regions), with the open PixMo dataset
- **NVLM** · NVIDIA

## B.4 Unified understanding and generation (axis three: one model that both sees and draws)

| Route | Mechanism | Public examples |
|---|---|---|
| **Unified discrete tokens** | Images are VQ-quantised into discrete tokens and predicted next-token alongside text | **Chameleon**, Emu3, **Janus-Pro** (decoupled encoders for understanding and generation) |
| **Diffusion + AR fusion** | Autoregression and diffusion inside one Transformer | **Transfusion**, Show-o |
| **Any-to-any omni** | A diffusion decoder on the output side for images, audio and video | **NExT-GPT**, AnyGPT, Qwen-Omni, Phi-4-multimodal |

## B.5 Closed-source frontier (direction only — check the vendor for model numbers and scores)
- GPT-4V → GPT-4o (OpenAI) ｜ Gemini 1.5/2.x long context (Google) ｜ Claude 3/3.5+ (Anthropic) ｜ Grok vision (xAI)
- ⚠️ This moves fast and second-hand sources are unreliable — check the vendor before putting it in anything formal.

## B.6 How the vision encoder is built (axis two: often overlooked)
- **A single CLIP/SigLIP**: the default.
- **Fusing several encoders** ⭐: **CLIP + DINOv2** together (semantics and dense detail complementing each other) → **Cambrian-1, Eagle, SPHINX, BRAVE**. A popular open direction.
- **A bigger vision tower**: InternViT-6B (InternVL) — make the eyes larger (questions 19b and 20).
- **Self-supervised dense features**: the DINOv2 family, stronger at localisation and segmentation.

## B.7 Alignment objectives (axis four: the training goal)
- **Contrastive (representation, no generation)**: CLIP / SigLIP / ALIGN — two-tower cosine alignment for retrieval and classification (questions 19 and 24).
- **Generative (looking and talking)**: the LLaVA family, next-token prediction (question 21).
