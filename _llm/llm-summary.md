---
layout: llm-doc
title: "LLM 知识总结"
subtitle: "基础架构 · 训练对齐 · 推理优化"
topic: llm
category: summary
order: 1
permalink: /llm/summary/
lang: zh
pair: llm-summary
source: "LLM知识总结.md"
highlights: "交叉熵与 KL 散度 · Transformer 与 self-attention · RoPE · KV Cache 与 MQA/GQA · MoE · RLHF 与 DPO · LoRA/QLoRA · 量化 · Flash Attention · 推测解码 · Prefill 与 Decode · Scaling Law"
title_en: "LLM Notes"
subtitle_en: "Architecture · Training &amp; Alignment · Inference"
highlights_en: "Cross-entropy and KL divergence · Transformer and self-attention · RoPE · KV cache, MQA/GQA · MoE · RLHF and DPO · LoRA/QLoRA · Quantization · FlashAttention · Speculative decoding · Prefill vs. decode · Scaling laws"
mathjax: true
---

* TOC
{:toc .llm-toc-list}

> **定位**：基础架构 · 训练对齐 · 推理优化。每个条目按 **核心答案 → 深入原理 → 权衡 / 追问 → 参考** 组织，⭐ 标记值得重点深挖的地方。
> 
> **配套**：[Agent 知识总结](/agent/summary/)

---

# 第零部分：数学基础（贯穿全篇）

> 这几个量在后面反复出现：**交叉熵**是预训练/SFT 的损失，**KL 散度**是 RLHF/PPO/DPO/GRPO 里约束策略别跑偏的核心项，蒸馏里又用 KL 对齐师生分布。先把它们和彼此的关系讲清楚，后面就不再展开。

### 0.1 交叉熵、KL 散度、熵三者什么关系？⭐ `#基础 #高频`
**【核心答案】** 设真实分布 p、模型分布 q：
- **熵** $H(p) = -\sum_x p(x)\log p(x)$：p 自身的不确定性——直观理解为**平均要问多少个「是/否」问题才能确定结果**（$\log$ 取 2 为底时单位是 bit），也等于最优编码下的平均码长下界。
  - 找手感：均匀的 6 面骰子 $H=\log_2 6\approx 2.58$ bit；若骰子必定掷出 1，则 $H=0$——结果已知，不需要传任何信息。**分布越平熵越大，越尖熵越小。**
  - **为什么信息量是 $-\log p$**：把单个事件的信息量记作 $I(x)$，只要求三件事——越罕见信息越多、必然事件 $I=0$、**独立事件的信息量可相加**。第三条最关键：独立时 $p(x,y)=p(x)p(y)$，而能把乘法变加法的函数只有对数，于是 $I(x)=-\log p(x)$（负号是因为 $p\le 1$、$\log$ 为负）。熵就是 $I(x)$ 按 p 加权的平均。
  - 换个角度：概率为 $1/2^k$ 的事件要 $k$ 个二进制位才能指认，而 $k=-\log_2 p$——所以 $-\log_2 p$ 字面意思就是「点名这个结果要几个 bit」。1 枚硬币 $p=1/2\to 1$ bit，2 枚独立硬币 $p=1/4\to 2$ bit，正好相加。
- **交叉熵** $H(p,q) = -\sum_x p(x)\log q(x)$：**你以为分布是 q，照着 q 设计编码，但真实分布其实是 p** —— 此时的平均码长。
  - 找手感：还是那颗骰子，你以为它均匀（按 2.58 bit 编码），实际它极偏向掷出 1（p 很尖）——那你每次都在为一个几乎不会发生的结果预留码长，白白多付。
  - 换成语言模型：$-\log q(\text{正确词})$ 就是模型这一步的「意外程度」，对所有位置取平均就是交叉熵（见 0.2）。
- **KL 散度** $D_{KL}(p\,\Vert \,q) = \sum_x p(x)\log\frac{p(x)}{q(x)}$：**上面「多付」的那部分**——用 q 近似 p 的额外代价。q 猜得越准，多付越少。

> **「编码 / 码长」是什么意思**：想象你要反复把结果用 0/1 发给别人，希望平均发得越短越好。办法是**常出现的结果给短码，罕见的给长码**（摩斯电码就是这样：E 最常用，是一个点；Q 是四个符号）。总代价 = Σ(出现频率 × 码长)，所以短码要留给高频结果。最优分配是给概率 $p(x)$ 的结果约 $-\log_2 p(x)$ 位——熵的公式就是这么来的。
>
> 一个能自己验算的例子。四个结果 A/B/C/D，真实概率 $p=(\tfrac12,\tfrac14,\tfrac18,\tfrac18)$：
>
> - **最优编码**（知道 p）：A=`0`、B=`10`、C=`110`、D=`111`，平均码长 $=\tfrac12(1)+\tfrac14(2)+\tfrac18(3)+\tfrac18(3)=1.75$ bit → 这就是**熵**。
> - **用错的编码**（以为 q 均匀）：每个都分 2 位，平均码长恒为 $2$ bit → 这就是**交叉熵**。
> - 多付的 $2-1.75=0.25$ bit → 正是 **KL**。
>
> 错在哪很直观：A 有一半时间出现却被分了 2 位而非 1 位，C/D 很罕见、给 3 位本来不亏却也占了 2 位——**短码没给对人**。

三者关系一行话：**交叉熵 = 熵 + KL**，即

  $$H(p,q) = H(p) + D_{KL}(p\,\Vert \,q)$$

**【深入】**
- 因为 H(p) 与模型参数无关（p 是固定的真实标签分布），**最小化交叉熵 ⇔ 最小化 KL**——这就是为什么训练直接用交叉熵当 loss。
- **KL 非负、不对称**：$D_{KL}(p\Vert q)\neq D_{KL}(q\Vert p)$，所以它是「散度」不是「距离」。$D_{KL}=0 \iff p=q$。
- 不对称的实际含义。先记一条：**$D_{KL}(a\Vert b)$ 的第一个位置就是取期望的分布**，即 $\mathbb{E}_{x\sim a}\big[\log\frac{a(x)}{b(x)}\big]$——下面两条都能由它推出来。
  - **Forward KL** $D_{KL}(p\Vert q)$（最大似然用的）：**从 p 采样**。p 有质量处 q 不能为 0，否则惩罚无穷 → q 倾向「覆盖所有模式」（mean-seeking，分布偏胖）。
  - **Reverse KL** $D_{KL}(q\Vert p)$（变分推断、部分 RL 用）：**从 q 采样**。q 不敢跑到 p 低的地方；但它**若干脆不去 p 高的某个区域，就永远采样不到那里、也就不受罚** → 倾向「锁定单一模式」（mode-seeking）。
  - 记方向：**forward 罚「该有的没有」，reverse 罚「不该有的有」**——后者对「遗漏」免罚，所以敢收缩。
  - **谁坐哪个位置**（这里最容易绕，因为同一个 $\pi_\theta$ 在两处坐的位置相反）：
    - 本条开头的定义：$p$ ＝ 真实分布，$q$ ＝ 模型。
    - SFT：$D_{KL}(p_{data}\Vert \pi_\theta)$ —— **模型在右边**，左边的数据是要逼近的**目标**。
    - PPO / DPO：$D_{KL}(\pi_\theta\Vert \pi_{ref})$ —— **模型在左边**，右边的 $\pi_{ref}$ 不是目标而是**约束**（真正的目标是 reward）。
    - 另外 forward / reverse 是**相对叫法**，不同文献可能定义相反；写作时直接写清两个位置上是谁，或用 mass-covering / mode-seeking 这类描述行为的说法，不会有歧义。
  - **落到 LLM 训练上，两个方向正好对应两个阶段**：
    - **SFT ＝ forward KL**。SFT 的损失就是在示范数据上算交叉熵，而上面已证 $H(p,q)=H(p)+D_{KL}(p\Vert q)$、$H(p_{data})$ 与参数无关，所以最小化 SFT 损失 $\equiv$ 最小化 $D_{KL}(p_{data}\Vert \pi_\theta)$。mass-covering 的后果是：**示范里出现过的说法模型都得分概率，哪怕它们风格不一甚至互相矛盾**——这是 SFT 出来的模型容易四平八稳、什么都沾一点的原因。
    - **偏好对齐用的是 reverse KL**。PPO 里的 $\mathrm{KL}(\pi_\theta\Vert \pi_{ref})$ 从**策略自己**采样估计，方向反了过来；**DPO 与之同源**——它正是把「奖励最大化 ＋ reverse KL 约束」这个目标闭式求解，$\beta$ 扮演的就是 KL 系数（区别在于 DPO 是离线的，约束隐含在 $\log\frac{\pi_\theta}{\pi_{ref}}$ 里，而非靠采样估计，见第 10 题）。mode-seeking 的后果是：策略可以**主动放弃**参考模型里那些拿不到高分的模式，收缩到少数高奖励表达上——这既是 RLHF 让回答变「锐利」的原因，也是它常被诟病的**多样性下降 / 熵坍缩**的来源。
  - 一句话记：**SFT 学「像」（覆盖全部示范），RLHF / DPO 学「好」（收缩到高分模式）**——差别在数学上就是 KL 的方向。（见第 8、9、10 题）

<details markdown="1">
<summary><b>展开推导：one-hot 如何让词表求和塌缩</b></summary>

严格写出来，SFT 损失是**位置 × 词表**的双重求和：

$$\mathcal{L}_{SFT}(\theta) = -\sum_{t=1}^{T}\sum_{v\in V} p_t(v)\,\log \pi_\theta(v\mid x, y_{<t})$$

在位置 $t$ 上把交叉熵逐项摊开（词表 $V=\{v_1,\dots,v_{\lvert V\rvert}\}$，真实词为 $y_t$）：

$$H(p_t,q_t) = -\big[\,p_t(v_1)\log q_t(v_1) + \cdots + p_t(y_t)\log q_t(y_t) + \cdots + p_t(v_{\lvert V\rvert})\log q_t(v_{\lvert V\rvert})\,\big]$$

代入 one-hot（$p_t(y_t)=1$，其余为 0）：

$$= -\big[\,0\cdot\log q_t(v_1) + \cdots + 1\cdot\log q_t(y_t) + \cdots + 0\cdot\log q_t(v_{\lvert V\rvert})\,\big] = -\log q_t(y_t)$$

KL 同样展开。这里要用约定 $0\log 0 = 0$（因为 $\lim_{x\to 0}x\log x = 0$），所以零项是**真的消失**，不是被忽略：

$$D_{KL}(p_t\Vert q_t) = \sum_{v\in V} p_t(v)\log\frac{p_t(v)}{q_t(v)} = 1\cdot\log\frac{1}{q_t(y_t)} = -\log q_t(y_t)$$

熵同理：$H(p_t) = -\big[\,0\log 0 + \cdots + 1\log 1 + \cdots\,\big] = 0$（$\log 1 = 0$）。代回恒等式即可验证 $-\log q_t(y_t) = 0 + (-\log q_t(y_t))$。

**关键**：内层求和不是被「简化」掉的，是被 one-hot **乘没了**。所以工程上只需从 logits 里取出真实 token 对应的那一个数，不必遍历整个词表——`cross_entropy(logits, labels)` 底层就是这么做的。而**蒸馏**的目标是软分布，$p_t(v)$ 处处非零，内层求和一项都塌缩不了，必须真把整排词表加起来。

</details>

**【权衡 / 追问】**
- 追问 **为什么对称化**：JS 散度 = 两个方向 KL 的平均，对称且有界，GAN 里用过。
- 追问 KL 在 LLM 里具体算什么：是**两个 token 分布的逐位置 KL**，PPO/DPO 里约束「新策略 π_θ 别偏离参考策略 π_ref 太远」，防止 reward hacking（见第 9、10 题）。

### 0.2 语言模型的交叉熵损失长什么样？和困惑度什么关系？⭐ `#基础 #高频`
**【核心答案】** 真实分布是 one-hot（真实下一个词 = 1，其余 = 0），所以交叉熵退化成**负对数似然（NLL）**：只看「模型给正确词的概率」。

  $$\mathcal{L} = -\frac{1}{T}\sum_{t=1}^{T}\log q_\theta(x_t \mid x_{<t})$$

**【深入】**
- one-hot 下 $\sum_x p(x)\log q(x)$ 只剩正确类那一项，所以交叉熵 = $-\log q(\text{正确词})$，预测得越准（概率越接近 1）loss 越接近 0。
- **困惑度（Perplexity）** = $\exp(\mathcal{L})$，即交叉熵的指数，直观理解为「模型在每步平均在多少个词里纠结」，越低越好。
- 分类任务里 softmax + 交叉熵的梯度极简洁：$\partial \mathcal{L}/\partial z_i = q_i - p_i$（预测概率 − 真实标签），这也是它好训练的原因。

**【权衡 / 追问】**
- 追问 **label smoothing**：把 one-hot 的 1 改成 1−ε、其余分一点 ε，等价于给目标分布掺入均匀分布，缓解过度自信、改善校准。
- 追问 **蒸馏（distillation）为何用 KL 而非交叉熵**：教师输出是「软分布」而非 one-hot，要让学生匹配整个分布，所以最小化 $D_{KL}(p_{teacher}\Vert q_{student})$（带温度 T 软化）——这里 KL ≠ 交叉熵，因为教师熵不为 0、不可忽略。

📖 参考：交叉熵/KL 基础见《Deep Learning》(Goodfellow) Ch.3 ｜ 蒸馏 — [https://arxiv.org/abs/1503.02531](https://arxiv.org/abs/1503.02531)

### 0.3 常见激活函数与选型？为什么大模型爱用 GLU 变体？⭐ `#基础 #高频`
**【核心答案】** 激活函数提供**非线性**，否则多层线性叠加仍等价于一层。从 Sigmoid/Tanh → ReLU → GELU/Swish → 现在 LLM 主流的 **SwiGLU / GeGLU**（门控线性单元变体）。

**【深入】**

| 激活 | 公式 | 特点 / 问题 |
|------|------|-----------|
| Sigmoid | $\frac{1}{1+e^{-x}}$ | 输出(0,1)；两端饱和→**梯度消失**，非零均值 |
| Tanh | $\frac{e^x-e^{-x}}{e^x+e^{-x}}$ | 零均值、仍饱和 |
| ReLU | $\max(0,x)$ | 简单、不饱和、收敛快；但负区恒 0→**神经元死亡** |
| LeakyReLU | $\max(\alpha x,x)$ | 负区给小斜率，缓解死亡 |
| GELU | $x\cdot\Phi(x)$ | 用高斯 CDF 平滑加权，BERT/GPT 常用，平滑可导 |
| Swish/SiLU | $x\cdot\sigma(x)$ | 平滑、非单调，深层表现好 |
| **SwiGLU** | $(\mathrm{Swish}(xW)\otimes xV)W_2$ | **门控**：一支做内容、一支做门控相乘；LLaMA/PaLM 采用 |

- **GLU 变体（SwiGLU/GeGLU）凭什么强**：把 FFN 从「一条路」变成「内容 × 门控」两条路逐元素相乘，**门控让网络动态决定每个维度放多少信息通过**，同等算力下质量更好（GLU Variants 论文实验证实）。
- 注意 SwiGLU 的 FFN 有 3 个权重矩阵（W, V, W_2），为保持参数量持平，中间维度常取 $\frac{2}{3}\times 4d$ 而非 4d。

**【权衡 / 追问】**
- 追问 **为什么不用 Sigmoid 当隐藏层激活**：饱和区梯度趋 0、非零均值导致梯度更新呈锯齿，深层难训；现在 Sigmoid 只用在二分类输出或门控。
- 追问 GELU vs ReLU：GELU 平滑、处处可导、在 Transformer 上略优；ReLU 更省算力。

### 0.4 优化器演进：SGD → Adam → AdamW，大模型怎么选？⭐ `#基础 #高频`
**【核心答案】** 主线是「**动量**（平滑梯度方向）+ **自适应学习率**（每个参数各自缩放）」。LLM 训练几乎默认 **AdamW**。

**【深入】**
- **SGD**：$\theta \leftarrow \theta - \eta\,g$，简单但对学习率敏感、易在沟壑震荡。
- **+ Momentum**：累积历史梯度的指数滑动平均 $v$，沿一致方向加速、抑制震荡。
- **AdaGrad / RMSProp**：用历史梯度平方做自适应步长；AdaGrad 学习率单调衰减易过早停，RMSProp 用滑动平均修正。
- **Adam = Momentum + RMSProp**：同时维护一阶矩 $m_t$（方向）和二阶矩 $v_t$（尺度），加偏差校正：

  $$m_t=\beta_1 m_{t-1}+(1-\beta_1)g_t,\quad v_t=\beta_2 v_{t-1}+(1-\beta_2)g_t^2$$

  $$\hat m_t=\tfrac{m_t}{1-\beta_1^t},\ \hat v_t=\tfrac{v_t}{1-\beta_2^t},\quad \theta\leftarrow\theta-\eta\,\tfrac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}$$

- **AdamW**：把 **weight decay 从梯度里解耦**出来，直接作用在权重上（$\theta\leftarrow\theta-\eta(\dots)-\eta\lambda\theta$）。Adam 里 L2 正则会被自适应分母缩放而失效，AdamW 修正了这点，**正则更干净、泛化更好**，是 LLM 标配。

**【权衡 / 追问】**
- 追问 **为什么大模型不用 SGD**：梯度噪声大、各参数尺度差异大，自适应方法收敛更稳更快；代价是 Adam 要存 m、v 两份状态，**显存约为参数量的 2 倍**（混合精度下更多），这也是 ZeRO/优化器状态切分要解决的问题。
- 追问学习率调度：大模型常用 **warmup + cosine 衰减**——warmup 防早期大梯度炸训，cosine 平滑退火。
- 追问新优化器：**Lion**（只存一阶动量、更省显存）、**Adafactor**（分解二阶矩省显存，T5 用）、**Muon/Shampoo**（二阶/矩阵预条件，近年大模型尝试）。

📖 参考：Adam — [https://arxiv.org/abs/1412.6980](https://arxiv.org/abs/1412.6980) ｜ AdamW — [https://arxiv.org/abs/1711.05101](https://arxiv.org/abs/1711.05101) ｜ GLU Variants — [https://arxiv.org/abs/2002.05202](https://arxiv.org/abs/2002.05202)

---

# 第一部分：LLM 基础与架构

### 1. Transformer 的核心是什么？为什么能取代 RNN？⭐ `#基础 #高频`
**【核心答案】** 核心是 self-attention：每个 token 能直接与序列中所有 token 交互，任意两个位置的路径长度为 O(1)，且整个序列可并行计算。

**【深入】**
- RNN 的两大问题：① 信息要逐步传递，长程依赖在反向传播中梯度消失/爆炸；② 时间步必须串行，无法并行，训练慢。
- Transformer 用注意力一步建立全局连接，并用残差连接 + LayerNorm 稳定深层训练，配合大规模数据和算力实现 scaling。

**【整体结构（自底向上的数据流）】**
- **输入层**：Token Embedding（把 id 查表成向量）+ Position Encoding（注入位置，见第 3 题）→ 得到序列表示 $X\in\mathbb{R}^{n\times d}$。
- **N 个堆叠的 Transformer Block**（GPT-3 96 层、LLaMA-3 数十层），每个 block 内两个子层：
  1. **多头自注意力（MHSA）子层**：`x → LN → MHSA → +x`（残差）
  2. **前馈网络（FFN/MLP）子层**：`x → LN → FFN → +x`（残差）
- **输出层**：最后一层 LN → 线性投影到词表大小（LM Head，常与输入 embedding **权重共享**）→ softmax 得到下一个 token 分布。
- 关键张量维度始终是 $n\times d$（n=序列长，d=hidden）：注意力做「token 间」混合（跨位置交互），FFN 做「token 内」逐位置的特征变换，两者交替，是 Transformer 的基本节奏。
- 一个 block 内：**多头自注意力 +（残差&归一化）+ 前馈网络 FFN +（残差&归一化）**。FFN 通常是 4×hidden 的两层 MLP（现代用 SwiGLU，见第 0.3 节），承担大部分参数量与「知识存储」。

**【残差连接：为什么不可或缺】**
- 形式：$\text{out} = x + \text{Sublayer}(\text{LN}(x))$（Pre-LN 写法）——子层只学「相对输入的增量 $F(x)$」，输出 = 输入 + 增量。
- **作用① 解决深层梯度消失**：反向传播时 $\frac{\partial \text{out}}{\partial x} = 1 + \frac{\partial F}{\partial x}$，那个 **「+1」让梯度有一条直达底层的「高速公路」**，即使 $\partial F/\partial x$ 很小，梯度也不会衰减到 0，几十上百层才训得动（源自 ResNet 思想）。
- **作用② 恒等映射易学**：如果某层最优是「什么都不做」，网络只需让 $F(x)\to 0$，比让一堆非线性层去拟合恒等函数容易得多 → 加深网络不会变差。
- **作用③ 信息保留**：每层都把原始信息原样带下去，再叠加新信息，避免深层把底层特征「冲刷」掉；可理解为对表示的**迭代式精炼（residual stream）**——这也是机理可解释性里把残差流看作「各层读写的公共总线」的由来。
- 配套的 **LayerNorm**：对每个 token 的特征维做归一化，稳定数值分布、加速收敛；LLM 常用更省的 **RMSNorm**（去掉均值中心化，只按均方根缩放）。

**【权衡 / 追问】**
- 代价是注意力的 O(n²) 复杂度（时间和显存都随序列长度平方增长），这是长序列优化的根源问题。
- 可能追问：**Pre-LN vs Post-LN**？Post-LN（原始 Transformer，`LN(x+Sublayer(x))`）表达力略强但深层梯度不稳、需 warmup；**Pre-LN**（`x+Sublayer(LN(x))`，归一化放子层输入端）让残差通路是干净的恒等映射、训练更稳、可去 warmup，是现在主流。
- 可能追问：FFN 为什么要先升维再降维？提供非线性容量、充当 key-value 记忆。
- 可能追问：**没有残差会怎样**？深层 Transformer 几乎无法收敛——这是 Pre-LN/残差/归一化「三件套」共同保证可训练性的核心原因。

📖 参考：Attention Is All You Need — [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762) ｜ ResNet（残差）— [https://arxiv.org/abs/1512.03385](https://arxiv.org/abs/1512.03385)

---

### 1.1 大模型的参数量怎么推算？⭐ `#基础 #工程 #高频`
**【核心答案】** 记隐层维度 $d$、层数 $L$、词表 $V$，则

$$N \approx \underbrace{12\,L\,d^2}_{\text{主体}} + \underbrace{V d}_{\text{词嵌入}}$$

那个 **12** 来自每层的两块：**注意力 $4d^2$**（$W_Q,W_K,W_V,W_O$ 各 $d\times d$）＋ **FFN $8d^2$**（升维 $d\times 4d$ ＋ 降维 $4d\times d$）。**参数量随 $d$ 平方增长、随 $L$ 线性增长**——这是「加宽比加深贵得多」的原因。

**【深入】**
- 逐项拆解（单层）：

| 部件 | 形状 | 参数量 |
|---|---|---|
| $W_Q,W_K,W_V,W_O$ | 各 $d\times d$ | $4d^2$ |
| FFN 升维 | $d\times d_{ff}$，$d_{ff}=4d$ | $4d^2$ |
| FFN 降维 | $d_{ff}\times d$ | $4d^2$ |
| LayerNorm / RMSNorm | 每层 2 个，各 $d$ | $\approx 2d$，可忽略 |
| **单层合计** | | $\mathbf{12d^2}$ |

- **SwiGLU 为什么不改变这个数**：它的 FFN 有 3 个矩阵（$W,V,W_2$）而非 2 个，所以中间维度取 $d_{ff}=\tfrac{2}{3}\times 4d$ 来保持参数量持平——$3\times d\times\tfrac{8d}{3}=8d^2$，和标准 FFN 一样（见 0.3）。实际实现还会把 $d_{ff}$ 向上取整到 256 的倍数。
- **验算一：GPT-3 175B**（$L=96,\ d=12288,\ V=50257$，词表绑定）：主体 $12\times 96\times 12288^2 = 173.9\text{B}$，词嵌入 $50257\times 12288 = 0.62\text{B}$，**合计 174.6B** —— 对上了官方的「175B」。
- **验算二：LLaMA-7B**（$L=32,\ d=4096,\ V=32000,\ d_{ff}=11008$，SwiGLU，输入输出词表不绑定）：每层 $4d^2+3d\,d_{ff}=0.202\text{B}$，主体 $6.476\text{B}$，词嵌入 $2\times 32000\times 4096=0.262\text{B}$，**合计 6.738B** —— 官方公布 6.74B。（$d_{ff}$ 的由来：$\tfrac23\times4\times4096=10922.7$，向上取到 256 的倍数即 11008。）
- **三处需要修正的情况**：
  - **GQA**：$W_K,W_V$ 缩小到 $d\times d_{kv}$（$d_{kv}=\tfrac{h_{kv}}{h}d$），注意力从 $4d^2$ 降到 $2d^2+2d\,d_{kv}$。LLaMA-3-70B 这类模型必须按这个算才对得上。
  - **MoE**：每层 FFN 复制成 $n$ 份专家，**总参数**按 $n$ 倍算，但**激活参数**只算 top-$k$ 那几个。DeepSeek-V3 的「671B 总 / 37B 激活」就是这么来的（见第 6 题）。
  - **词表绑定**：输入 embedding 和输出 LM Head 是否共享权重，差一个 $Vd$。

**【权衡 / 追问】**
- 追问 **词嵌入什么时候不能忽略**：大模型里 $Vd$ 占比极小（GPT-3 只有 0.35%），但**小模型里它能占到一半**——比如 $d=768$、$V=32000$ 时 $Vd\approx 24.6\text{M}$，而 12 层主体只有 $12\times12\times768^2\approx 85\text{M}$。所以给端侧小模型缩词表是真的有效。
- 追问 **训练算力**：$C \approx 6ND$ FLOP（$N$ 参数、$D$ 训练 token）。来源是每 token 每参数前向约 2 FLOP、反向约 4 FLOP。**MoE 要代入激活参数**而非总参数。例：7B 模型训 2T tokens $\approx 6\times 7\text{e}9\times 2\text{e}12 = 8.4\text{e}22$ FLOP。
- 追问 **显存**：训练（混合精度 + Adam）约 **16~20 bytes/参数** ＝ 权重(fp16 2) + 梯度(fp16 2) + Adam 状态(fp32 master 4 + $m$ 4 + $v$ 4)，再加激活；所以 7B 全量训练要 100+ GB，必须 ZeRO / 并行。推理则是 参数 × 每参数字节（fp16 = 2、int4 = 0.5）＋ **KV cache**（见第 5 题）。
- 追问 **为什么参数量常与「加宽还是加深」挂钩**：$N\propto Ld^2$，加宽的代价是平方级；但加深会拉长梯度传播路径、增加流水线并行的气泡。实际配置一般让 $d/L$ 落在某个经验区间（GPT-3 是 $12288/96=128$）。

---

### 2. 手撕 self-attention，并解释每一步 ⭐ `#手撕 #高频`
**【核心答案】** Attention(Q,K,V) = softmax(QKᵀ / √dₖ) · V。Q/K/V 由输入分别乘三个可学习矩阵得到；QKᵀ 算相似度，缩放后 softmax 归一化成权重，再加权求和 V。

**【深入】**
- **为什么除以 √dₖ**：Q、K 各维度近似独立、均值 0 方差 1 时，点积的方差约等于 dₖ。维度越大点积越大，softmax 进入饱和区，梯度趋近 0。除以 √dₖ 把方差拉回 1 附近，保证梯度健康。
- **多头注意力**：把 d 维切成 h 个 d/h 维子空间并行做注意力，让不同头关注不同关系（语法、指代、位置等），最后拼接再线性映射。
- **因果掩码**：生成式模型在 softmax 前把「未来位置」置为 -∞，保证第 i 个 token 只能看到 ≤ i 的信息。

**【权衡 / 追问】**
- 追问 **复杂度**：序列长 n、维度 d，注意力是 O(n²·d)。
- 追问 **MHA / MQA / GQA 区别**：见第 5 题。
- 手撕时别忘了 mask 和 dropout 的位置，以及最后还有一层输出投影 Wₒ。

参考代码骨架（PyTorch 伪代码）：
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

### 3. 位置编码有哪些？RoPE 为什么成为主流？⭐ `#基础 #高频`
**【核心答案】** 注意力本身对位置不敏感，需要显式注入位置信息。主流分三类：绝对位置编码、相对位置编码、旋转位置编码（RoPE）。RoPE 因为「统一了绝对与相对、外推性好、实现简单且不增加参数」成为 LLaMA / Qwen / 主流开源模型的标配。

**【深入】**
- **绝对位置编码**：原始 Transformer 用正弦函数（无参、可外推一点）或可学习位置向量（BERT，长度固定、不可外推）。直接加到 embedding 上。
- **RoPE（旋转位置编码）**：把每个 token 的 Q、K 按其位置 m 旋转一个角度（按维度成对做二维旋转）。数学上使得 ⟨q_m, k_n⟩ 只依赖相对距离 (m−n)，从而把相对位置信息天然编码进注意力内积。
- **ALiBi**：不改 Q/K，而是在注意力分数上加一个随距离线性递减的偏置（越远惩罚越大），无显式位置向量，外推性好。

**【权衡 / 追问】**
- 追问 **长上下文外推**：RoPE 直接外推到训练长度之外会退化，常用 **位置插值（PI）** 或 **NTK-aware / YaRN** 调整 base 频率来扩展上下文。
- 追问 RoPE 的 base（θ）超参影响：base 越大，长距离区分度越好，是长上下文调优的关键旋钮。

📖 参考：RoFormer (RoPE) — [https://arxiv.org/abs/2104.09864](https://arxiv.org/abs/2104.09864)

---

### 4. Decoder-only / Encoder-only / Encoder-Decoder 的区别与选型 `#基础`
**【核心答案】** 区别在注意力方向和结构：Encoder 双向、Decoder 单向因果、Encoder-Decoder 两者皆有。现代大模型几乎全是 Decoder-only。

**【深入】**
- **Encoder-only（BERT）**：双向注意力，每个 token 看全局，擅长理解类任务（分类、NER、检索）。不能直接生成。
- **Decoder-only（GPT/LLaMA）**：因果掩码、自回归，预训练目标统一为 next-token prediction，scaling 友好、few-shot 能力强，是目前主流。
- **Encoder-Decoder（T5/BART）**：编码器理解输入、解码器生成输出，擅长明确的 seq2seq（翻译、摘要）。

**【权衡 / 追问】**
- 追问 **为什么大模型都收敛到 Decoder-only**？训练目标简单统一、零样本/少样本泛化好、工程上推理范式一致；研究也表明在大规模下纯解码器架构的表现不输甚至更优。
- 追问 **PrefixLM**：一种折中，prompt 部分用双向注意力、生成部分用因果注意力。

📖 参考：BERT — [https://arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805) ｜ GPT-3 — [https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)

---

### 5. KV Cache 是什么？为什么是推理瓶颈？MQA / GQA 如何缓解？⭐ `#工程 #高频`
**【核心答案】** 自回归生成时历史 token 的 K、V 不变，缓存它们避免每步重算，把每步注意力从 O(n²) 降到 O(n)。代价是显存：KV cache ∝ batch × 层数 × 序列长 × head数 × head维。

**【深入】**
- 没有 KV cache，生成第 t 个 token 要重新计算前 t-1 个的全部注意力；有了它，只算当前 token 对历史的注意力。
- 长上下文 + 大 batch 下，KV cache 往往比模型权重还吃显存，是 decode 阶段的主要瓶颈。
- **MQA（Multi-Query Attention）**：所有 head 共享同一组 K/V，KV cache 缩小 head 倍，但质量有损。
- **GQA（Grouped-Query Attention）**：把 head 分成 g 组，每组共享一组 K/V，是 MHA 与 MQA 的折中，LLaMA-2/3 采用。

**【权衡 / 追问】**
- 追问 **怎么进一步省 KV cache**：量化 KV（KV cache int8）、PagedAttention 分页管理（见第 17 题）、滑动窗口注意力、把不重要的 KV 驱逐（H2O 等）。
- 追问 prefill 阶段需不需要 cache？prefill 一次性并行算完所有输入并把 K/V 写入 cache，供后续 decode 复用。

**【扩展：LLM 服务性能指标】** —— 「怎么衡量一个推理服务好不好」，分四类：

- **延迟（Latency，单请求体验）**
  - **TTFT（Time To First Token）**：从请求到首 token 的时间，主要由 **prefill** 阶段决定，受输入长度、是否命中 prefix cache 影响；决定「等待感」。
  - **TPOT / ITL（Time Per Output Token / Inter-Token Latency）**：相邻输出 token 的平均间隔，主要由 **decode** 阶段决定，决定「打字速度」。
  - **端到端延迟 ≈ TTFT + TPOT × 输出 token 数**；常用 P50/P90/P99 而非均值，长尾更能反映体验。

- **吞吐（Throughput，集群效率 / 成本）**
  - **Output tokens/s**（最常用）、**Total tokens/s**（含输入）、**Requests/s（QPS）**。
  - **吞吐 vs 延迟是一对矛盾**：增大 batch（continuous batching）提升吞吐，但单请求 TPOT 变差。常画「吞吐-延迟」曲线，在满足 SLO 的前提下追求最高吞吐。

- **资源 / 成本**
  - **GPU 利用率（MFU / 算力利用率）**、**显存占用**（权重 + KV cache，决定最大并发与最长上下文）。
  - **\$ / 1M tokens**、**单卡并发请求数**——直接对应部署成本。
  - 经验：prefill 是 **compute-bound**，decode 是 **memory-bandwidth-bound**，因此两阶段的瓶颈和优化手段（甚至 PD 分离部署）不同。

- **质量 / 稳定性**
  - **Goodput**：不是裸吞吐，而是「满足 SLO（如 TTFT<Xs、TPOT<Yms）的有效吞吐」，更贴近真实可用容量。
  - 准确率不应因量化/投机解码等优化而下降；还需关注 **超时率、错误率、抢占/排队时延**。

> 追问技巧：被问「服务慢了怎么排查」，按 **TTFT 高 → 看 prefill / 排队 / prefix cache 命中率**；**TPOT 高 → 看 batch、KV cache 显存是否打满、是否频繁抢占** 来分层定位。

📖 参考：GQA — [https://arxiv.org/abs/2305.13245](https://arxiv.org/abs/2305.13245) ｜ vLLM/PagedAttention — [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180) ｜ DistServe（PD 分离）— [https://arxiv.org/abs/2401.09670](https://arxiv.org/abs/2401.09670)

---

### 6. MoE（混合专家）原理、优势与难点 ⭐ `#基础 #工程`
**【核心答案】** 用多个 FFN「专家」，由一个 router 网络为每个 token 选 top-k 个专家做稀疏激活。总参数量很大，但单次前向只激活一小部分，从而在固定算力下扩大模型容量。

**【深入】**
- **基础版（Mixtral 时代）**：Mixtral 8×7B —— 8 个专家，每 token 选 top-2，激活 ~13B，总参数 47B。router = 线性层 + softmax，选 top-k 加权组合。靠**负载均衡损失**防「专家塌缩」（router 总偏爱少数专家）。
- **现代 MoE 三大升级（DeepSeek 系，2024–2025）⭐**：
  - **细粒度专家（fine-grained）**：把专家切得更小更多（如 64 选 8 而非 8 选 2）→ 组合数更多、分工更专。
  - **共享专家（shared experts）**：留 1~2 个「永远激活」的专家装通用知识，其余路由专家管专业知识 → 减少冗余。
  - **无辅助损失均衡（aux-loss-free，DeepSeek-V3）**：给每个专家加可动态调整的 **bias**，过载就调低，不再用会「和主任务打架、伤性能」的负载均衡损失。
- **两种路由范式**：**token-choice**（主流，每 token 选 top-k，可能撑爆专家 → 超 capacity 的 token 被丢弃/转发）vs **expert-choice**（每个专家挑 token，天然均衡）。
- **代表模型**：DeepSeek-V3（671B 总 / 37B 激活）、Mixtral、Qwen-MoE、Grok-1、DBRX、Llama 4、MiniMax 等。

**【权衡 / 追问】**
- 核心价值：**MoE 把「模型容量」和「单 token 算力」解耦** —— 加专家涨容量，但每 token 计算几乎不变。
- **训练优势大 ✅**：等训练算力下能到更低 loss（约等于「免费放大 2~4× 有效容量」，倍数看配置）。代价：总参数全程占显存、all-to-all 通信、训练更不稳。
- **推理优势「有条件」⚠️**：**省算力不省显存** —— 每 token 只算激活参数（便宜），但要把**全部专家**装进显存（贵）。
  - 🟢 **高并发/批量服务**：算力瓶颈 → 吞吐高、单位成本低，显存成本被摊薄 → 划算。
  - 🔴 **低 batch/低延迟/单用户/端侧**：显存带宽瓶颈 + 路由通信开销 → 优势缩水甚至变负担（端侧反而偏爱稠密小模型）。
  - 注意：**MoE 不降低延迟下限**，它赢在吞吐和训练成本，不是「单条请求更快」。
- 追问 **MoE 和并行的关系**：**专家并行（expert parallelism）** 把不同专家放不同卡，是分布式 MoE 的核心，和 TP/PP/DP 组合；all-to-all 是主要通信瓶颈。
- 追问 **怎么得到 MoE**：可从头训，也可 **upcycling**（把训好的稠密模型 FFN 复制成多专家再续训，省成本）。

📖 参考：Mixtral of Experts — [https://arxiv.org/abs/2401.04088](https://arxiv.org/abs/2401.04088) ｜ DeepSeekMoE — [https://arxiv.org/abs/2401.06066](https://arxiv.org/abs/2401.06066) ｜ DeepSeek-V3 — [https://arxiv.org/abs/2412.19437](https://arxiv.org/abs/2412.19437)
> ⚠️ DeepSeek-V3 的 671B/37B 等数字按公开资料，写定稿前对一遍原报告。

---

### 7. Tokenization：BPE 怎么工作？为什么数字/中文/代码容易出问题？ `#基础`
**【核心答案】** BPE（字节对编码）从字符（或字节）开始，反复把语料中出现频率最高的相邻 pair 合并成新 token，直到达到目标词表大小，得到一套子词词表，平衡词表规模与 OOV。

**【深入】**
- **BPE**：贪心按频率合并；**WordPiece**（BERT）：按合并后的语言模型似然增益来选；**SentencePiece**：直接在原始文本上训练、语言无关、能处理无空格语言；**byte-level BPE**（GPT-2）：在字节上做，理论上永不 OOV。
- 一个汉字常被切成多个 token（UTF-8 多字节），所以中文「字数 ≠ token 数」，中文文本的 token 消耗通常更高。
- 数字常被不规则切分（如 "12345" 可能切成 "123"+"45"），影响算术能力；代码的缩进、符号也会产生大量碎 token。

**【权衡 / 追问】**
- 追问 **词表大小的权衡**：词表大→序列短、embedding 矩阵大；词表小→序列长、计算多。
- 追问为什么 LLM 不擅长「数字母」「反转字符串」：因为它看到的是 token 不是字符。

---

# 第二部分：LLM 训练与对齐

### 8. 大模型训练分哪几个阶段？ `#对齐 #基础`
**【核心答案】** ① 预训练（海量无标注文本做 next-token prediction，学语言与世界知识）→ ② SFT 监督微调（用指令-回答对学会听指令）→ ③ 偏好对齐（RLHF / DPO，让输出更符合人类偏好：有用、无害、诚实 3H）。

**【深入】**
- 预训练消耗 99%+ 的算力，决定模型「知道什么」。
- SFT 改变的是「怎么表达/遵循格式」，数据量小但质量要求极高。
- 对齐阶段进一步精细调节行为边界与偏好。近年还常加 **持续预训练**（领域增强）和 **拒绝采样微调（RFT）**。

**【权衡 / 追问】**
- 追问「能力」主要来自哪个阶段？知识与核心能力来自预训练，SFT/对齐主要是「激发与对齐」，而非注入新知识——这也是「知识更新优先用 RAG 而非微调」的依据。

---

### 8.1 On-policy 蒸馏是什么？和 SFT / RFT / 普通蒸馏怎么区分？⭐ `#对齐 #高频`
**【核心答案】** 从**学生自己**采样一段 rollout，在它走过的每个 token 位置上让**教师**给出完整分布，最小化两者的 KL。一句话：**用 RL 的采样方式 + 蒸馏的监督密度**。

**【深入】**
- 四种做法可以放进一张 2×2，两个轴互相正交：

| | 目标是 **one-hot**（硬标签） | 目标是**软分布**（教师 logits） |
|---|---|---|
| **在固定 / 教师数据上**（off-policy） | 合成数据 SFT（Alpaca 式） | **标准 KD** |
| **在学生自生成上**（on-policy） | **RFT / 拒绝采样微调**（见第 8 题） | **On-policy 蒸馏** |

- **横轴＝监督有多密**。硬标签每个位置只告诉你「正确答案是哪个词」；软标签给的是整排词表的概率，信息量高得多。这条分界线就是 0.1 折叠推导里的那件事：one-hot 会把词表求和**乘没**，软分布则一项都塌缩不了。
- **纵轴＝训练分布对不对**。在固定数据上训练，学生被喂的永远是「别人的好前缀」，推理时却要接自己生成的前缀——**exposure bias**：它从没在自己的错误上训练过，一步走偏就进入没见过的状态，误差累积。从学生自己采样则天然没有这个错配。
- **和 RL 比，赢在监督密度**：GRPO/PPO 跑完一整条几百 token 的轨迹只换回**一个标量** reward，信用分配全靠猜；on-policy 蒸馏在同一条轨迹的**每个位置**都有一个完整分布做监督。这是它比 RL 省算力的根本原因。
- **KL 方向**：通常用 **reverse KL** $D_{KL}(\pi_{student}\Vert \pi_{teacher})$，且在学生的 rollout 上计算。用 0.1 的记法一眼可读：第一个位置是学生 → 期望对学生取 → on-policy；reverse 是 mode-seeking → 学生不铺满教师的所有模式，而是**挑一个做好**——对容量小得多的学生，这比 forward KL 的 mass-covering（样样稀松）更实际。
- **自蒸馏是第三根轴**（教师 ＝ 学生自己或它的历史版本），与上面两轴正交：RFT 就是「on-policy ＋ 硬标签 ＋ 自蒸馏」。另有 **SDFT**——先让模型用自己的话重写目标数据集再做 SFT，使微调数据贴近模型原分布，**缓解灾难性遗忘**（见第 12 题）。

**【权衡 / 追问】**
- 代价：**教师必须全程在线跑前向**（学生每采一步都要问它），显存和算力都比离线蒸馏贵；离线 KD 可以把教师分布预先算好存下来。
- 追问 **divergence 怎么选**：文献并不统一。GKD 提出在学生自生成序列上训练、并用广义 JS 散度族在 forward / reverse 之间插值；MiniLLM 明确主张 LLM 蒸馏用 reverse KL。
- 追问 **和 RFT 的区别**：RFT 只保留「答对的整条轨迹」当硬标签，信号仍是稀疏的；on-policy 蒸馏不筛选轨迹，而是在每个 token 上要教师的分布，**错的轨迹同样能提供监督**（教师会指出该走哪一步）。
- 追问 **在训练谱系里的位置**：SFT（forward KL / 数据分布 / 密集）→ on-policy 蒸馏（reverse KL / 学生分布 / 密集）→ RLHF、GRPO（reverse KL / 学生分布 / 稀疏奖励）。它填的正是 SFT 与 RL 之间那个空档。

📖 参考：GKD — [https://arxiv.org/abs/2306.13649](https://arxiv.org/abs/2306.13649) ｜ MiniLLM — [https://arxiv.org/abs/2306.08543](https://arxiv.org/abs/2306.08543)

---

### 9. RLHF 完整流程，痛点是什么？⭐ `#对齐 #高频`
**【核心答案】** ① 用人类对多个回答的排序训练一个 **Reward Model（RM）**；② 用 **PPO** 优化策略模型最大化 reward，同时加 **KL 惩罚**约束它别偏离 SFT 模型太远。

**【深入】**
- 数据：让标注者对同一 prompt 的多个回答排序，RM 学习这个偏好打分。
- PPO 阶段同时存在 4 个模型：policy（在训）、reference（SFT 冻结，算 KL）、reward（打分）、critic/value（估计优势）。
- KL 惩罚是关键：没有它，policy 会为了刷高 reward 输出畸形文本（**reward hacking**）。

**【公式：RM 与 PPO】**
- **RM 损失**（Bradley-Terry 成对排序，y_w 优于 y_l）：

  $$\mathcal{L}_{RM} = -\,\mathbb{E}_{(x,y_w,y_l)}\big[\log \sigma\big(r_\theta(x,y_w) - r_\theta(x,y_l)\big)\big]$$

- **PPO 优化目标**（带 KL 惩罚的奖励 + clip 的策略梯度）：

  $$\max_{\pi_\theta}\ \mathbb{E}_{x,\,y\sim\pi_\theta}\Big[\,r_\phi(x,y) - \beta\,\mathrm{KL}\big(\pi_\theta(y\mid x)\,\Vert \,\pi_{ref}(y\mid x)\big)\Big]$$

  实现上用 clip 形式（A 为 GAE 优势，r_t(θ)=π_θ/π_old 为重要性比）：

  $$\mathcal{L}_{PPO} = \mathbb{E}_t\big[\min(r_t(\theta)\,A_t,\ \mathrm{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\,A_t)\big]$$

**【权衡 / 追问】**
- 痛点：流程复杂、4 模型同时占显存、RL 训练不稳、对超参敏感、RM 容易被钻空子。
- 追问 **RLHF vs RLAIF**：RLAIF 用 AI（如更强模型/宪法）代替人类生成偏好标签，降本，Anthropic 的 Constitutional AI 是代表思路。
- 追问 **GRPO**：PPO 的简化，去掉 critic、用组内相对优势代替，见第 9.1 题。

📖 参考：InstructGPT — [https://arxiv.org/abs/2203.02155](https://arxiv.org/abs/2203.02155) ｜ GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300)

---

### 9.1 GRPO 详解：组内优势怎么算、又怎么传回 loss？⭐ `#对齐 #高频`
**【核心答案】** GRPO ＝ **PPO 去掉 critic**。同一个 prompt 采样一组 G 条回答，用**组内归一化的 reward 当优势**（组均值就是 baseline），再套 PPO 的 clip 目标。关键机制：优势是**一条回答一个标量**，被**广播到该回答的每一个 token**，在梯度里充当对数概率的系数。

**【深入】**
- **第一步：算优势（序列级）**。对同一 prompt 采样 $\{o_1,\dots,o_G\}$，得到奖励 $\{r_1,\dots,r_G\}$：

  $$\hat{A}_i = \frac{r_i - \mathrm{mean}(\{r_1,\dots,r_G\})}{\mathrm{std}(\{r_1,\dots,r_G\})}$$

  出来的是 **G 个标量**，一条回答一个。PPO 靠 critic 给出**逐 token** 的 $A_t$，GRPO 没有 critic，所以**根本没有 token 级的价值估计**。
- **第二步：广播**。$\hat{A}_{i,t}=\hat{A}_i$ 对 $o_i$ 中所有 $t$ 成立——一条 500 token 的回答，这 500 个位置拿到的是**同一个数**。
- **第三步：进入 clip 目标**（$\rho_{i,t}=\pi_\theta(o_{i,t}\mid x,o_{i,<t})/\pi_{old}(o_{i,t}\mid x,o_{i,<t})$）：

  $$\mathcal{L} = \frac{1}{G}\sum_{i}\frac{1}{\lvert o_i\rvert}\sum_{t}\Big[\min\big(\rho_{i,t}\hat{A}_i,\ \mathrm{clip}(\rho_{i,t},1-\epsilon,1+\epsilon)\hat{A}_i\big) - \beta\,\mathbb{D}_{KL}[\pi_\theta\Vert \pi_{ref}]\Big]$$

- **梯度上它到底做了什么**。$\hat{A}_i$ 是常数（必须 detach，不参与求导），梯度只经 $\rho$ 流过，未被 clip 时：

  $$\nabla_\theta \mathcal{L} \approx \frac{1}{G}\sum_i\frac{1}{\lvert o_i\rvert}\sum_t \hat{A}_i\,\rho_{i,t}\,\nabla_\theta \log \pi_\theta(o_{i,t}\mid \cdot)$$

  所以**优势的全部作用就是给每个 token 的对数概率梯度乘一个可正可负的系数**：$\hat{A}_i>0$ 抬高该序列全部 token 的概率，$<0$ 则全部压低。结构上和 SFT 的交叉熵梯度一模一样，只是前面多乘了一个标量——这正是策略梯度恒等式 $\nabla\mathbb{E}[R]=\mathbb{E}[R\nabla\log\pi]$ 的直接体现。
- **一个具体数字**：一组 4 条回答的奖励是 $[1,0,0,1]$，则 $\mathrm{mean}=0.5$、$\mathrm{std}=0.5$，$\hat{A}=[+1,-1,-1,+1]$。两条正确回答的所有 token 系数 $+1$，两条错误回答的所有 token 系数 $-1$。
- **clip 的作用**：当 $\rho$ 跑出 $[1-\epsilon,1+\epsilon]$ 且方向是继续加强时，$\min$ 选中被 clip 的那支，而 clip 在该区域是常数、**梯度为 0**——策略在某个 token 上偏离 $\pi_{old}$ 太远就不再推它。
- **KL 的位置和 PPO 不同**：PPO 把 KL 惩罚**混进逐 token 的 reward**；GRPO 把它作为**独立正则项直接加在 loss 里**，好处是 reward 保持"干净"（纯粹反映答案好坏）、KL 强度可单独调。实现上常用 k3 估计量（无偏、恒非负）。

**【权衡 / 追问】**
- **最重要的局限：credit assignment**。同一个标量砸在所有 token 上，无法区分是哪几步真正起了作用——一条 500 token 推理链最后答对，中间走了弯路但侥幸没影响结果的 token 也会被一视同仁推高；答错的回答里推理正确、只是结论算错的步骤则被无差别压低。这直接解释了两个方向的动机：**过程奖励模型（PRM）** 逐步打分，以及 **on-policy 蒸馏**每 token 给完整分布（见第 8.1 题）。
- **实现坑：整组同分则无信号**。若组内 reward 全相同（全对或全错），$\mathrm{std}=0$、$\hat{A}$ 全为 0，**这一组完全不提供梯度**（实现里靠加 $\epsilon$ 或直接跳过）。所以题目太难或太简单都是在浪费采样，GRPO 需要组内有区分度。
- 追问 **两个归一化的争议**：**Dr. GRPO** 指出除以 $\lvert o_i\rvert$ 会摊薄长回答里每个 token 的惩罚，在 $\hat{A}<0$ 时反而鼓励把错误答案写长；除以 $\mathrm{std}$ 则过度加权组内方差小的样本。它的做法是两个归一化都去掉。
- 追问 **可验证奖励下能否去掉 KL**：在数学/代码这类由规则判对错的场景，有些变体（如 **DAPO**）干脆去掉 KL 项——既然 reward 本身就是客观正确性，就不需要参考模型来防 reward hacking，去掉后模型能走得更远。该方向仍在演进。
- 追问 **为什么适合推理任务**：无需训练 RM（规则即奖励）、无需 critic（省一个同规模模型），且组内采样天然适配「同一题采多次、对错自然分层」的数学/代码场景。

📖 参考：GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300) ｜ DeepSeek-R1 — [https://arxiv.org/abs/2501.12948](https://arxiv.org/abs/2501.12948)

---

### 10. DPO 相比 RLHF 的优势与局限 ⭐ `#对齐 #高频`
**【核心答案】** DPO 把 RLHF 的目标用数学推导成一个**直接在偏好数据上的分类损失**，不需要单独训练 reward model，也不需要 RL 采样循环，因此更稳定、更省资源、更易实现。

**【深入】**
- 关键洞察：RLHF 的最优策略与 reward 之间存在闭式关系，于是可以把「奖励最大化 + KL 约束」重参数化，直接用偏好对 (chosen, rejected) 做一个类似二分类的损失来优化策略，reward model 被「隐式」吸收进策略本身。
- 仍需要一个 reference 模型算 KL 项，但省掉了 RM 和 PPO 的复杂度。

**【公式：DPO】**
- 由 RLHF 最优解 $\pi^*(y\mid x) \propto \pi_{ref}(y\mid x)\exp\big(\tfrac{1}{\beta}r(x,y)\big)$ 反解出**隐式奖励** $r(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{ref}(y\mid x)} + \beta\log Z(x)$，代入 Bradley-Terry，配分项 Z(x) 在成对相减中抵消，得到：

  $$\mathcal{L}_{DPO} = -\,\mathbb{E}_{(x,y_w,y_l)}\Big[\log \sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{ref}(y_w\mid x)} - \beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{ref}(y_l\mid x)}\Big)\Big]$$

  直观理解：**抬高 chosen、压低 rejected 相对 reference 的对数概率比**，β 控制偏离 reference 的强度（等价于 RLHF 里的 KL 系数）。

**【权衡 / 追问】**
- 局限：① 是 **offline**（用固定偏好数据），不像 PPO 能在线采样，可能不如在线方法上限高；② 对偏好数据分布敏感、易过拟合。
- 追问 **衍生方法**：IPO（缓解过拟合）、KTO（用单条好/坏标签而非成对）、SimPO（去掉 reference 模型）、ORPO（把 SFT 和偏好对齐合一）。

**【三者对比：PPO vs DPO vs GRPO】**

| 维度 | PPO（RLHF） | DPO | GRPO |
|------|------------|-----|------|
| 范式 | Online RL | Offline，直接偏好优化 | Online RL（PPO 简化） |
| 需要 RM？ | ✅ 显式训练 | ❌ 隐式吸收进策略 | ✅（或规则/可验证奖励） |
| 需要 Critic/Value？ | ✅ | ❌ | ❌（用组内均值当 baseline） |
| 训练模型数 | 4（policy/ref/RM/critic） | 2（policy/ref） | 3（policy/ref/RM） |
| 优势估计 | GAE（critic 估计） | 无（直接分类损失） | 组内 reward 归一化 |
| **KL 怎么进入** | 混进逐 token 的 reward | **无显式项**，隐含在 $\beta\log\frac{\pi_\theta}{\pi_{ref}}$ 里 | **loss 里的独立正则项**（k3 估计） |
| 显存/复杂度 | 高 | 低 | 中 |
| 稳定性 | 对超参敏感、易不稳 | 稳定、好复现 | 比 PPO 稳，省 critic |
| 在线探索 | ✅ 上限高 | ❌ 受限于数据分布 | ✅ |
| 适用场景 | 通用对齐、追求上限 | 资源有限、快速对齐 | 推理/数学/代码（RLVR） |
| 代表 | InstructGPT/ChatGPT | Zephyr、众多开源对齐 | DeepSeekMath、DeepSeek-R1 |

> 一句话总结：**PPO 最通用但最重；DPO 用一个分类损失换掉整条 RL 流水线，简单稳定但是 offline；GRPO 介于两者之间——保留在线 RL 与探索，但用「组内相对优势」干掉 critic，特别适合有可验证奖励的推理任务。**

📖 参考：DPO — [https://arxiv.org/abs/2305.18290](https://arxiv.org/abs/2305.18290) ｜ GRPO/DeepSeekMath — [https://arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300)

---

### 11. 为什么会幻觉（hallucination）？怎么缓解？⭐ `#对齐 #高频`
**【核心答案】** 根因是训练目标只优化「下一个 token 的流畅与高概率」，而非「事实正确」；当知识缺失/过时/长尾时，模型仍倾向流畅地编造而非承认不知道。

**【深入】**
- 来源细分：① 预训练数据本身有错/过时；② 长尾知识记不准；③ 解码随机性；④ SFT 阶段如果教模型回答它其实不知道的问题，会强化「自信地胡说」。
- 缓解分层：
  - **数据/训练**：提高数据质量；对齐时奖励「不确定就说不知道」与「引用来源」。
  - **推理时**：RAG 提供外部依据并溯源、降低温度、self-consistency（多次采样投票）、self-verification（让模型核查自己的答案）。
  - **系统层**：输出附带引用、置信度、可点击溯源。

**【权衡 / 追问】**
- 追问 RAG 能否消除幻觉？不能，只能降低——检索错/不全、或模型「无视」检索结果仍会幻觉。
- 追问怎么**评测**幻觉：TruthfulQA、FActScore、以及多模态的 POPE。

📖 参考：RAG — [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

---

### 12. 灾难性遗忘怎么处理？ `#对齐`
**【核心答案】** 微调新任务/新领域时旧能力退化。常用：原始数据回放（replay/混合通用数据）、参数高效微调（LoRA/Adapter 只动少量参数）、较小学习率、正则化（如 EWC 约束重要参数）。

**【深入】**
- 全参微调最容易遗忘；只训练旁路（LoRA）天然保留原能力。
- 持续学习中常按比例混入通用语料（如 5–30%）来「锚定」原分布。

**【权衡 / 追问】** 追问数据配比怎么定？经验性，需实验；领域数据过多会遗忘通用能力，过少则领域提升不足。

---

### 13. LoRA 原理与优势？QLoRA 又是什么？⭐ `#工程 #高频`
**【核心答案】** 冻结原权重 W，旁路加一个低秩分解 ΔW = B·A（A 把维度降到秩 r，B 再升回去，r 远小于原维度），只训练 A、B。基于「权重更新本质是低秩的」这一假设。

**【深入】**
- 训练参数量从 d×d 降到 2×d×r，降几个数量级；显存和存储大幅下降；多个 LoRA 可即插即用切换。
- 推理时可把 B·A 合并回 W，**不增加推理延迟**。
- 初始化：A 用高斯、B 置零，保证训练开始时 ΔW=0 不破坏原模型。
- **QLoRA**：把基座权重量化到 4-bit（NF4）后再做 LoRA，单卡就能微调很大的模型，引入了 NF4、double quantization、paged optimizer 等技巧。

**【权衡 / 追问】**
- 追问 **秩 r 怎么选**：常见 8/16/32/64，越大表达力越强但越接近全参微调；任务越复杂用越大。
- 追问 LoRA 的局限：对需要大幅改变模型行为的任务，可能不如全参微调。

📖 参考：LoRA — [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685) ｜ QLoRA — [https://arxiv.org/abs/2305.14314](https://arxiv.org/abs/2305.14314)

---

# 第三部分：LLM 推理与工程优化

### 14. 量化是什么？PTQ 和 QAT 的区别？常见方案？ `#工程`
**【核心答案】** 把权重/激活从 FP16 降到 INT8/INT4 等低比特，省显存、提速。分训练后量化（PTQ，无需再训练，快）和量化感知训练（QAT，训练时模拟量化，精度好但成本高）。

**【深入】**
- **PTQ 主流**：GPTQ（逐层最小化量化误差，权重 4-bit）、AWQ（识别并保护「重要权重」对应的通道）、SmoothQuant（把激活的异常值平移到权重上，让激活更好量化）。
- 难点是**激活里的 outlier**：少数维度数值极大，直接量化会损失精度，上述方法都在处理它。
- 衍生概念：W4A16（权重 4-bit、激活 16-bit）、KV cache 量化。

**【权衡 / 追问】** 核心权衡是精度损失 vs 显存/速度收益。追问 INT4 一般损失多少？通常 4-bit 权重量化精度损失很小（1-2%），是性价比甜点。

📖 参考：GPTQ — [https://arxiv.org/abs/2210.17323](https://arxiv.org/abs/2210.17323) ｜ AWQ — [https://arxiv.org/abs/2306.00978](https://arxiv.org/abs/2306.00978)

---

### 15. Flash Attention 到底解决了什么？⭐ `#工程 #高频`
**【核心答案】** 它**不减少计算量，而是减少显存读写**（IO-aware）。标准注意力要把 n×n 的注意力矩阵写回显存（HBM）再读出，IO 成 O(n²)；Flash Attention 用分块（tiling）在高速 SRAM 内计算、用 online softmax 增量更新，避免存下完整矩阵。

**【深入】**
- 关键观察：现代 GPU 计算快、访存慢，注意力是**访存受限**而非计算受限。
- online softmax：分块计算时维护running max 和 running sum，逐块更新结果，无需一次性看到整行。
- 结果：更快 + 更省显存，且是**精确注意力**（非近似，不损失精度）。
- 后续：FlashAttention-2（更好的并行与工作划分）、FlashAttention-3（针对 H100 的异步与 FP8）。

**【权衡 / 追问】** 追问它和稀疏/线性注意力的区别？后者通过近似降低计算复杂度（有损），Flash Attention 是无损的工程优化。

📖 参考：FlashAttention — [https://arxiv.org/abs/2205.14135](https://arxiv.org/abs/2205.14135)

---

### 16. 推测解码（Speculative Decoding）原理？⭐ `#工程`
**【核心答案】** 用一个**小模型（draft）快速自回归生成若干候选 token**，再用大模型**一次前向并行验证**这些 token，接受匹配的前缀、从第一个不匹配处重采。大模型一次能确认多个 token，提升吞吐。

**【深入】**
- 大模型对一段序列做一次前向就能拿到每个位置的概率分布，用它来「批量校验」小模型的猜测。
- 通过精心设计的接受/重采规则，保证最终输出分布与「只用大模型」**严格一致**（无损加速）。
- 变体：Medusa（给大模型加多个预测头自己做 draft，省去独立小模型）、EAGLE（在特征层做更准的 draft）、Lookahead Decoding。

**【权衡 / 追问】** 加速比取决于小模型的「命中率」和两者大小差距；draft 太弱则接受率低、收益小。追问适用场景：批量小、追求低延迟时收益明显。

📖 参考：Speculative Decoding — [https://arxiv.org/abs/2211.17192](https://arxiv.org/abs/2211.17192)

---

### 17. 提升推理吞吐的工程手段有哪些？ `#工程`
**【核心答案】** Continuous batching（动态拼接请求）、PagedAttention（KV cache 分页管理）、prefix caching（复用相同前缀的 KV）、张量/流水线并行、量化、推测解码。

**【深入】**
- **Continuous batching**：传统静态 batch 要等最慢的请求完成才能放新请求；continuous batching 在每步动态把已完成的换成新请求，大幅提高 GPU 利用率。
- **PagedAttention**（vLLM）：借鉴操作系统虚拟内存分页，把 KV cache 切成固定大小的块、用页表映射到非连续物理显存，几乎消除碎片，并支持请求间 KV 共享（如相同 system prompt）。
- **Prefix caching**：多个请求共享前缀（如同一 system prompt）时只算一次。

**【权衡 / 追问】** 追问 throughput vs latency 的权衡：大 batch 提吞吐但单请求延迟变高；在线服务要在两者间取舍。

📖 参考：vLLM / PagedAttention — [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180)

---

### 18. Prefill 和 Decode 两个阶段有什么本质区别？ `#工程 #高频`
**【核心答案】** Prefill 处理输入 prompt，所有 token 可并行，是**计算密集（compute-bound）**；Decode 逐 token 生成，每步只算一个 token 对全部历史的注意力，是**访存密集（memory-bound）**，受 KV cache 读取带宽限制。

**【深入】**
- 这解释了为什么：长输入（prefill 重）和长输出（decode 步数多）的优化重点不同。
- 指标：prefill 影响「首 token 延迟 TTFT」，decode 影响「每 token 延迟 TPOT / 吞吐」。
- 工程上常把两者**分离调度**（如 disaggregated serving，prefill 和 decode 跑在不同节点）以分别优化。

**【权衡 / 追问】** 追问 chunked prefill：把长 prefill 切块，和 decode 混合调度，平衡 TTFT 与吞吐。

---

# 第六部分：高频开放题

> 这些没有标准答案，考的是判断力和「讲权衡」的能力。

- **上下文越长越好吗？** 不是。长上下文有「lost in the middle」（中段信息易被忽略）、推理成本随长度上升、注意力被稀释等问题。RAG 与长上下文互补而非替代：要溯源/省成本/知识常更新 → RAG；信息必须整体一起看（如长合同通读）→ 长上下文。

- **RAG 还是微调？** 知识频繁更新、需溯源、降低幻觉 → RAG；改变风格/格式/输出习惯、注入稳定的领域能力 → 微调；二者常结合（微调让模型更会用检索结果）。一句话：RAG 改「模型知道什么」，微调改「模型怎么表现」。

- **temperature / top-p 怎么调？** temperature 缩放 softmax 平滑度控制随机性（低→确定、高→发散）；top-p（核采样）只在累计概率达 p 的 token 集合里采样，截断长尾。事实/代码任务用低温，创意任务用高温。两者一般不同时大幅调。

- **Scaling Law 是什么？Chinchilla 的启示？** 模型性能随参数 N、数据 D、算力 C 呈幂律提升。Chinchilla 指出当时多数大模型「参数过大、数据不足」，在固定算力下应让 N 和 D 更均衡地增长（经验上 token 数约 20×参数量），同算力下小而「喂饱」的模型反而更强。

- **怎么把一个大模型压缩上线？** 组合拳：量化（4-bit 权重）+ 蒸馏（大模型教小模型）+ 剪枝 + 推理引擎优化（vLLM / TensorRT-LLM）。按延迟、成本、精度目标做取舍，先定 SLA 再选方案。

📖 参考：Scaling Laws — [https://arxiv.org/abs/2001.08361](https://arxiv.org/abs/2001.08361) ｜ Chinchilla — [https://arxiv.org/abs/2203.15556](https://arxiv.org/abs/2203.15556)
