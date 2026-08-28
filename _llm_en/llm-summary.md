---
title: "LLM Notes"
subtitle: "Architecture · Training & Alignment · Inference"
topic: llm
category: summary
order: 1
lang: en
pair: llm-summary
source: "LLM知识总结.md"
mathjax: true
---

* TOC
{:toc .llm-toc-list}

> **Scope**: architecture · training and alignment · inference optimisation. Every entry runs **core answer → how it works → trade-offs / follow-ups → references**; ⭐ marks the points worth digging into.

---

# Part 0: The maths that runs through everything

> These quantities keep coming back: **cross-entropy** is the loss for pretraining and SFT, **KL divergence** is the term in RLHF/PPO/DPO/GRPO that keeps the policy from drifting, and distillation uses KL to align teacher and student. Getting them and their relationships straight here means not having to revisit them later.

### 0.1 How are cross-entropy, KL divergence and entropy related? ⭐ `#basics #core`
**【Core answer】** With a true distribution p and a model distribution q:
- **Entropy** $H(p) = -\sum_x p(x)\log p(x)$: p's own uncertainty (the theoretical minimum code length).
- **Cross-entropy** $H(p,q) = -\sum_x p(x)\log q(x)$: the average cost of coding p using q.
- **KL divergence** $D_{KL}(p\,\Vert \,q) = \sum_x p(x)\log\frac{p(x)}{q(x)}$: the *extra* cost of approximating p with q.

In one line: **cross-entropy = entropy + KL**, that is

  $$H(p,q) = H(p) + D_{KL}(p\,\Vert \,q)$$

**【How it works】**
- Because H(p) does not depend on the model's parameters (p is the fixed label distribution), **minimising cross-entropy is minimising KL** — which is why training uses cross-entropy directly as the loss.
- **KL is non-negative and asymmetric**: $D_{KL}(p\Vert q)\neq D_{KL}(q\Vert p)$, so it is a divergence, not a distance. $D_{KL}=0 \iff p=q$.
- What the asymmetry means in practice:
  - **Forward KL** $D_{KL}(p\Vert q)$ (what maximum likelihood uses): wherever p has mass, q cannot be zero or the penalty is infinite → q tends to **cover every mode** (mean-seeking, and over-broad).
  - **Reverse KL** $D_{KL}(q\Vert p)$ (variational inference, some RL): q only dares place mass where p is high → it tends to **lock onto one mode** (mode-seeking).

**【Trade-offs / follow-ups】**
- A common follow-up is **how to symmetrise it**: the JS divergence is the average of KL in both directions, symmetric and bounded; GANs used it.
- A common follow-up is **what KL actually computes in an LLM**: the **per-position KL between two token distributions**. In PPO and DPO it constrains the new policy π_θ from straying too far from the reference π_ref, guarding against reward hacking (questions 9 and 10).

### 0.2 What does an LM's cross-entropy loss look like, and how does it relate to perplexity? ⭐ `#basics #core`
**【Core answer】** The true distribution is one-hot (the actual next word is 1, everything else 0), so cross-entropy collapses to **negative log-likelihood (NLL)** — only the probability the model assigned to the correct word matters.

  $$\mathcal{L} = -\frac{1}{T}\sum_{t=1}^{T}\log q_\theta(x_t \mid x_{<t})$$

**【How it works】**
- Under one-hot, $\sum_x p(x)\log q(x)$ keeps only the correct-class term, so cross-entropy = $-\log q(\text{correct word})$: the better the prediction (the closer to probability 1), the closer the loss to 0.
- **Perplexity** = $\exp(\mathcal{L})$, the exponential of cross-entropy. Read it as "how many words the model is torn between at each step on average" — lower is better.
- For classification, the gradient of softmax plus cross-entropy is beautifully simple: $\partial \mathcal{L}/\partial z_i = q_i - p_i$ (predicted probability minus true label), which is part of why it trains so well.

**【Trade-offs / follow-ups】**
- A common follow-up is **label smoothing**: replace the one-hot 1 with 1−ε and spread ε over the rest, which is equivalent to mixing a uniform distribution into the target. It reduces over-confidence and improves calibration.
- A common follow-up is **why distillation uses KL rather than cross-entropy**: the teacher outputs a *soft* distribution, not a one-hot label, and the student must match the whole thing — so minimise $D_{KL}(p_{teacher}\Vert q_{student})$ (softened with temperature T). Here KL ≠ cross-entropy, because the teacher's entropy is non-zero and cannot be dropped.

📖 Reference: cross-entropy and KL basics in *Deep Learning* (Goodfellow) Ch.3 ｜ Distillation — [https://arxiv.org/abs/1503.02531](https://arxiv.org/abs/1503.02531)

### 0.3 Activation functions, and why large models favour GLU variants ⭐ `#basics #core`
**【Core answer】** Activations supply **non-linearity**; without them stacked linear layers collapse back into one. The line runs Sigmoid/Tanh → ReLU → GELU/Swish → today's LLM default, **SwiGLU / GeGLU** (gated linear unit variants).

**【How it works】**

| Activation | Formula | Character / problem |
|------|------|-----------|
| Sigmoid | $\frac{1}{1+e^{-x}}$ | Output in (0,1); saturates at both ends → **vanishing gradients**, non-zero mean |
| Tanh | $\frac{e^x-e^{-x}}{e^x+e^{-x}}$ | Zero-mean, still saturates |
| ReLU | $\max(0,x)$ | Simple, non-saturating, fast to converge; but flat at zero on the negative side → **dying neurons** |
| LeakyReLU | $\max(\alpha x,x)$ | A small slope on the negative side eases the dying problem |
| GELU | $x\cdot\Phi(x)$ | Smooth weighting by the Gaussian CDF; common in BERT/GPT, smooth and differentiable |
| Swish/SiLU | $x\cdot\sigma(x)$ | Smooth and non-monotonic; strong in deep networks |
| **SwiGLU** | $(\mathrm{Swish}(xW)\otimes xV)W_2$ | **Gated**: one branch carries content, the other gates it elementwise; used by LLaMA and PaLM |

- **Why GLU variants (SwiGLU/GeGLU) win**: they turn the FFN from one path into two — content times gate, multiplied elementwise. **The gate lets the network decide dynamically how much of each dimension gets through**, which buys better quality at equal compute (the GLU Variants paper measured this).
- Note that a SwiGLU FFN has three weight matrices (W, V, W_2), so to hold parameter count steady the inner dimension is usually $\frac{2}{3}\times 4d$ rather than 4d.

**【Trade-offs / follow-ups】**
- A common follow-up is **why sigmoid is not used for hidden layers**: gradients vanish in the saturated region and its non-zero mean makes updates zig-zag, so deep networks are hard to train. Sigmoid now survives only in binary-classification outputs and gates.
- A common follow-up is **GELU vs. ReLU**: GELU is smooth, differentiable everywhere and slightly better in Transformers; ReLU is cheaper.

### 0.4 Optimisers: SGD → Adam → AdamW, and what large models use ⭐ `#basics #core`
**【Core answer】** The through-line is **momentum** (smooth the gradient direction) plus **adaptive learning rates** (scale each parameter separately). LLM training is essentially always **AdamW**.

**【How it works】**
- **SGD**: $\theta \leftarrow \theta - \eta\,g$ — simple, but sensitive to the learning rate and prone to oscillating in ravines.
- **With momentum**: keep an exponential moving average $v$ of past gradients to accelerate along a consistent direction and damp oscillation.
- **AdaGrad / RMSProp**: adapt the step size using accumulated squared gradients. AdaGrad's learning rate decays monotonically and can stall early; RMSProp fixes this with a moving average.
- **Adam = momentum + RMSProp**: maintain both a first moment $m_t$ (direction) and a second moment $v_t$ (scale), with bias correction:

  $$m_t=\beta_1 m_{t-1}+(1-\beta_1)g_t,\quad v_t=\beta_2 v_{t-1}+(1-\beta_2)g_t^2$$

  $$\hat m_t=\tfrac{m_t}{1-\beta_1^t},\ \hat v_t=\tfrac{v_t}{1-\beta_2^t},\quad \theta\leftarrow\theta-\eta\,\tfrac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}$$

- **AdamW**: **decouple weight decay from the gradient** and apply it straight to the weights ($\theta\leftarrow\theta-\eta(\dots)-\eta\lambda\theta$). In Adam, L2 regularisation gets rescaled by the adaptive denominator and stops working; AdamW fixes that, giving **cleaner regularisation and better generalisation**. It is the LLM standard.

**【Trade-offs / follow-ups】**
- A common follow-up is **why large models do not use SGD**: gradients are noisy and parameter scales vary widely, so adaptive methods converge faster and more stably. The price is storing both m and v, roughly **twice the parameter count in memory** (more under mixed precision) — exactly what ZeRO and optimiser-state sharding exist to address.
- A common follow-up is **the learning-rate schedule**: large models typically use **warmup plus cosine decay** — warmup keeps early large gradients from blowing up training, cosine anneals smoothly.
- A common follow-up is **newer optimisers**: **Lion** (first moment only, so lighter on memory), **Adafactor** (factorises the second moment to save memory; used by T5), and **Muon/Shampoo** (second-order / matrix preconditioning, tried in recent large models).

📖 Reference: Adam — [https://arxiv.org/abs/1412.6980](https://arxiv.org/abs/1412.6980) ｜ AdamW — [https://arxiv.org/abs/1711.05101](https://arxiv.org/abs/1711.05101) ｜ GLU Variants — [https://arxiv.org/abs/2002.05202](https://arxiv.org/abs/2002.05202)

---

# Part I: LLM fundamentals and architecture

### 1. What is at the core of the Transformer, and why did it displace the RNN? ⭐ `#basics #core`
**【Core answer】** Self-attention: every token interacts directly with every other token in the sequence, the path between any two positions is O(1) long, and the whole sequence computes in parallel.

**【How it works】**
- The RNN's two problems: (1) information has to be relayed step by step, so long-range dependencies vanish or explode during backpropagation; (2) timesteps are inherently serial, so nothing parallelises and training is slow.
- The Transformer establishes global connections in one step with attention, stabilises deep training with residual connections and LayerNorm, and scales with data and compute.

**【The overall structure, bottom-up】**
- **Input layer**: token embedding (look up an id as a vector) plus position encoding (question 3) → a sequence representation $X\in\mathbb{R}^{n\times d}$.
- **N stacked Transformer blocks** (96 layers in GPT-3, several dozen in LLaMA-3), each with two sublayers:
  1. **Multi-head self-attention (MHSA)**: `x → LN → MHSA → +x` (residual)
  2. **Feed-forward network (FFN/MLP)**: `x → LN → FFN → +x` (residual)
- **Output layer**: a final LN → linear projection to vocabulary size (the LM head, usually **weight-tied** with the input embedding) → softmax for the next-token distribution.
- The key tensor stays $n\times d$ throughout (n = sequence length, d = hidden size): attention mixes **between tokens** (across positions), the FFN transforms features **within each token** (position-wise). Alternating the two is the Transformer's basic rhythm.
- Inside one block: **multi-head self-attention + (residual & norm) + FFN + (residual & norm)**. The FFN is usually a two-layer MLP at 4× hidden width (modern models use SwiGLU, section 0.3) and carries most of the parameters — and most of the stored knowledge.

**【Residual connections: why they are indispensable】**
- The form: $\text{out} = x + \text{Sublayer}(\text{LN}(x))$ (Pre-LN style) — the sublayer only learns an **increment $F(x)$ relative to its input**, and output = input + increment.
- **Effect 1, deep gradients survive**: on the backward pass $\frac{\partial \text{out}}{\partial x} = 1 + \frac{\partial F}{\partial x}$, and that **"+1" gives the gradient a motorway straight down to the bottom layers**. Even when $\partial F/\partial x$ is tiny the gradient does not decay to zero, which is what makes tens or hundreds of layers trainable (the ResNet insight).
- **Effect 2, identity is easy to learn**: if the best thing a layer can do is nothing, the network only needs $F(x)\to 0$ — far easier than making a stack of non-linear layers fit the identity. So depth stops hurting.
- **Effect 3, information is preserved**: every layer carries the original signal through unchanged and adds to it, so deep layers cannot wash out the features below. Read it as **iterative refinement of a representation (the residual stream)** — which is why mechanistic interpretability treats the residual stream as a shared bus that every layer reads from and writes to.
- The companion **LayerNorm** normalises across each token's feature dimension, stabilising the numerics and speeding convergence; LLMs often use the cheaper **RMSNorm** (no mean centring, just scaling by root-mean-square).

**【Trade-offs / follow-ups】**
- The cost is attention's O(n²) complexity — both time and memory grow with the square of sequence length, the root of every long-sequence optimisation.
- A likely follow-up: **Pre-LN vs. Post-LN**. Post-LN (the original Transformer, `LN(x+Sublayer(x))`) is marginally more expressive but unstable deep and needs warmup; **Pre-LN** (`x+Sublayer(LN(x))`, normalising the sublayer's input) leaves the residual path a clean identity, trains more stably and can drop warmup. It is now the default.
- A likely follow-up: why does the FFN expand and then contract? To provide non-linear capacity and act as key-value memory.
- A likely follow-up: **what happens without residuals?** A deep Transformer barely converges at all — which is why residuals, normalisation and Pre-LN together are what makes the thing trainable.

📖 Reference: Attention Is All You Need — [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762) ｜ ResNet — [https://arxiv.org/abs/1512.03385](https://arxiv.org/abs/1512.03385)

---

### 2. Write self-attention from scratch and explain each step ⭐ `#implement #core`
**【Core answer】** Attention(Q,K,V) = softmax(QKᵀ / √dₖ) · V. Q, K and V come from multiplying the input by three learnable matrices; QKᵀ gives similarities, scaling then softmax turns them into weights, and those weights sum V.

**【How it works】**
- **Why divide by √dₖ**: when Q and K have roughly independent dimensions with mean 0 and variance 1, the dot product's variance is about dₖ. Larger dimensions mean larger dot products, which push softmax into saturation where gradients go to zero. Dividing by √dₖ pulls the variance back near 1 and keeps gradients healthy.
- **Multi-head attention**: split the d dimensions into h subspaces of d/h and attend in parallel, so different heads can track different relations (syntax, coreference, position), then concatenate and project.
- **Causal masking**: generative models set future positions to −∞ before the softmax, so token i can only see positions ≤ i.

**【Trade-offs / follow-ups】**
- A common follow-up is **complexity**: with sequence length n and dimension d, attention is O(n²·d).
- A common follow-up is **MHA vs. MQA vs. GQA**: see question 5.
- When writing it out, do not forget where the mask and dropout go, and that there is an output projection Wₒ at the end.

A skeleton (PyTorch pseudocode):
```python
def attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = (Q @ K.transpose(-2, -1)) / math.sqrt(d_k)  # [B, h, n, n]
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    attn = scores.softmax(dim=-1)
    return attn @ V
```

---

### 3. What position encodings exist, and why did RoPE win? ⭐ `#basics #core`
**【Core answer】** Attention itself is blind to position, so position has to be injected explicitly. Three families: absolute, relative and rotary (RoPE). RoPE became the default in LLaMA, Qwen and most open models because it **unifies absolute and relative position, extrapolates well, is simple to implement and adds no parameters**.

**【How it works】**
- **Absolute**: the original Transformer used sinusoids (parameter-free, extrapolates a little) or learned position vectors (BERT — fixed length, no extrapolation), added straight onto the embeddings.
- **RoPE**: rotate each token's Q and K by an angle determined by its position m (a 2D rotation applied to dimension pairs). Mathematically this makes ⟨q_m, k_n⟩ depend only on the relative distance (m−n), so relative position is encoded naturally inside the attention inner product.
- **ALiBi**: leaves Q/K alone and instead adds a bias to the attention scores that decreases linearly with distance (the further apart, the larger the penalty). No explicit position vectors, and it extrapolates well.

**【Trade-offs / follow-ups】**
- A common follow-up is **extrapolating to long context**: RoPE degrades if pushed past its training length, so **position interpolation (PI)** or **NTK-aware / YaRN** adjustments to the base frequency are used to extend it.
- A common follow-up is **the effect of RoPE's base (θ)**: a larger base discriminates better at long range, making it the key knob for long-context tuning.

📖 Reference: RoFormer (RoPE) — [https://arxiv.org/abs/2104.09864](https://arxiv.org/abs/2104.09864)

---

### 4. Decoder-only vs. encoder-only vs. encoder-decoder `#basics`
**【Core answer】** They differ in attention direction and structure: the encoder is bidirectional, the decoder is causal and unidirectional, encoder-decoder has both. Essentially every modern large model is decoder-only.

**【How it works】**
- **Encoder-only (BERT)**: bidirectional attention, every token sees the whole sequence. Strong on understanding tasks (classification, NER, retrieval); cannot generate directly.
- **Decoder-only (GPT/LLaMA)**: causal masking and autoregression, with next-token prediction as the single pretraining objective. Scales well, strong few-shot ability, and the current mainstream.
- **Encoder-decoder (T5/BART)**: the encoder understands the input and the decoder produces the output. Good for well-defined seq2seq work like translation and summarisation.

**【Trade-offs / follow-ups】**
- A common follow-up is **why everything converged on decoder-only**: one simple unified training objective, good zero- and few-shot generalisation, and a single consistent inference pattern to engineer around. Research also suggests that at scale, pure decoders match or beat the alternatives.
- A common follow-up is **PrefixLM**: a middle ground with bidirectional attention over the prompt and causal attention over the generated part.

📖 Reference: BERT — [https://arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805) ｜ GPT-3 — [https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

---

### 5. What is the KV cache, why is it the inference bottleneck, and how do MQA/GQA help? ⭐ `#systems #core`
**【Core answer】** During autoregressive generation the K and V of past tokens never change, so caching them avoids recomputation and drops per-step attention from O(n²) to O(n). The price is memory: KV cache ∝ batch × layers × sequence length × heads × head dimension.

**【How it works】**
- Without a KV cache, generating token t means recomputing attention over all t−1 previous tokens; with it, only the current token's attention against history is computed.
- Under long context and large batches the KV cache often consumes more memory than the model weights, making it the main bottleneck in the decode phase.
- **MQA (multi-query attention)**: all heads share one set of K/V, shrinking the cache by a factor of the head count at some cost to quality.
- **GQA (grouped-query attention)**: heads are split into g groups, each sharing one K/V set — a middle ground between MHA and MQA, adopted by LLaMA-2/3.

**【Trade-offs / follow-ups】**
- A common follow-up is **how to shrink the KV cache further**: quantise it (int8 KV cache), page it with PagedAttention (question 17), use sliding-window attention, or evict unimportant entries (H2O and similar).
- A common follow-up is **whether prefill needs the cache**: prefill computes the whole input in parallel once and writes K/V into the cache for decode to reuse.

**【Aside: how to measure an LLM serving stack】** — four families of metric:

- **Latency (what a single request feels like)**
  - **TTFT (time to first token)**: request to first token, determined mostly by **prefill**, affected by input length and whether the prefix cache hits. This is the "waiting" feeling.
  - **TPOT / ITL (time per output token / inter-token latency)**: the average gap between successive output tokens, determined mostly by **decode**. This is the "typing speed".
  - **End-to-end latency ≈ TTFT + TPOT × output tokens**. Use P50/P90/P99 rather than the mean — the tail is what users feel.

- **Throughput (cluster efficiency and cost)**
  - **Output tokens/s** (the usual one), **total tokens/s** (including input), **requests/s (QPS)**.
  - **Throughput and latency pull against each other**: a bigger batch (continuous batching) raises throughput but worsens per-request TPOT. Plot the throughput-latency curve and chase maximum throughput subject to the SLO.

- **Resources and cost**
  - **GPU utilisation (MFU)** and **memory footprint** (weights plus KV cache, which sets maximum concurrency and context length).
  - **\$ per 1M tokens** and **concurrent requests per GPU** map directly to deployment cost.
  - Rule of thumb: prefill is **compute-bound**, decode is **memory-bandwidth-bound**, so the two phases have different bottlenecks and different fixes — even separate deployment (PD disaggregation).

- **Quality and stability**
  - **Goodput**: not raw throughput but throughput that **meets the SLO** (TTFT < X s, TPOT < Y ms), which is much closer to real usable capacity.
  - Accuracy must not fall because of quantisation or speculative decoding, and **timeout rate, error rate and preemption/queueing delay** all deserve watching.

> A useful diagnostic habit: asked "the service got slow, how do you debug it", split by symptom — **high TTFT → look at prefill, queueing and prefix-cache hit rate**; **high TPOT → look at batch size, whether KV-cache memory is saturated, and whether requests are being preempted**.

📖 Reference: GQA — [https://arxiv.org/abs/2305.13245](https://arxiv.org/abs/2305.13245) ｜ vLLM/PagedAttention — [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180) ｜ DistServe (PD disaggregation) — [https://arxiv.org/abs/2401.09670](https://arxiv.org/abs/2401.09670)

---

### 6. Mixture of Experts: how it works, what it buys, what it costs ⭐ `#basics #systems`
**【Core answer】** Use many FFN "experts" and have a router pick the top-k for each token, activating them sparsely. Total parameters can be enormous while a single forward pass touches only a fraction, which expands model capacity at fixed compute.

**【How it works】**
- **The basic version (the Mixtral era)**: Mixtral 8×7B — 8 experts, top-2 per token, ~13B activated out of 47B total. The router is a linear layer plus softmax that picks and weights the top-k. A **load-balancing loss** prevents expert collapse, where the router keeps favouring a handful of experts.
- **Three modern upgrades (the DeepSeek line, 2024–2025)** ⭐:
  - **Fine-grained experts**: cut experts smaller and more numerous (8 of 64 rather than 2 of 8), giving more combinations and sharper specialisation.
  - **Shared experts**: keep one or two **always-on** experts for general knowledge, leaving the routed experts to specialise — which cuts redundancy.
  - **Auxiliary-loss-free balancing (DeepSeek-V3)**: give each expert a dynamically adjusted **bias**, lowered when it is overloaded, instead of a load-balancing loss that fights the main objective and costs quality.
- **Two routing paradigms**: **token-choice** (the mainstream — each token picks top-k, which can overflow an expert, so tokens beyond capacity are dropped or forwarded) versus **expert-choice** (each expert picks tokens, balanced by construction).
- **Representative models**: DeepSeek-V3 (671B total / 37B active), Mixtral, Qwen-MoE, Grok-1, DBRX, Llama 4, MiniMax.

**【Trade-offs / follow-ups】**
- The core value: **MoE decouples model capacity from per-token compute** — add experts to grow capacity while per-token computation stays roughly flat.
- **A clear win for training ✅**: lower loss at equal training compute, roughly a free 2–4× in effective capacity depending on configuration. The costs: all parameters occupy memory throughout, all-to-all communication, and less stable training.
- **A conditional win for inference ⚠️**: it **saves compute, not memory** — each token only computes the active parameters (cheap) but **every expert** must be resident (expensive).
  - 🟢 **High-concurrency batch serving**: compute-bound, so throughput is high, unit cost low, and the memory cost amortises. Worth it.
  - 🔴 **Small batch, low latency, single user, on-device**: memory-bandwidth-bound plus routing communication overhead, so the advantage shrinks or inverts — on-device workloads usually prefer a small dense model.
  - Note that **MoE does not lower the latency floor**. It wins on throughput and training cost, not on making one request faster.
- A common follow-up is **how MoE relates to parallelism**: **expert parallelism** places different experts on different devices and is the heart of distributed MoE, composed with TP/PP/DP. All-to-all is the main communication bottleneck.
- A common follow-up is **how you get an MoE**: train from scratch, or **upcycle** — clone a trained dense model's FFN into several experts and continue training, which is cheaper.

📖 Reference: Mixtral of Experts — [https://arxiv.org/abs/2401.04088](https://arxiv.org/abs/2401.04088) ｜ DeepSeekMoE — [https://arxiv.org/abs/2401.06066](https://arxiv.org/abs/2401.06066) ｜ DeepSeek-V3 — [https://arxiv.org/abs/2412.19437](https://arxiv.org/abs/2412.19437)
> ⚠️ DeepSeek-V3's 671B/37B figures follow public material; check the original report before relying on them.

---

### 7. Tokenization: how BPE works, and why numbers, Chinese and code cause trouble `#basics`
**【Core answer】** BPE (byte-pair encoding) starts from characters (or bytes) and repeatedly merges the most frequent adjacent pair in the corpus into a new token until the vocabulary reaches its target size. The result is a subword vocabulary balancing vocabulary size against out-of-vocabulary words.

**【How it works】**
- **BPE** merges greedily by frequency. **WordPiece** (BERT) picks merges by the language-model likelihood gain. **SentencePiece** trains directly on raw text, is language-agnostic and copes with languages that have no spaces. **Byte-level BPE** (GPT-2) works on bytes and can never, in principle, hit an OOV.
- A single Chinese character often splits into several tokens (UTF-8 is multi-byte), so character count ≠ token count and Chinese text usually costs more tokens.
- Numbers get split irregularly ("12345" may become "123" + "45"), which hurts arithmetic, and code's indentation and punctuation generate a lot of token fragments.

**【Trade-offs / follow-ups】**
- A common follow-up is **the vocabulary-size trade-off**: a larger vocabulary means shorter sequences but a bigger embedding matrix; a smaller one means longer sequences and more compute.
- A common follow-up is **why LLMs are bad at counting letters or reversing strings**: they see tokens, not characters.

---

# Part II: Training and alignment

### 8. What are the stages of training a large model? `#alignment #basics`
**【Core answer】** (1) Pretraining — next-token prediction over a vast unlabelled corpus, learning language and world knowledge; (2) SFT — supervised fine-tuning on instruction-response pairs, learning to follow instructions; (3) preference alignment — RLHF or DPO, shaping output toward human preference (helpful, harmless, honest).

**【How it works】**
- Pretraining consumes 99%+ of the compute and determines what the model *knows*.
- SFT changes *how it expresses itself and follows formats*. Small in volume, extremely demanding on quality.
- Alignment then tunes behavioural boundaries and preferences. Recent pipelines often add **continued pretraining** (domain strengthening) and **rejection-sampling fine-tuning (RFT)**.

**【Trade-offs / follow-ups】**
- A common follow-up is **which stage capability comes from**: knowledge and core ability come from pretraining; SFT and alignment mostly *elicit and align* rather than inject new knowledge — which is the basis for preferring RAG over fine-tuning when knowledge needs updating.

---

### 9. The full RLHF pipeline, and what hurts ⭐ `#alignment #core`
**【Core answer】** (1) Train a **reward model (RM)** on human rankings of several answers; (2) optimise the policy with **PPO** to maximise reward, with a **KL penalty** keeping it from drifting too far from the SFT model.

**【How it works】**
- The data: annotators rank several answers to the same prompt, and the RM learns to score that preference.
- The PPO stage holds four models at once: the policy (training), the reference (frozen SFT, for KL), the reward model (scoring) and the critic/value network (advantage estimation).
- The KL penalty is the load-bearing part: without it the policy will emit degenerate text purely to farm reward — **reward hacking**.

**【Formulas: RM and PPO】**
- **RM loss** (Bradley-Terry pairwise ranking, y_w preferred over y_l):

  $$\mathcal{L}_{RM} = -\,\mathbb{E}_{(x,y_w,y_l)}\big[\log \sigma\big(r_\theta(x,y_w) - r_\theta(x,y_l)\big)\big]$$

- **PPO objective** (KL-penalised reward with a clipped policy gradient):

  $$\max_{\pi_\theta}\ \mathbb{E}_{x,\,y\sim\pi_\theta}\Big[\,r_\phi(x,y) - \beta\,\mathrm{KL}\big(\pi_\theta(y\mid x)\,\Vert \,\pi_{ref}(y\mid x)\big)\Big]$$

  In practice the clipped form is used (A is the GAE advantage, r_t(θ)=π_θ/π_old the importance ratio):

  $$\mathcal{L}_{PPO} = \mathbb{E}_t\big[\min(r_t(\theta)\,A_t,\ \mathrm{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\,A_t)\big]$$

**【Trade-offs / follow-ups】**
- What hurts: the pipeline is complex, four models sit in memory at once, RL training is unstable, it is hyperparameter-sensitive, and the RM is easy to game.
- A common follow-up is **RLHF vs. RLAIF**: RLAIF replaces human preference labels with AI-generated ones (a stronger model, or a constitution), which lowers cost. Anthropic's Constitutional AI is the representative approach.
- A common follow-up is **GRPO** (introduced by DeepSeek, used in DeepSeekMath and R1): a simplification of PPO that **removes the critic/value network**, saving a model the size of the policy and improving both memory use and stability. It samples a group of G answers {o_1..o_G} for the same prompt and uses **group-normalised reward as the advantage**:

  $$\hat{A}_i = \frac{r_i - \mathrm{mean}(\{r_1,\dots,r_G\})}{\mathrm{std}(\{r_1,\dots,r_G\})}$$

  then applies PPO's clipped objective, adding KL as a **separate regulariser** in the loss rather than folding it into the reward. The upsides: no critic, and a natural fit for **verifiable-reward RL (RLVR)** where rules decide correctness in maths and code. The limits: it needs several samples per group, and it destabilises when reward variance is high.

📖 Reference: InstructGPT — [https://arxiv.org/abs/2203.02155](https://arxiv.org/abs/2203.02155) ｜ GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300)

---

### 10. What DPO gains over RLHF, and where it falls down ⭐ `#alignment #core`
**【Core answer】** DPO derives RLHF's objective into a **classification loss applied directly to preference data**. No separate reward model, no RL sampling loop — so it is more stable, cheaper and far easier to implement.

**【How it works】**
- The key insight: RLHF's optimal policy has a closed-form relationship with the reward, so "maximise reward subject to KL" can be reparameterised into something like a binary classification loss over (chosen, rejected) pairs, with the reward model absorbed *implicitly* into the policy.
- A reference model is still needed for the KL term, but the RM and PPO machinery disappear.

**【Formula: DPO】**
- From the RLHF optimum $\pi^*(y\mid x) \propto \pi_{ref}(y\mid x)\exp\big(\tfrac{1}{\beta}r(x,y)\big)$, invert to get the **implicit reward** $r(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{ref}(y\mid x)} + \beta\log Z(x)$, substitute into Bradley-Terry, and the partition term Z(x) cancels in the pairwise difference, leaving:

  $$\mathcal{L}_{DPO} = -\,\mathbb{E}_{(x,y_w,y_l)}\Big[\log \sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{ref}(y_w\mid x)} - \beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{ref}(y_l\mid x)}\Big)\Big]$$

  Read intuitively: **raise the chosen answer's log-probability ratio against the reference and push the rejected one down**, with β controlling how far the policy may stray (equivalent to RLHF's KL coefficient).

**【Trade-offs / follow-ups】**
- The limits: (1) it is **offline**, working from a fixed preference dataset, so it cannot sample online as PPO can and may have a lower ceiling; (2) it is sensitive to the preference-data distribution and prone to overfitting.
- A common follow-up is **the derivatives**: IPO (reduces overfitting), KTO (single good/bad labels instead of pairs), SimPO (drops the reference model), ORPO (merges SFT and preference alignment).

**【Side by side: PPO vs. DPO vs. GRPO】**

| Axis | PPO (RLHF) | DPO | GRPO |
|------|------------|-----|------|
| Paradigm | Online RL | Offline, direct preference optimisation | Online RL (simplified PPO) |
| Needs an RM? | ✅ Trained explicitly | ❌ Absorbed implicitly into the policy | ✅ (or rules / verifiable reward) |
| Needs a critic? | ✅ | ❌ | ❌ (group mean serves as baseline) |
| Models in training | 4 (policy/ref/RM/critic) | 2 (policy/ref) | 3 (policy/ref/RM) |
| Advantage estimate | GAE (from the critic) | None (direct classification loss) | Group-normalised reward |
| Memory / complexity | High | Low | Medium |
| Stability | Hyperparameter-sensitive, easily unstable | Stable, reproducible | Steadier than PPO, no critic |
| Online exploration | ✅ Higher ceiling | ❌ Bounded by the dataset | ✅ |
| Where it fits | General alignment, chasing the ceiling | Limited resources, fast alignment | Reasoning / maths / code (RLVR) |
| Representative | InstructGPT/ChatGPT | Zephyr and much open alignment | DeepSeekMath, DeepSeek-R1 |

> In one line: **PPO is the most general and the heaviest; DPO trades the entire RL pipeline for one classification loss — simple and stable, but offline; GRPO sits between them, keeping online RL and exploration while killing the critic with a group-relative advantage, which suits reasoning tasks that have verifiable rewards.**

📖 Reference: DPO — [https://arxiv.org/abs/2305.18290](https://arxiv.org/abs/2305.18290) ｜ GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300)

---

### 11. Why do models hallucinate, and what reduces it? ⭐ `#alignment #core`
**【Core answer】** The root cause is that the training objective optimises for a fluent, high-probability next token, not for factual correctness. When knowledge is missing, stale or long-tail, the model still prefers to invent something fluent rather than admit ignorance.

**【How it works】**
- Breaking down the sources: (1) the pretraining data is itself wrong or out of date; (2) long-tail knowledge is remembered imprecisely; (3) decoding randomness; (4) if SFT teaches the model to answer questions it does not actually know, it reinforces confident nonsense.
- Mitigations, by layer:
  - **Data and training**: raise data quality; during alignment, reward saying "I don't know" when uncertain, and reward citing sources.
  - **At inference**: RAG for external grounding and attribution, lower temperature, self-consistency (sample several times and vote), self-verification (have the model check its own answer).
  - **At the system level**: attach citations, confidence, and clickable provenance.

**【Trade-offs / follow-ups】**
- A common follow-up is **whether RAG eliminates hallucination**. It does not — it only reduces it. Bad or incomplete retrieval, or a model that ignores what was retrieved, still hallucinates.
- A common follow-up is **how to measure hallucination**: TruthfulQA, FActScore, and POPE for multimodal.

📖 Reference: RAG — [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

---

### 12. Handling catastrophic forgetting `#alignment`
**【Core answer】** Fine-tuning on a new task or domain degrades old abilities. The usual remedies: replay original data (mix general data back in), parameter-efficient fine-tuning (LoRA/adapters touch few parameters), a smaller learning rate, and regularisation (EWC constraining important parameters).

**【How it works】**
- Full fine-tuning forgets most readily; training only a side path (LoRA) preserves the original ability by construction.
- Continual learning usually mixes in a proportion of general corpus (5–30%, say) to anchor the original distribution.

**【Trade-offs / follow-ups】** A common follow-up is **how to choose the mixing ratio**: empirically, by experiment. Too much domain data and general ability erodes; too little and the domain barely improves.

---

### 13. How LoRA works, and what QLoRA adds ⭐ `#systems #core`
**【Core answer】** Freeze the original weight W and add a low-rank side path ΔW = B·A (A projects down to rank r, B projects back up, with r far below the original dimension), training only A and B. It rests on the assumption that weight updates are intrinsically low-rank.

**【How it works】**
- Trainable parameters drop from d×d to 2×d×r, orders of magnitude fewer; memory and storage fall sharply, and multiple LoRAs can be hot-swapped.
- At inference B·A can be merged back into W, so there is **no added latency**.
- Initialisation: A Gaussian, B zero, so ΔW = 0 at the start and the original model is untouched.
- **QLoRA**: quantise the base weights to 4-bit (NF4) and then apply LoRA, making it possible to fine-tune very large models on a single GPU. It introduced NF4, double quantisation and paged optimisers.

**【Trade-offs / follow-ups】**
- A common follow-up is **choosing rank r**: 8/16/32/64 are common. Larger means more expressive and closer to full fine-tuning; harder tasks want larger.
- A common follow-up is **LoRA's limits**: for tasks that require substantially changing the model's behaviour it can fall short of full fine-tuning.

📖 Reference: LoRA — [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685) ｜ QLoRA — [https://arxiv.org/abs/2305.14314](https://arxiv.org/abs/2305.14314)

---

# Part III: Inference and systems optimisation

### 14. Quantization: PTQ vs. QAT, and the common schemes `#systems`
**【Core answer】** Drop weights and activations from FP16 to INT8/INT4 or lower to save memory and go faster. Two families: post-training quantization (PTQ — no retraining, quick) and quantization-aware training (QAT — simulate quantization during training, better accuracy but expensive).

**【How it works】**
- **The PTQ mainstream**: GPTQ (minimise quantization error layer by layer, 4-bit weights), AWQ (identify and protect the channels of "important" weights), SmoothQuant (shift activation outliers into the weights so activations quantise more cleanly).
- The hard part is **activation outliers**: a few dimensions carry enormous values, and quantising them naively destroys accuracy. All the methods above are variations on handling this.
- Related notation: W4A16 (4-bit weights, 16-bit activations), and KV-cache quantization.

**【Trade-offs / follow-ups】** The core trade is accuracy loss against memory and speed. A common follow-up is **how much INT4 costs you**: 4-bit weight quantization typically loses very little (1–2%), which is why it is the sweet spot.

📖 Reference: GPTQ — [https://arxiv.org/abs/2210.17323](https://arxiv.org/abs/2210.17323) ｜ AWQ — [https://arxiv.org/abs/2306.00978](https://arxiv.org/abs/2306.00978)

---

### 15. What does FlashAttention actually solve? ⭐ `#systems #core`
**【Core answer】** It does **not reduce computation — it reduces memory traffic** (it is IO-aware). Standard attention writes the n×n attention matrix out to HBM and reads it back, so IO is O(n²). FlashAttention tiles the computation into fast SRAM and updates incrementally with online softmax, never materialising the full matrix.

**【How it works】**
- The key observation: modern GPUs compute fast and access memory slowly, so attention is **memory-bound**, not compute-bound.
- Online softmax: while computing tile by tile, maintain a running max and running sum and update the result incrementally, so no full row is ever needed at once.
- The result: faster *and* lighter on memory, while remaining **exact attention** — no approximation, no accuracy loss.
- What followed: FlashAttention-2 (better parallelism and work partitioning) and FlashAttention-3 (asynchrony and FP8 for H100).

**【Trade-offs / follow-ups】** A common follow-up is **how it differs from sparse or linear attention**: those approximate to reduce complexity and lose accuracy; FlashAttention is a lossless systems optimisation.

📖 Reference: FlashAttention — [https://arxiv.org/abs/2205.14135](https://arxiv.org/abs/2205.14135)

---

### 16. How does speculative decoding work? ⭐ `#systems`
**【Core answer】** A small **draft model autoregressively guesses several tokens quickly**, then the large model **verifies them in a single parallel forward pass**, accepting the matching prefix and resampling from the first mismatch. Confirming several tokens per large-model pass raises throughput.

**【How it works】**
- One forward pass over a sequence gives the large model a probability distribution at every position, which is exactly what is needed to check the draft's guesses in bulk.
- A carefully designed accept/resample rule guarantees the final output distribution is **exactly** what the large model alone would have produced — lossless acceleration.
- Variants: Medusa (extra prediction heads on the large model so it drafts for itself, no separate small model), EAGLE (drafting in feature space for higher accuracy), Lookahead Decoding.

**【Trade-offs / follow-ups】** Speedup depends on the draft's hit rate and the size gap between the two models; a draft that is too weak gets rejected often and buys little. A common follow-up is **where it pays**: small batches and latency-sensitive serving.

📖 Reference: Speculative Decoding — [https://arxiv.org/abs/2211.17192](https://arxiv.org/abs/2211.17192)

---

### 17. What raises inference throughput? `#systems`
**【Core answer】** Continuous batching (splice requests in dynamically), PagedAttention (paged KV-cache management), prefix caching (reuse the KV of shared prefixes), tensor and pipeline parallelism, quantization, and speculative decoding.

**【How it works】**
- **Continuous batching**: a static batch has to wait for its slowest request before admitting new ones; continuous batching swaps finished requests for new ones every step, sharply raising GPU utilisation.
- **PagedAttention** (vLLM): borrow virtual-memory paging from operating systems — cut the KV cache into fixed-size blocks and map them through a page table onto non-contiguous memory. Fragmentation nearly vanishes, and KV can be shared between requests (an identical system prompt, for example).
- **Prefix caching**: when several requests share a prefix, compute it once.

**【Trade-offs / follow-ups】** A common follow-up is **the throughput-versus-latency trade**: bigger batches raise throughput but lengthen per-request latency, and online serving has to pick a point between them.

📖 Reference: vLLM / PagedAttention — [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180)

---

### 18. How do prefill and decode fundamentally differ? `#systems #core`
**【Core answer】** Prefill processes the input prompt with every token in parallel and is **compute-bound**. Decode generates one token at a time, computing that single token's attention over all history each step, and is **memory-bound**, limited by the bandwidth of reading the KV cache.

**【How it works】**
- This explains why long inputs (heavy prefill) and long outputs (many decode steps) call for different optimisations.
- Metrics: prefill drives **TTFT**, decode drives **TPOT and throughput**.
- In practice the two are often **scheduled separately** (disaggregated serving, with prefill and decode on different nodes) so each can be optimised on its own terms.

**【Trade-offs / follow-ups】** A common follow-up is **chunked prefill**: split a long prefill into chunks and interleave it with decode, balancing TTFT against throughput.

---

# Part VI: Open-ended questions

> These have no standard answer. What they test is judgement and the ability to talk about trade-offs.

- **Is longer context always better?** No. Long context suffers "lost in the middle" (information in the middle gets overlooked), costs more to run as it grows, and dilutes attention. RAG and long context complement rather than replace one another: choose RAG when you need attribution, lower cost, or frequently updated knowledge; choose long context when the information genuinely has to be read as a whole, like a long contract.

- **RAG or fine-tuning?** Frequently updated knowledge, attribution, less hallucination → RAG. Changing style, format or output habits, or instilling stable domain skill → fine-tuning. The two are often combined, with fine-tuning teaching the model to use retrieved material better. In one line: RAG changes **what the model knows**, fine-tuning changes **how it behaves**.

- **How do you set temperature and top-p?** Temperature scales the softmax's smoothness and thus randomness (low → deterministic, high → divergent); top-p (nucleus sampling) samples only from the token set whose cumulative probability reaches p, truncating the tail. Low temperature for factual and code tasks, high for creative work. The two are not usually pushed hard at the same time.

- **What are scaling laws, and what did Chinchilla teach us?** Performance improves as a power law in parameters N, data D and compute C. Chinchilla pointed out that most large models of the time were **too big and under-fed**: at fixed compute, N and D should grow together (empirically about 20 tokens per parameter), and a smaller, well-fed model beats a larger, starved one at equal compute.

- **How do you compress a large model for production?** A combination: quantization (4-bit weights) + distillation (a large model teaching a small one) + pruning + inference-engine optimisation (vLLM, TensorRT-LLM). Trade against latency, cost and accuracy targets — set the SLA first, then choose.

📖 Reference: Scaling Laws — [https://arxiv.org/abs/2001.08361](https://arxiv.org/abs/2001.08361) ｜ Chinchilla — [https://arxiv.org/abs/2203.15556](https://arxiv.org/abs/2203.15556)
