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
>
> **See also**: [Agent Notes](/agent/summary/)

---

# Part 0: The maths that runs through everything

> These quantities keep coming back: **cross-entropy** is the loss for pretraining and SFT, **KL divergence** is the term in RLHF/PPO/DPO/GRPO that keeps the policy from drifting, and distillation uses KL to align teacher and student. Getting them and their relationships straight here means not having to revisit them later.

### 0.1 How are cross-entropy, KL divergence and entropy related? ⭐ `#basics #core`
**【Core answer】** With a true distribution p and a model distribution q:
- **Entropy** $H(p) = -\sum_x p(x)\log p(x)$: p's own uncertainty — read it as **how many yes/no questions you need on average to pin down the outcome** (in bits, when $\log$ is base 2), which is also the lower bound on average code length under an optimal code.
  - For a feel: a fair six-sided die has $H=\log_2 6\approx 2.58$ bits; a die that always shows 1 has $H=0$ — the outcome is known, so nothing needs to be sent. **The flatter the distribution the higher the entropy, the peakier the lower.**
  - **Why information content is $-\log p$**: write the information in a single event as $I(x)$ and ask only three things of it — rarer means more, a certain event carries none ($I=0$), and **independent events add up**. The third is the binding one: independence means $p(x,y)=p(x)p(y)$, and the only function turning multiplication into addition is the logarithm, so $I(x)=-\log p(x)$ (negative because $p\le 1$ makes $\log$ negative). Entropy is then $I(x)$ averaged under p.
  - Another angle: an event of probability $1/2^k$ needs $k$ binary digits to identify, and $k=-\log_2 p$ — so $-\log_2 p$ literally counts **the bits it takes to name this outcome**. One coin, $p=1/2\to 1$ bit; two independent coins, $p=1/4\to 2$ bits, exactly additive.
- **Cross-entropy** $H(p,q) = -\sum_x p(x)\log q(x)$: **you believe the distribution is q and build your code for q, but reality is p** — this is the average code length you then pay.
  - For a feel: the same die, which you take to be fair (coding at 2.58 bits) when it is in fact heavily biased toward 1 (p is peaky) — you keep reserving code length for outcomes that almost never happen, and overpay every time.
  - In language-model terms: $-\log q(\text{correct word})$ is the model's **surprise** at that step, and averaging over positions gives the cross-entropy (see 0.2).
- **KL divergence** $D_{KL}(p\,\Vert \,q) = \sum_x p(x)\log\frac{p(x)}{q(x)}$: **exactly the overpayment above** — the extra cost of approximating p with q. The better q's guess, the less you overpay.

> **What "coding" and "code length" actually mean**: picture sending the outcome to someone over and over as 0s and 1s, wanting the average message to be as short as possible. The trick is to **give frequent outcomes short codewords and rare ones long codewords** (Morse code does exactly this: E, the commonest letter, is a single dot; Q takes four symbols). Total cost = Σ(frequency × code length), so short codes must go to frequent outcomes. The optimal allocation gives an outcome of probability $p(x)$ about $-\log_2 p(x)$ bits — which is where the entropy formula comes from.
>
> An example you can check by hand. Four outcomes A/B/C/D with true probabilities $p=(\tfrac12,\tfrac14,\tfrac18,\tfrac18)$:
>
> - **Optimal code** (knowing p): A=`0`, B=`10`, C=`110`, D=`111`, average length $=\tfrac12(1)+\tfrac14(2)+\tfrac18(3)+\tfrac18(3)=1.75$ bits → this is the **entropy**.
> - **Wrong code** (believing q is uniform): two bits for each, average length is always $2$ bits → this is the **cross-entropy**.
> - The overpayment, $2-1.75=0.25$ bits → is precisely the **KL**.
>
> Where it went wrong is easy to see: A shows up half the time yet was given 2 bits instead of 1, while C and D are rare and would happily have taken 3 — **the short codes went to the wrong outcomes**.

In one line: **cross-entropy = entropy + KL**, that is

  $$H(p,q) = H(p) + D_{KL}(p\,\Vert \,q)$$

**【How it works】**
- Because H(p) does not depend on the model's parameters (p is the fixed label distribution), **minimising cross-entropy is minimising KL** — which is why training uses cross-entropy directly as the loss.
- **KL is non-negative and asymmetric**: $D_{KL}(p\Vert q)\neq D_{KL}(q\Vert p)$, so it is a divergence, not a distance. $D_{KL}=0 \iff p=q$.
- What the asymmetry means in practice. One thing to fix first: **the first slot of $D_{KL}(a\Vert b)$ is the distribution the expectation is taken over**, i.e. $\mathbb{E}_{x\sim a}\big[\log\frac{a(x)}{b(x)}\big]$ — both cases below follow from that.
  - **Forward KL** $D_{KL}(p\Vert q)$ (what maximum likelihood uses): **sampling from p**. Wherever p has mass, q cannot be zero or the penalty is infinite → q tends to **cover every mode** (mean-seeking, and over-broad).
  - **Reverse KL** $D_{KL}(q\Vert p)$ (variational inference, some RL): **sampling from q**. q dares not go where p is low; but if it simply **stays away from a region where p is high, it never samples there and is never penalised** → it tends to **lock onto one mode** (mode-seeking).
  - A way to remember the direction: **forward punishes "missing what should be there", reverse punishes "having what should not be"** — the latter charges nothing for omission, which is why it is willing to contract.
  - **Who sits in which slot** (the easiest thing to lose track of, since the same $\pi_\theta$ sits on opposite sides in the two cases):
    - The definition at the top of this entry: $p$ = the true distribution, $q$ = the model.
    - SFT: $D_{KL}(p_{data}\Vert\pi_\theta)$ — **the model is on the right**, and the data on the left is the **target** to approach.
    - PPO / DPO: $D_{KL}(\pi_\theta\Vert\pi_{ref})$ — **the model is on the left**, and $\pi_{ref}$ on the right is not a target but a **constraint** (the actual target is the reward).
    - Note also that forward/reverse are **relative labels** and some papers define them the other way round; when writing, name the two slots explicitly, or use mass-covering / mode-seeking, which are unambiguous.
  - **Mapped onto LLM training, the two directions are exactly the two stages**:
    - **SFT = forward KL**. The SFT loss is cross-entropy over demonstration data, and since $H(p,q)=H(p)+D_{KL}(p\Vert q)$ (shown above) with $H(p_{data})$ independent of the parameters, minimising the SFT loss $\equiv$ minimising $D_{KL}(p_{data}\Vert\pi_\theta)$. Mass-covering means **every phrasing that appears in the demonstrations has to be given probability, even where they differ in style or contradict each other** — which is why an SFT'd model tends toward the safe, slightly-of-everything answer.
    - **Preference alignment uses reverse KL**. PPO's $\mathrm{KL}(\pi_\theta\Vert\pi_{ref})$ is estimated by sampling from **the policy itself**, so the direction is flipped; **DPO shares the same origin** — it is the closed-form solution of that same "maximise reward + reverse-KL constraint" objective, with $\beta$ playing the KL coefficient (the difference being that DPO is offline, so the constraint is baked into $\log\frac{\pi_\theta}{\pi_{ref}}$ rather than estimated by sampling; see question 10). Mode-seeking means the policy can **deliberately abandon** the modes of the reference model that do not score well and contract onto a few high-reward phrasings — which is both why RLHF sharpens answers and where its much-criticised **loss of diversity / entropy collapse** comes from.
  - One line to remember: **SFT learns to "resemble" (cover every demonstration), RLHF / DPO learn to be "good" (contract onto high-scoring modes)** — mathematically the difference is just the direction of the KL. (See questions 8, 9 and 10.)

<details markdown="1">
<summary><b>Worked derivation: how one-hot collapses the sum over the vocabulary</b></summary>

Written out in full, the SFT loss is a double sum over **positions × vocabulary**:

$$\mathcal{L}_{SFT}(\theta) = -\sum_{t=1}^{T}\sum_{v\in V} p_t(v)\,\log \pi_\theta(v\mid x, y_{<t})$$

Expanding the cross-entropy term by term at position $t$ (vocabulary $V=\{v_1,\dots,v_{\lvert V\rvert}\}$, true token $y_t$):

$$H(p_t,q_t) = -\big[\,p_t(v_1)\log q_t(v_1) + \cdots + p_t(y_t)\log q_t(y_t) + \cdots + p_t(v_{\lvert V\rvert})\log q_t(v_{\lvert V\rvert})\,\big]$$

Substituting the one-hot target ($p_t(y_t)=1$, everything else 0):

$$= -\big[\,0\cdot\log q_t(v_1) + \cdots + 1\cdot\log q_t(y_t) + \cdots + 0\cdot\log q_t(v_{\lvert V\rvert})\,\big] = -\log q_t(y_t)$$

The KL expands the same way. It needs the convention $0\log 0 = 0$ (because $\lim_{x\to 0}x\log x = 0$), so the zero terms genuinely **vanish** rather than being waved away:

$$D_{KL}(p_t\Vert q_t) = \sum_{v\in V} p_t(v)\log\frac{p_t(v)}{q_t(v)} = 1\cdot\log\frac{1}{q_t(y_t)} = -\log q_t(y_t)$$

And the entropy: $H(p_t) = -\big[\,0\log 0 + \cdots + 1\log 1 + \cdots\,\big] = 0$ (since $\log 1 = 0$). Substituting back checks the identity: $-\log q_t(y_t) = 0 + (-\log q_t(y_t))$.

**The point**: the inner sum is not "simplified" away — it is **multiplied away** by the one-hot target. So in practice you only need to pull out the one logit corresponding to the true token rather than walk the whole vocabulary, which is exactly what `cross_entropy(logits, labels)` does underneath. **Distillation**, by contrast, has a soft target where $p_t(v)$ is non-zero everywhere, nothing collapses, and the full vocabulary really does have to be summed.

</details>

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

### 1.1 How do you work out a model's parameter count? ⭐ `#basics #systems #core`
**【Core answer】** With hidden size $d$, $L$ layers and vocabulary $V$:

$$N \approx \underbrace{12\,L\,d^2}_{\text{the body}} + \underbrace{V d}_{\text{embeddings}}$$

That **12** comes from the two blocks in each layer: **attention $4d^2$** ($W_Q,W_K,W_V,W_O$, each $d\times d$) plus **FFN $8d^2$** (up-projection $d\times 4d$ and down-projection $4d\times d$). **Parameters grow quadratically in $d$ and only linearly in $L$** — which is why widening is far more expensive than deepening.

**【How it works】**
- Term by term, for a single layer:

| Component | Shape | Parameters |
|---|---|---|
| $W_Q,W_K,W_V,W_O$ | $d\times d$ each | $4d^2$ |
| FFN up-projection | $d\times d_{ff}$, $d_{ff}=4d$ | $4d^2$ |
| FFN down-projection | $d_{ff}\times d$ | $4d^2$ |
| LayerNorm / RMSNorm | two per layer, $d$ each | $\approx 2d$, negligible |
| **Per layer** | | $\mathbf{12d^2}$ |

- **Why SwiGLU does not change this number**: its FFN has three matrices ($W,V,W_2$) rather than two, so the inner dimension is set to $d_{ff}=\tfrac{2}{3}\times 4d$ to hold the parameter count steady — $3\times d\times\tfrac{8d}{3}=8d^2$, the same as a standard FFN (see 0.3). Implementations then round $d_{ff}$ up to a multiple of 256.
- **Check one: GPT-3 175B** ($L=96,\ d=12288,\ V=50257$, tied embeddings): the body is $12\times 96\times 12288^2 = 173.9\text{B}$ and the embeddings $50257\times 12288 = 0.62\text{B}$, for **174.6B total** — which is the published "175B".
- **Check two: LLaMA-7B** ($L=32,\ d=4096,\ V=32000,\ d_{ff}=11008$, SwiGLU, untied embeddings): per layer $4d^2+3d\,d_{ff}=0.202\text{B}$, body $6.476\text{B}$, embeddings $2\times 32000\times 4096=0.262\text{B}$, for **6.738B total** — against a published 6.74B. (Where $d_{ff}$ comes from: $\tfrac23\times4\times4096=10922.7$, rounded up to the multiple of 256, giving 11008.)
- **Three cases that need a correction**:
  - **GQA**: $W_K$ and $W_V$ shrink to $d\times d_{kv}$ (with $d_{kv}=\tfrac{h_{kv}}{h}d$), so attention drops from $4d^2$ to $2d^2+2d\,d_{kv}$. Models like LLaMA-3-70B only add up if you count this way.
  - **MoE**: each layer's FFN is replicated across $n$ experts, so **total** parameters scale with $n$ while **active** parameters count only the top-$k$. DeepSeek-V3's "671B total / 37B active" is exactly this (question 6).
  - **Tied embeddings**: whether the input embedding and the output LM head share weights changes the count by one $Vd$.

**【Trade-offs / follow-ups】**
- A common follow-up is **when the embeddings stop being negligible**: $Vd$ is a rounding error in a large model (0.35% of GPT-3) but can be **half of a small one** — at $d=768$ and $V=32000$, $Vd\approx 24.6\text{M}$ against a 12-layer body of only $12\times12\times768^2\approx 85\text{M}$. Shrinking the vocabulary really does pay off for on-device models.
- A common follow-up is **training compute**: $C \approx 6ND$ FLOP ($N$ parameters, $D$ training tokens), from roughly 2 FLOP forward and 4 FLOP backward per parameter per token. **For MoE, substitute the active parameters**, not the total. A 7B model on 2T tokens is $6\times 7\text{e}9\times 2\text{e}12 = 8.4\text{e}22$ FLOP.
- A common follow-up is **memory**: training with mixed precision and Adam runs about **16–20 bytes per parameter** — weights (fp16, 2) + gradients (fp16, 2) + Adam state (fp32 master 4, $m$ 4, $v$ 4) — plus activations, so full training of a 7B model needs 100+ GB and forces ZeRO or parallelism. Inference is parameters × bytes per parameter (fp16 = 2, int4 = 0.5) plus the **KV cache** (question 5).
- A common follow-up is **why this frames the "wider or deeper" question**: $N\propto Ld^2$, so widening costs quadratically; but depth lengthens the gradient path and adds pipeline-parallel bubbles. Configurations tend to keep $d/L$ in an empirical band (GPT-3 sits at $12288/96=128$).

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

### 8.1 What is on-policy distillation, and how does it differ from SFT / RFT / ordinary distillation? ⭐ `#alignment #core`
**【Core answer】** Sample a rollout from **the student itself**, and at every token it passes through ask the **teacher** for its full distribution, then minimise the KL between the two. In one line: **RL's way of sampling with distillation's density of supervision**.

**【How it works】**
- Four approaches fit into one 2×2, along two orthogonal axes:

| | Target is **one-hot** (hard labels) | Target is a **soft distribution** (teacher logits) |
|---|---|---|
| **On fixed / teacher data** (off-policy) | SFT on synthetic data (the Alpaca recipe) | **Ordinary KD** |
| **On the student's own generations** (on-policy) | **RFT / rejection-sampling fine-tuning** (question 8) | **On-policy distillation** |

- **The horizontal axis is how dense the supervision is.** A hard label tells you only which single word was correct at that position; a soft label hands over the probability of the whole vocabulary, which carries far more information. This is the same dividing line as the collapse in 0.1: a one-hot target **multiplies the vocabulary sum away**, while a soft distribution collapses nothing.
- **The vertical axis is whether the training distribution is the right one.** Training on fixed data means the student is always fed *someone else's good prefix*, yet at inference it has to continue its own — **exposure bias**: it has never been trained on its own mistakes, so one wrong step lands it in a state it has never seen and errors compound. Sampling from the student removes that mismatch by construction.
- **Against RL, it wins on supervision density**: GRPO/PPO spend a whole several-hundred-token trajectory to get back **one scalar** reward, leaving credit assignment to guesswork; on-policy distillation gets a full distribution at **every position** of that same trajectory. That is fundamentally why it costs less compute than RL.
- **Direction of the KL**: usually **reverse KL** $D_{KL}(\pi_{student}\Vert\pi_{teacher})$, computed over the student's rollouts. The mnemonic from 0.1 reads it off directly: the student is in the first slot → the expectation is over the student → on-policy; and reverse KL is mode-seeking → rather than spreading itself over all of the teacher's modes the student **picks one and does it well** — which for a student of much smaller capacity is more practical than forward KL's mass-covering (thin everywhere).
- **Self-distillation is a third axis** (the teacher *is* the student, or an earlier checkpoint of it), orthogonal to the two above: RFT is precisely "on-policy + hard labels + self-distillation". There is also **SDFT**, which has the model rewrite the target dataset in its own words before fine-tuning on it, keeping the training data close to the model's own distribution and **reducing catastrophic forgetting** (question 12).

**【Trade-offs / follow-ups】**
- The cost: **the teacher has to run forward passes throughout** (every step the student samples has to be scored), so it is more expensive in memory and compute than offline distillation, where teacher distributions can be precomputed and stored.
- A common follow-up is **which divergence to use**. The literature does not agree. GKD trains on student-generated sequences using a generalised Jensen-Shannon family that interpolates between forward and reverse KL; MiniLLM argues specifically for reverse KL when distilling LLMs.
- A common follow-up is **how it differs from RFT**: RFT keeps only whole trajectories that came out right and uses them as hard labels, so the signal stays sparse; on-policy distillation filters nothing and asks the teacher for a distribution at every token, so **even a wrong trajectory still supplies supervision** — the teacher points out which step should have been taken.
- A common follow-up is **where it sits in the training spectrum**: SFT (forward KL / data distribution / dense) → on-policy distillation (reverse KL / student distribution / dense) → RLHF and GRPO (reverse KL / student distribution / sparse reward). It fills exactly the gap between SFT and RL.

📖 Reference: GKD — [https://arxiv.org/abs/2306.13649](https://arxiv.org/abs/2306.13649) ｜ MiniLLM — [https://arxiv.org/abs/2306.08543](https://arxiv.org/abs/2306.08543)

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
- A common follow-up is **GRPO**: PPO simplified — the critic is dropped and replaced by a group-relative advantage; see question 9.1.

📖 Reference: InstructGPT — [https://arxiv.org/abs/2203.02155](https://arxiv.org/abs/2203.02155) ｜ GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300)

---

### 9.1 GRPO in detail: how the group advantage is computed, and how it reaches the loss ⭐ `#alignment #core`
**【Core answer】** GRPO is **PPO with the critic removed**. For one prompt it samples a group of G answers and uses the **group-normalised reward as the advantage** (the group mean *is* the baseline), then applies PPO's clipped objective. The mechanism worth understanding: the advantage is **one scalar per answer**, **broadcast to every token of that answer**, where it acts as a coefficient on the log-probability gradient.

**【How it works】**
- **Step 1: compute the advantage (at sequence level).** Sample $\{o_1,\dots,o_G\}$ for the same prompt and collect rewards $\{r_1,\dots,r_G\}$:

  $$\hat{A}_i = \frac{r_i - \mathrm{mean}(\{r_1,\dots,r_G\})}{\mathrm{std}(\{r_1,\dots,r_G\})}$$

  What comes out is **G scalars**, one per answer. PPO gets a **per-token** $A_t$ from its critic; GRPO has no critic, so there is **no token-level value estimate at all**.
- **Step 2: broadcast.** $\hat{A}_{i,t}=\hat{A}_i$ for every $t$ in $o_i$ — a 500-token answer hands **the same number** to all 500 positions.
- **Step 3: into the clipped objective** (with $\rho_{i,t}=\pi_\theta(o_{i,t}\mid x,o_{i,<t})/\pi_{old}(o_{i,t}\mid x,o_{i,<t})$):

  $$\mathcal{L} = \frac{1}{G}\sum_{i}\frac{1}{\lvert o_i\rvert}\sum_{t}\Big[\min\big(\rho_{i,t}\hat{A}_i,\ \mathrm{clip}(\rho_{i,t},1-\epsilon,1+\epsilon)\hat{A}_i\big) - \beta\,\mathbb{D}_{KL}[\pi_\theta\Vert\pi_{ref}]\Big]$$

- **What it actually does to the gradient.** $\hat{A}_i$ is a constant (it must be detached, and carries no gradient), so the gradient flows only through $\rho$; away from the clip:

  $$\nabla_\theta \mathcal{L} \approx \frac{1}{G}\sum_i\frac{1}{\lvert o_i\rvert}\sum_t \hat{A}_i\,\rho_{i,t}\,\nabla_\theta \log \pi_\theta(o_{i,t}\mid\cdot)$$

  So **the advantage's entire role is to multiply each token's log-probability gradient by a signed scalar**: $\hat{A}_i>0$ raises the probability of every token in that sequence, $<0$ lowers all of them. Structurally this is the same gradient as SFT's cross-entropy, only with a scalar in front — which is the policy-gradient identity $\nabla\mathbb{E}[R]=\mathbb{E}[R\nabla\log\pi]$ in the flesh.
- **A concrete number**: a group of four answers with rewards $[1,0,0,1]$ gives $\mathrm{mean}=0.5$, $\mathrm{std}=0.5$ and $\hat{A}=[+1,-1,-1,+1]$. Every token of the two correct answers gets $+1$, every token of the two wrong ones gets $-1$.
- **What the clip does**: once $\rho$ leaves $[1-\epsilon,1+\epsilon]$ in the direction that would push further, $\min$ selects the clipped branch, which is constant there and therefore has **zero gradient** — a token whose policy has already moved far from $\pi_{old}$ stops being pushed.
- **The KL sits somewhere different from PPO**: PPO folds the KL penalty **into the per-token reward**; GRPO adds it as a **separate regulariser directly in the loss**, which keeps the reward "clean" (purely about whether the answer is good) and lets the KL strength be tuned on its own. Implementations typically use the k3 estimator (unbiased and non-negative).

**【Trade-offs / follow-ups】**
- **The main limitation: credit assignment.** One scalar lands on every token, so nothing distinguishes which steps actually mattered — a 500-token chain that ends up correct has even its detours pushed up, while a wrong answer has its correct reasoning pushed down alongside the arithmetic slip that ruined it. This is exactly what motivates **process reward models (PRM)**, which score step by step, and **on-policy distillation**, which supplies a full distribution per token (question 8.1).
- **An implementation trap: a uniform group gives no signal.** If every reward in the group is identical (all right or all wrong), $\mathrm{std}=0$ and every $\hat{A}$ is 0, so **that group contributes no gradient at all** (implementations add an $\epsilon$ or skip the group). Questions that are too hard or too easy therefore waste sampling — GRPO needs spread within the group.
- A common follow-up is **the dispute over the two normalisations**: **Dr. GRPO** points out that dividing by $\lvert o_i\rvert$ thins the per-token penalty on long answers, which under $\hat{A}<0$ actively encourages padding wrong answers out; and dividing by $\mathrm{std}$ over-weights groups with little reward variance. Its fix is to drop both.
- A common follow-up is **whether the KL can go away under verifiable rewards**: for maths and code, where correctness is decided by a rule, some variants (**DAPO** among them) drop the KL term entirely — if the reward already *is* objective correctness, no reference model is needed to guard against reward hacking, and removing it lets the model travel further. The direction is still developing.
- A common follow-up is **why it suits reasoning tasks**: no reward model to train (the rule is the reward), no critic (a model the size of the policy saved), and group sampling fits maths and code naturally, where the same question can be attempted repeatedly and right/wrong separate on their own.

📖 Reference: GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300) ｜ DeepSeek-R1 — [https://arxiv.org/abs/2501.12948](https://arxiv.org/abs/2501.12948)

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
| **How the KL enters** | Folded into the per-token reward | **No explicit term** — absorbed into $\beta\log\frac{\pi_\theta}{\pi_{ref}}$ | **A separate regulariser in the loss** (k3 estimator) |
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
