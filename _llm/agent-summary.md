---
layout: llm-doc
title: "Agent 知识总结"
subtitle: "规划 · 工具 · 记忆 · 多智能体"
topic: agent
category: summary
order: 1
permalink: /agent/summary/
lang: zh
pair: agent-summary
source: "Agent知识总结.md"
highlights: "Agent 核心组成 · ReAct 与规划 · 工具调用 · 短期与长期记忆 · 反思与自我纠错 · 多智能体协作 · 评测与失败模式"
title_en: "Agent Notes"
subtitle_en: "Planning · Tools · Memory · Multi-Agent"
highlights_en: "What an LLM agent is · ReAct and planning · Tool use · Short- and long-term memory · Reflection and self-correction · Multi-agent collaboration · Evaluation and failure modes"
---

* TOC
{:toc .llm-toc-list}

> **定位**：规划 · 工具 · 记忆 · 多智能体。每个条目按 **核心答案 → 深入原理 → 权衡 / 追问 → 参考** 组织，⭐ 标记值得重点深挖的地方。
> 
> **配套**：[LLM 知识总结](/llm/summary/)

---

# 第五部分：Agent（智能体）

### 1. 什么是 LLM Agent？核心组成？⭐ `#agent #高频`
**【核心答案】** 以 LLM 为「大脑」，通过**规划 + 工具 + 记忆 + 反思**自主完成多步任务，而非单轮问答。四大模块：Planning（任务拆解/规划）、Tool use（调用外部 API/工具获取能力与信息）、Memory（短期上下文 + 长期记忆）、Reflection（基于反馈自我纠错）。

**但更有判断力的一条分界线是 workflow 与 agent** —— 关键在**谁决定流程**：

| | 流程由谁决定 | 例子 |
|---|---|---|
| **Workflow** | **预先写死的代码路径**，LLM 只在固定节点上被调用 | 先分类 → 再按类别走不同 prompt → 汇总 |
| **Agent** | **LLM 自己决定**下一步做什么、调哪个工具、何时停 | 给定目标和一组工具，自行推进直到完成 |

**生产系统里大多数「AI agent」其实是 workflow，而且这样通常更好**——可预测、可测试、成本可控。真正需要 agent 的场景是：步骤数无法预先确定、路径依赖中间结果。

**【深入】**
- Agent ＝ LLM（推理与决策）＋ 工具（扩展能力边界）＋ **控制循环**（感知-决策-行动-观察）。三者里**循环才是 agent 之所以为 agent 的东西**——去掉循环就退化成一次函数调用。
- **最小可运行形态其实很简单**，本质就是「LLM 在循环里调工具」：

```python
messages = [{"role": "user", "content": task}]
for _ in range(MAX_STEPS):                 # 步数上限，防死循环
    reply = llm(messages, tools=TOOLS)     # 模型决定：说话，还是调工具
    if not reply.tool_calls:               # 没有工具调用 → 任务结束
        return reply.content
    messages.append(reply)
    for call in reply.tool_calls:
        result = TOOLS[call.name](**call.args)   # 真正执行的是外部代码
        messages.append({"role": "tool", "content": result})
```

  这十几行就是第 10 题所说 **harness** 的骨架：模型只负责「决定调什么」，**执行、回填、循环控制全在模型之外**。
- 与「单纯 prompt」的区别：Agent **有状态、有循环、能与环境交互并根据反馈调整**。
- **循环带来能力，也带来代价**：每多一步，出错的机会就多一次，且错误会顺着循环累积——这是第 8 题「Agent 为什么不可靠」的根源。能力和脆弱性来自同一个机制。
- 关于「四大模块」的地位：这是 Lilian Weng 2023 年那篇综述的**分类视角，不是架构规范**——没有哪个框架真的按这四块来实现。它适合用来盘点「我这套系统缺了哪一环」，不适合当作搭建蓝图。

**【权衡 / 追问】**
- 追问 **Agent 何时是过度设计**：简单任务直接 prompt/RAG 更稳更便宜；能用固定流程表达清楚的，就写成 workflow。Agent 适合**多步、动态决策、需要调工具**的复杂任务。判断标准可以很直接：**你能不能提前把流程图画出来？** 画得出来就写 workflow。
- 追问 **为什么说「大多数 agent 就是 LLM 加个循环」**：Anthropic 在 *Building effective agents* 里的核心观察就是——成功的实现往往用**简单、可组合的模式**，而不是复杂框架；框架的抽象层反而会挡住你对 prompt 和工具返回值的调试视线。
- 追问 **循环的终止条件怎么定**：模型不再发出工具调用（自然终止）、步数/时间上限（硬性兜底）、外部判据（测试通过、目标达成）。**必须有硬性兜底**，否则遇上模型反复调同一个工具就停不下来（见第 8 题）。

📖 参考：Anthropic「Building effective agents」— [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents) ｜ Lilian Weng「LLM Powered Autonomous Agents」— [https://lilianweng.github.io/posts/2023-06-23-agent/](https://lilianweng.github.io/posts/2023-06-23-agent/)

---

### 2. ReAct 是什么？为什么有效？⭐ `#agent #高频`
**【核心答案】** Reasoning + Acting 交替：模型循环输出 **Thought（推理）→ Action（调工具）→ Observation（结果）**，直到完成。推理指导行动，行动的真实反馈又修正推理。

**【深入】**
- 纯 CoT 只在「脑内」推理，无法获取外部信息、易累积错误；纯 Acting 缺乏规划。ReAct 把两者结合：用推理决定下一步动作，用观察校正推理。
- 通过与外部（如搜索、API）交互，能减少幻觉、动态获取最新信息。

**【权衡 / 追问】** 追问 ReAct 的失败模式：陷入循环、重复无效动作、推理与动作不一致；需配合步数上限、反思机制。

📖 参考：ReAct — [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

---

### 3. Function Calling / Tool Use 的机制与工程要点 `#agent #工程`
**【核心答案】** 给模型提供工具的 **schema（名称、参数、描述）**，模型输出结构化调用（通常 JSON），由外部代码执行后把结果喂回模型继续推理。

**【深入】**
- 模型本身不执行工具，它只「决定调哪个工具、传什么参数」；执行和结果回填由 agent 框架完成。
- 训练上：通过包含工具调用轨迹的数据微调，让模型学会何时/如何调用（Toolformer 思路）。

**【权衡 / 追问】**
- 工程要点：参数 schema 校验、调用失败重试、工具选择准确率、并行调用、防止模型幻觉出不存在的工具或乱传参。
- 追问怎么提升工具调用准确率：清晰的工具描述、few-shot 示例、约束解码（强制合法 JSON）、减少同时暴露的工具数量。

📖 参考：Toolformer — [https://arxiv.org/abs/2302.04761](https://arxiv.org/abs/2302.04761)

---

### 4. Agent 的规划方法有哪些？ `#agent`
**【核心答案】** CoT（单线链式推理）、ToT（Tree of Thoughts，树状探索多路径并回溯）、Plan-and-Execute（先整体规划再逐步执行）、Reflexion（失败后基于语言反馈反思重试）。

**【深入】**
- **CoT**：把问题拆成中间步骤，适合一次性推理题。
- **ToT**：每步生成多个候选思路，用搜索（BFS/DFS）+ 评估选优，适合需要试错/回溯的问题（如解谜）。
- **Plan-and-Execute**：先让 LLM 列出完整计划再逐项执行，比 ReAct 更省 LLM 调用、更适合长任务，但对计划质量敏感。
- **Reflexion**：把失败的轨迹和反思写进记忆，下次重试时参考。

**【权衡 / 追问】** 追问 ReAct vs Plan-and-Execute：前者灵活、能动态调整但调用多；后者高效但计划错了就全错。

📖 参考：Tree of Thoughts — [https://arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601) ｜ Reflexion — [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

---

### 5. RAG 完整流程与优化点？⭐ `#agent #工程 #高频`
**【核心答案】** 流程：文档切块 → 向量化入库 → 检索 Top-k → 拼进 prompt → 生成。每个环节都有优化空间。

**【深入】**
- **切块（chunking）**：定长+重叠窗口 / 语义切块 / 按结构（标题、段落）切；块太大噪声多，太小丢上下文。
- **检索**：① **混合检索** = 向量（语义）+ BM25（关键词）；② **rerank**：用 cross-encoder 对召回结果重排序，显著提质；③ **query 改写/扩展**：把口语化问题改写成更适合检索的查询（HyDE、multi-query）。
- **生成**：引用溯源、防止「检索到了却不用」、控制上下文不超长。
- **进阶**：GraphRAG（用知识图谱组织）、多跳检索（多轮检索回答复杂问题）、Self-RAG（模型自己判断要不要检索、检索得好不好）。

**【权衡 / 追问】**
- 追问 RAG 失败的常见原因：检索召回差（根因最多）、chunk 切坏、reranker 缺失、上下文太长「lost in the middle」。
- 追问 **RAG vs 长上下文**：互补——RAG 省 token、可溯源、知识可更新；长上下文省检索工程但贵且中段信息易丢。

📖 参考：RAG — [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

---

### 6. Agent 的记忆怎么设计？ `#agent`
**【核心答案】** **短期记忆** = 当前对话上下文（受 context 长度限制）；**长期记忆** = 把历史/知识存入向量库，按需检索召回。可加摘要压缩、重要性打分、时间衰减。

**【深入】**
- 长上下文满了怎么办：滚动摘要（把旧对话压成摘要）、只保留关键信息、外置到向量库检索。
- Generative Agents（斯坦福小镇）用「记忆流 + 重要性/相关性/时近性打分」检索记忆，是经典设计。

**【权衡 / 追问】** 追问检索式记忆的问题：召回不准会「忘事」或「记错」；需要好的写入（什么值得记）和读出（怎么检索）策略。

---

### 7. Multi-Agent 系统的价值与挑战 `#agent`
**【核心答案】** 价值：角色分工（如规划者/执行者/审查者）、并行处理、复杂任务分解、相互审查提质。挑战：通信与协调成本、错误在 agent 间累积放大、终止条件难定、成本与延迟高。

**【深入】**
- 常见模式：流水线（顺序）、辩论（debate 提升正确性）、监督者-工作者（supervisor 分派）。
- 框架：AutoGen、CrewAI、LangGraph、MetaGPT。

**【权衡 / 追问】** 追问 multi-agent 真比单 agent 强吗？不一定——简单任务下多 agent 徒增成本和不稳定；要看任务是否真能从分工/审查中获益。

---

### 8. Agent 为什么不可靠？怎么提升稳定性？⭐ `#agent #高频`
**【核心答案】** 主因是**误差累积**——多步任务里任一步出错都可能让后续全盘崩坏；加上工具调用幻觉、死循环、长程规划弱。提升靠：限制步数+超时、每步校验与重试、ReAct/Reflexion 自纠、关键步骤 human-in-the-loop、结构化输出约束、充分的日志与可观测性。

**【深入】**
- 假设单步成功率 95%，10 步串联整体成功率仅约 0.95¹⁰ ≈ 60%——这是 agent 可靠性差的数学本质。
- 因此「减少步数」「每步验证」「可恢复/回滚」比「让单步更聪明」往往更有效。

**【权衡 / 追问】** 追问怎么定位 agent 失败：靠 tracing（如 LangSmith）逐步看 thought/action/observation，找出第一个出错步。

---

### 9. 怎么评估一个 Agent？ `#agent`
**【核心答案】** 指标：任务成功率、步数/调用次数/成本、延迟、工具调用准确率、鲁棒性。基准：AgentBench（综合）、GAIA（通用助理）、WebArena（网页操作）、SWE-bench（真实代码修复）、τ-bench（工具+对话）。

**【深入】** 评估难点在于任务开放、过程难自动判分；常用「最终状态是否达成」+「轨迹质量」结合，必要时用更强模型当裁判（LLM-as-judge，但要防偏见）。

**【权衡 / 追问】** 追问 LLM-as-judge 的坑：位置偏见、长度偏见、自我偏好；需打乱顺序、设评分细则、必要时人工抽检。

---

### 10. 什么是 Agent Harness？Skill 又是什么？⭐ `#agent #工程 #高频`
**【核心答案】** **Harness（智能体框架/骨架）** 是包裹在 LLM 外面、驱动它持续运转的那层工程系统：它负责把上下文喂给模型、解析模型的工具调用、真正执行工具、把结果回填，再循环——也就是 ReAct「感知-决策-行动-观察」循环的**工程实现载体**。**Skill（技能）** 则是给 Agent 按需加载的一份「能力包」：通常是一段结构化的指令/流程说明（+ 可选的脚本、模板、参考文档），告诉模型在某类任务上「该怎么做」，用到时才注入上下文。Claude Code / Claude Agent SDK 的 Skills 就是典型。

**【深入】**
- **Harness 干的事**（模型本身不做的那部分）：上下文拼装与裁剪、工具 schema 注入、工具调用的解析与执行、错误重试、循环控制（步数/超时/终止条件）、状态与记忆管理、权限与沙箱、可观测性（trace/log）。可以说**模型是大脑，harness 是神经系统与躯干**。
- **Skill 的本质是「渐进式上下文加载（progressive disclosure）」**：不把所有领域知识一次性塞进 system prompt（浪费 token、稀释注意力），而是平时只放一句「技能简介」，模型判断相关时才把完整的技能内容拉进上下文。这把「Agent 的能力」从「写死的 prompt」变成了**可插拔、可复用、可版本管理的模块**。
- 一个 Skill 通常包含：触发描述（什么时候用）、操作步骤/最佳实践、可调用的脚本或工具、示例与模板。它和 **Tool/Function** 的区别：Tool 是「一个可执行的原子动作」，Skill 是「一套做某类事的方法论 + 可能打包了多个 tool 的用法」。
- 与 **RAG** 的区别：RAG 检索的是「事实知识」用于回答；Skill 加载的是「程序性知识/操作手册」用于指导行动。

**【权衡 / 追问】**
- 追问 **为什么需要 harness 而不是让模型自己跑**：模型是无状态的「下一个 token 预测器」，没有循环、不能真正执行代码、不持久化状态——这些都得 harness 补。harness 的质量（上下文工程、工具可靠性、错误恢复）往往比换更强的模型更决定 Agent 的成败。
- 追问 **Skill / Harness 体现的核心思想 = 上下文工程（context engineering）**：在有限的上下文窗口里，决定「此刻该放什么、不放什么」。Skill 是按需加载，harness 的滚动摘要/记忆检索是动态裁剪，二者都是为了对抗「上下文越长越稀释、越贵」。
- 追问与 **MCP（Model Context Protocol）** 的关系：MCP 是标准化「工具/数据源怎么接入」的协议，harness 通过 MCP 拿到工具；Skill 则是「怎么用这些工具把事做好」的方法层。
- 追问落地代表：Claude Code（harness + Skills + 子 agent）、OpenAI 的 Assistants/Responses、各类 Agent SDK；工程上常配合**子 Agent（subagent）**——把一个复杂技能丢给独立上下文的子 agent 执行，避免污染主上下文。

📖 参考：Anthropic「Building effective agents」— [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents) ｜ Agent Skills — [https://www.anthropic.com/news/skills](https://www.anthropic.com/news/skills) ｜ MCP — [https://modelcontextprotocol.io](https://modelcontextprotocol.io)

---

### 11. 什么是 Agent 的 Trajectory（轨迹）？有什么用？⭐ `#agent #高频`
**【核心答案】** Trajectory 是 Agent 为完成一个任务所走过的**完整交互序列**——从接到任务到结束的整段「行动历史」。在 ReAct 范式下，它就是一连串 `(Thought 思考 → Action 动作 → Observation 观察)` 三元组，直到产出最终答案。一条轨迹 ≈ 强化学习里的一个 **episode**。

**【深入】**
- 典型结构：`任务 → 思考 → 动作(调工具) → 观察(工具返回) → 思考 → … → 最终答案`。把这整段记录串起来就是一条 trajectory。
- 四大用途：
  - **评估（trajectory evaluation）**：不只看最终答案对不对，还看中间过程是否合理——少走弯路、没有死循环、工具调用得当。对应第 9 题的「最终状态 + 轨迹质量」双重判分。
  - **训练数据**：收集高质量轨迹做 SFT；或用 **拒绝采样（rejection sampling）/ DPO** 从多条轨迹里挑好坏对，让模型学会更优的行动策略。
  - **强化学习**：轨迹 = 一个 episode，每步是 `(state, action)`，配合 reward 算策略梯度（RLHF/GRPO 训练 agent 行为）。
  - **调试 / 可观测性**：出错时回放轨迹，定位是「哪一步思考错了」还是「工具调错了」，是 harness 的 trace/log 的核心对象。

**【权衡 / 追问】**
- 追问 **轨迹级 reward 的难点**：稀疏（只有终点有信号）+ 信用分配难（哪一步该为成败负责）；缓解靠过程奖励（PRM）、对每步打分或回溯。
- 追问 **怎么判一条轨迹好坏**：成功率、步数/工具调用次数/成本、是否有冗余或循环动作；过程开放时常用更强模型当裁判（LLM-as-judge）。
- 追问与 **Reflexion** 的关系（第 4 题）：Reflexion 正是把「失败轨迹 + 反思」写进记忆，下次重试时参考——是轨迹的一种再利用方式。

📖 参考：ReAct — [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629) ｜ Reflexion — [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

---

### 12. Agent 的「协议三件套」：MCP / A2A / AG-UI 分别解决什么？⭐ `#agent #工程 #高频`
**【核心答案】** 三个协议**各管一条连线**，互补而非竞争：
- **MCP**（Model Context Protocol，Anthropic）：**Agent ↔ 工具/数据** —— 标准化「怎么接工具和数据源」。
- **A2A**（Agent2Agent，Google）：**Agent ↔ Agent** —— 标准化「多智能体之间怎么协作」。
- **AG-UI**（Agent–User Interaction Protocol，**CopilotKit**）：**Agent ↔ 用户/前端** —— 标准化「Agent 怎么把过程实时呈现给界面、并接受用户干预」。

```
        ┌──── MCP ────► 工具 / 数据源
Agent ──┼──── A2A ────► 其他 Agent
        └──── AG-UI ──► 前端 / 用户
```

**【深入】AG-UI 是什么（这条最容易被忽略）**
- **定位**：**开放、轻量、事件驱动**的协议，把 agent 后端和前端(如 React)接起来，是**双向桥**。源于 CopilotKit 与 LangGraph / CrewAI 的合作，现已扩到更广生态。
- **为什么需要它**：传统 **请求/响应**架构撑不住 agent —— agent **长时间运行、要流式吐中间过程、非确定性、结构化与非结构化输出混合、还能嵌套组合**。所以改成**事件流**。
- **怎么工作**：前后端交换一串 **JSON 事件**，传输可走 **SSE / WebSocket / HTTP**。
- **约 16–17 个事件类型，分 5 类**：

  | 类别 | 代表事件 | 作用 |
  |---|---|---|
  | **生命周期** | `RUN_STARTED` / `RUN_ERROR` / `RUN_FINISHED` | 标记一次运行的起止与错误 |
  | **消息** | `TEXT_MESSAGE_START` / `_CONTENT` / `_END` | **流式**吐文本(逐块) |
  | **工具** | `TOOL_CALL_START` / `_ARGS` / `_RESULT` | 让前端**看见 agent 在调什么工具** |
  | **步骤** | `STEP_STARTED` / `STEP_FINISHED` | 适配 LangGraph 这类**分步执行**框架 |
  | **状态 / 特殊** | state 快照+增量 / 自定义事件 | 状态同步；不属于以上类别的**兜底** |

  （草案中还有 Activity、Reasoning(思维链可见性)、Meta、可中断的生命周期事件。）
- **四大能力**：
  - **状态同步**：**类型化共享状态**(只读/读写)，用**事件溯源的流式 diff + 冲突解决**做协同。
  - **Human-in-the-Loop**：支持**中断** —— 用户可**暂停/批准/编辑/重试/升级**，**且不丢状态**。
  - **Generative UI**：既支持 app 控制的静态组件，也支持 **agent 提出 UI 树**再校验的声明式界面。
  - **多模态**：类型化附件 + 实时媒体(文件/图/音频/转写)。
- **生态**:8+ 框架有适配(LangGraph、CrewAI、Microsoft Agent Framework、Google ADK、AWS Strands、AG2 等)，OpenAI / Cloudflare 平台在推进。

**【权衡 / 追问】**
- 追问 **为什么不能用普通 REST/请求响应**：agent 是**长任务 + 中间过程有价值 + 需要中途干预**；一问一答既没法流式展示"它正在调什么工具/想什么"，也没法在中途插手。
- 追问 **AG-UI 和 MCP 会不会重叠**：不会。**MCP 是"往下"接工具，AG-UI 是"往上"接人**；一个 agent 通常**同时用两者**(MCP 拿能力，AG-UI 露给用户)。
- 追问 **它解决的真实痛点**：在此之前**每个 agent↔前端集成都是定制的**(自己定义 SSE 格式、自己做状态同步、自己实现审批)；AG-UI 把这"最后一公里"标准化了。
- 追问 **和 Trajectory(第 11 题)的关系**:AG-UI 的事件流本质就是**把轨迹实时投射到 UI** —— 工具事件/步骤事件正是轨迹里的 Action/Observation。

📖 参考：AG-UI 官方文档 — [https://docs.ag-ui.com](https://docs.ag-ui.com) ｜ AG-UI(CopilotKit) — [https://www.copilotkit.ai/ag-ui](https://www.copilotkit.ai/ag-ui) ｜ MCP — [https://modelcontextprotocol.io](https://modelcontextprotocol.io) ｜ A2A — [https://a2aproject.github.io/A2A/](https://a2aproject.github.io/A2A/)

---

### 13. Agent 一般怎么训练？⭐ `#agent #对齐 #高频`
**【核心答案】** 先说一句最重要的：**多数 agent 根本不训模型**——用通用模型 ＋ 工具 ＋ harness，靠 prompt 和上下文工程就够了，训练是 prompt 调不动之后才做的事。真要训，主流四条路线是递进的：**轨迹 SFT（行为克隆）→ 拒绝采样 RFT → 结果奖励 RL（GRPO/PPO）→ 过程监督（PRM / on-policy 蒸馏）**，和 [LLM 笔记](/llm/summary/)里的训练谱系一一对应。

**【深入】**
- **① 轨迹 SFT（行为克隆）**：拿人工示范、更强模型跑出的、或线上跑通的轨迹直接微调。
  - **必须知道的实现细节：要 mask 掉 observation。** 一条轨迹是 `Thought(模型生成) → Action(模型生成) → Observation(工具返回，不是模型生成的) → …`，**loss 只算 Thought 和 Action 的 token**。不 mask 的话模型会去学「猜工具会返回什么」——既浪费容量，又会诱发自问自答式的幻觉。这条同样适用于后面的 RL，很多人第一次训 agent 就栽在这里。
  - 局限：off-policy，有 **exposure bias**——模型从没在自己的错误上训练过（见 LLM 笔记第 8.1 题）。
- **② 拒绝采样 / RFT**：让模型自己跑，**筛掉失败轨迹**，用成功的做 SFT。采样是 on-policy 的（缓解分布错配），但标签是硬的（监督仍稀疏）。便宜、稳定，是 SFT 之后最划算的一步。
- **③ 结果奖励 RL（GRPO / PPO）**：奖励 ＝ 任务成没成（测试通过、答案正确、目标达成）；规则可判时即 **RLVR**。但 agent 场景比单轮推理难得多：

| | 单轮数学 | Agent |
|---|---|---|
| 轨迹长度 | 几百 token | 几千 token × 多轮 |
| 一次 rollout 的代价 | 跑个字符串比对 | **真的去编译 / 请求 / 点击** |
| 可复现性 | 确定 | 环境有状态、网络会抖 |
| credit assignment | 已经很难 | **更难**（跨轮、跨工具调用） |

  第二行最被低估：**数学题的 rollout 几乎免费，agent 的 rollout 要真跑环境**——采样成本高出几个数量级，这是 agent RL 比推理 RL 落地慢的主要原因。而 reward hacking 也更花样百出：让测试通过最省事的办法，可能是删掉测试或把返回值写死。
- **④ 过程监督**：结果奖励太稀疏，于是给中间步骤打分。**PRM** 训一个模型逐步评分；**on-policy 蒸馏**用更强的 agent 当教师、在学生自己的轨迹上逐 token 给完整分布——**监督密度比 RL 高几百倍**，是目前性价比很高的路线（见 LLM 笔记第 8.1 题）。
- **数据从哪来**：

| 来源 | 成本 | 质量 |
|---|---|---|
| 人工示范 | 极贵 | 高，但覆盖窄 |
| 更强模型蒸馏 | 中 | 受教师上限约束 |
| 自采样 ＋ 筛选（RFT） | 低 | 受当前模型上限约束 |
| 合成环境 / 任务 | 中 | 可规模化，但可能失真 |

**【权衡 / 追问】**
- 追问 **什么该训、什么该留给 harness**（这个划分最关键，因为很多「agent 能力」根本不在权重里）：

| 归训练 | 归 harness / prompt |
|---|---|
| 工具调用的格式可靠性 | 工具有哪些、schema 长什么样 |
| **知道什么时候该停** | 步数上限、超时 |
| 长程规划、从错误中恢复 | 上下文压缩、记忆检索 |
| 少走弯路、少调冗余工具 | 权限、沙箱 |

  判断标准很直接：**换个模型就没了的才该训；换个 harness 就变的，别训。**
- 追问 **为什么轨迹是天然的训练数据**：一条轨迹既是评估对象、又是训练样本、还是调试材料（见第 11 题）。RFT 从中挑好的，RL 把它当 episode，蒸馏在它上面逐 token 对齐——三条路线消费的是同一份东西。
- 追问 **GRPO 用在 agent 上的具体困难**：优势是**一条轨迹一个标量、广播到所有 token**（见 LLM 笔记第 9.1 题）。单轮推理已经难分辨是哪步起作用，agent 还要跨多轮和多次工具调用，信用分配进一步恶化——这正是过程监督的动机。
- 追问 **先做哪一步**：一般是 SFT 打底 → RFT 提一档 → 有稳定环境和可验证奖励再上 RL。没有可靠的自动判分就别急着上 RL，否则是在优化一个错的目标。

📖 参考：Toolformer — [https://arxiv.org/abs/2302.04761](https://arxiv.org/abs/2302.04761) ｜ STaR — [https://arxiv.org/abs/2203.14465](https://arxiv.org/abs/2203.14465) ｜ GKD（on-policy 蒸馏）— [https://arxiv.org/abs/2306.13649](https://arxiv.org/abs/2306.13649)
