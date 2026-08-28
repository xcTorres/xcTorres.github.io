---
title: "Agent Notes"
subtitle: "Planning · Tools · Memory · Multi-Agent"
topic: agent
category: summary
order: 1
lang: en
pair: agent-summary
source: "Agent知识总结.md"
---

* TOC
{:toc .llm-toc-list}

> **Scope**: planning · tools · memory · multi-agent. Every entry runs **core answer → how it works → trade-offs / follow-ups → references**; ⭐ marks the points worth digging into.
>
> **See also**: [LLM Notes](/llm/summary/) · [VLM Notes](/vlm/summary/)

---

# Part V: Agents

### 25. What is an LLM agent, and what is it made of? ⭐ `#agent #core`
**【Core answer】** An LLM acting as the "brain", completing multi-step tasks on its own through **planning + tools + memory + reflection**, rather than answering in a single turn. Four modules: planning (decomposing the task), tool use (calling external APIs for capability and information), memory (short-term context plus long-term storage), and reflection (self-correction from feedback).

**【How it works】**
- Agent = LLM (reasoning and decisions) + tools (extending what it can reach) + a control loop (perceive → decide → act → observe).
- What separates it from "just prompting": an agent has state, runs in a loop, interacts with an environment and adjusts on feedback.

**【Trade-offs / follow-ups】** A common follow-up is **when an agent is over-engineering**. Simple tasks are steadier and cheaper with a plain prompt or RAG; agents earn their keep on complex work that genuinely needs multiple steps, dynamic decisions and tool calls.

---

### 26. What is ReAct, and why does it work? ⭐ `#agent #core`
**【Core answer】** Reasoning and acting, interleaved: the model loops through **Thought (reason) → Action (call a tool) → Observation (result)** until it is done. Reasoning steers the action, and the action's real-world feedback corrects the reasoning.

**【How it works】**
- Pure chain-of-thought reasons only "in its head" — it cannot fetch outside information and errors compound. Pure acting has no plan. ReAct combines them: reasoning picks the next action, observation corrects the reasoning.
- Interacting with the outside world (search, APIs) cuts hallucination and pulls in current information.

**【Trade-offs / follow-ups】** A common follow-up is **how ReAct fails**: it gets stuck in loops, repeats useless actions, or lets reasoning and action drift apart. Pair it with a step cap and a reflection mechanism.

📖 Reference: ReAct — [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

---

### 27. Function calling / tool use: the mechanism and what matters in practice `#agent #systems`
**【Core answer】** Give the model each tool's **schema** (name, parameters, description); the model emits a structured call (usually JSON); external code executes it and feeds the result back so the model can keep reasoning.

**【How it works】**
- The model never executes anything. It only decides **which tool to call and with what arguments** — execution and result hand-back are the agent framework's job.
- On the training side: fine-tune on data containing tool-call trajectories so the model learns when and how to call (the Toolformer idea).

**【Trade-offs / follow-ups】**
- What matters in practice: validating the argument schema, retrying failed calls, tool-selection accuracy, parallel calls, and stopping the model from inventing tools that do not exist or passing nonsense arguments.
- A common follow-up is **how to raise tool-call accuracy**: clear tool descriptions, few-shot examples, constrained decoding (force valid JSON), and exposing fewer tools at once.

📖 Reference: Toolformer — [https://arxiv.org/abs/2302.04761](https://arxiv.org/abs/2302.04761)

---

### 28. What planning methods do agents use? `#agent`
**【Core answer】** CoT (a single reasoning chain), ToT (Tree of Thoughts — explore several branches and backtrack), Plan-and-Execute (plan the whole thing first, then work through it), and Reflexion (after a failure, reflect in natural language and retry).

**【How it works】**
- **CoT**: break the problem into intermediate steps. Good for one-shot reasoning questions.
- **ToT**: generate several candidate thoughts per step, then search (BFS/DFS) and score to pick the best. Good for problems needing trial and backtracking, like puzzles.
- **Plan-and-Execute**: have the LLM lay out a full plan, then execute item by item. Fewer LLM calls than ReAct and better suited to long tasks, but only as good as the plan.
- **Reflexion**: write the failed trajectory and the reflection on it into memory, and consult that on the retry.

**【Trade-offs / follow-ups】** A common follow-up is **ReAct vs. Plan-and-Execute**: the former is flexible and adapts as it goes but burns more calls; the latter is efficient, but a wrong plan poisons everything downstream.

📖 Reference: Tree of Thoughts — [https://arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601) ｜ Reflexion — [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

---

### 29. The full RAG pipeline, and where to optimise it ⭐ `#agent #systems #core`
**【Core answer】** The pipeline: chunk the documents → embed and index → retrieve top-k → splice into the prompt → generate. Every stage has room to improve.

**【How it works】**
- **Chunking**: fixed length with overlap, semantic splitting, or structural splitting (by heading or paragraph). Chunks that are too big carry noise; too small and you lose context.
- **Retrieval**: (1) **hybrid retrieval** = vectors (semantics) + BM25 (keywords); (2) **reranking** — a cross-encoder reorders the recalled set, which lifts quality noticeably; (3) **query rewriting / expansion** — turn a colloquial question into something retrievable (HyDE, multi-query).
- **Generation**: cite sources, stop the model from ignoring what it retrieved, and keep the context from overflowing.
- **Going further**: GraphRAG (organise with a knowledge graph), multi-hop retrieval (several rounds for complex questions), Self-RAG (the model decides whether to retrieve and judges what came back).

**【Trade-offs / follow-ups】**
- A common follow-up is **why RAG fails**: poor recall (the most frequent root cause), badly cut chunks, a missing reranker, and context so long the middle gets lost.
- A common follow-up is **RAG vs. long context**: they are complementary. RAG saves tokens, cites sources and keeps knowledge updatable; long context skips the retrieval engineering but is expensive and loses information in the middle.

📖 Reference: RAG — [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

---

### 30. How should an agent's memory be designed? `#agent`
**【Core answer】** **Short-term memory** is the current conversation context, bounded by the context window. **Long-term memory** puts history and knowledge in a vector store to be retrieved on demand. Add summarisation, importance scoring and time decay on top.

**【How it works】**
- When the context fills up: rolling summarisation (compress old turns into a summary), keep only what matters, or push it out to a vector store and retrieve.
- Generative Agents (the Stanford "small town") retrieves memories by scoring a memory stream on importance, relevance and recency — the classic design.

**【Trade-offs / follow-ups】** A common follow-up is **what goes wrong with retrieval-based memory**: bad recall makes the agent "forget" or "misremember". It needs a good write policy (what is worth storing) and a good read policy (how to retrieve it).

---

### 31. Multi-agent systems: what they buy you, and what they cost `#agent`
**【Core answer】** The upside: role specialisation (planner / executor / reviewer), parallelism, decomposition of complex tasks, and quality gains from mutual review. The cost: communication and coordination overhead, errors compounding as they pass between agents, termination conditions that are hard to define, and higher cost and latency.

**【How it works】**
- Common patterns: pipelines (sequential), debate (arguing improves correctness), and supervisor-worker (a supervisor hands out work).
- Frameworks: AutoGen, CrewAI, LangGraph, MetaGPT.

**【Trade-offs / follow-ups】** A common follow-up is **whether multi-agent really beats a single agent**. Not necessarily — on simple tasks extra agents only add cost and instability. It depends on whether the task genuinely benefits from division of labour or review.

---

### 32. Why are agents unreliable, and how do you stabilise them? ⭐ `#agent #core`
**【Core answer】** The main culprit is **compounding error** — in a multi-step task any single misstep can derail everything after it — plus hallucinated tool calls, infinite loops and weak long-horizon planning. What helps: step limits and timeouts, validation and retry at each step, self-correction via ReAct/Reflexion, human-in-the-loop at critical steps, constrained structured output, and thorough logging and observability.

**【How it works】**
- At a 95% per-step success rate, ten steps in series succeed only about 0.95¹⁰ ≈ 60% of the time. That is the mathematical heart of agent unreliability.
- Which is why "take fewer steps", "verify each step" and "make it recoverable" usually beat "make each step smarter".

**【Trade-offs / follow-ups】** A common follow-up is **how to localise a failure**: use tracing (LangSmith and similar) to walk the thought/action/observation sequence and find the first step that went wrong.

---

### 33. How do you evaluate an agent? `#agent`
**【Core answer】** Metrics: task success rate, number of steps / calls / cost, latency, tool-call accuracy, robustness. Benchmarks: AgentBench (broad), GAIA (general assistant), WebArena (web operation), SWE-bench (real code fixes), τ-bench (tools plus dialogue).

**【How it works】** The hard part is that tasks are open-ended and the process resists automatic scoring. The usual compromise combines "was the end state reached" with "was the trajectory any good", falling back on a stronger model as judge (LLM-as-judge) where necessary — with its biases in mind.

**【Trade-offs / follow-ups】** A common follow-up is **the pitfalls of LLM-as-judge**: position bias, length bias and self-preference. Shuffle the order, write an explicit rubric, and spot-check by hand.

---

### 34. What is an agent harness? And what is a skill? ⭐ `#agent #systems #core`
**【Core answer】** The **harness** is the engineering layer wrapped around the LLM that keeps it running: it assembles the context, parses the model's tool calls, actually executes the tools, feeds the results back, and loops — in other words, it is the **concrete implementation** of ReAct's perceive-decide-act-observe cycle. A **skill** is a capability package loaded on demand: typically a structured set of instructions or procedures (plus optional scripts, templates and reference documents) telling the model *how to do* a class of task, injected into context only when it is needed. Skills in Claude Code / the Claude Agent SDK are the canonical example.

**【How it works】**
- **What the harness does** (all the parts the model does not): context assembly and trimming, tool-schema injection, parsing and executing tool calls, error retries, loop control (step count, timeouts, termination), state and memory management, permissions and sandboxing, and observability (traces and logs). Put another way: **the model is the brain, the harness is the nervous system and the body**.
- **A skill is progressive disclosure**: rather than cramming every piece of domain knowledge into the system prompt (wasting tokens and diluting attention), keep a one-line description around and pull the full skill into context only when the model judges it relevant. That turns "what the agent can do" from a hard-coded prompt into **pluggable, reusable, versionable modules**.
- A skill usually contains a trigger description (when to use it), the steps or best practices, any scripts or tools it calls, and examples and templates. Against a **tool/function**: a tool is *one executable atomic action*; a skill is *a methodology for a class of work*, often packaging the use of several tools.
- Against **RAG**: RAG retrieves *factual knowledge* to answer with; a skill loads *procedural knowledge* — an operating manual — to act on.

**【Trade-offs / follow-ups】**
- A common follow-up is **why a harness is needed at all rather than letting the model run itself**: the model is a stateless next-token predictor. It has no loop, cannot really execute code, and persists nothing — the harness supplies all of it. The quality of the harness (context engineering, tool reliability, error recovery) often decides an agent's success more than swapping in a stronger model.
- A common follow-up is **the idea underneath skills and harnesses: context engineering** — deciding, within a finite window, what belongs in context right now and what does not. Skills load on demand; the harness's rolling summaries and memory retrieval trim dynamically. Both fight the same thing: longer context is both more diluted and more expensive.
- A common follow-up is **the relationship to MCP (Model Context Protocol)**: MCP standardises *how tools and data sources plug in*, and the harness obtains its tools through it; skills are the layer above, about *how to use those tools well*.
- A common follow-up is **who does this in practice**: Claude Code (harness + skills + subagents), OpenAI's Assistants/Responses, and the various agent SDKs. A frequent companion pattern is the **subagent** — hand a complex skill to an agent with its own context so the main context stays clean.

📖 Reference: Anthropic, "Building effective agents" — [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents) ｜ Agent Skills — [https://www.anthropic.com/news/skills](https://www.anthropic.com/news/skills) ｜ MCP — [https://modelcontextprotocol.io](https://modelcontextprotocol.io)

---

### 35. What is an agent trajectory, and what is it for? ⭐ `#agent #core`
**【Core answer】** A trajectory is the **complete interaction sequence** an agent walks through to finish a task — the whole action history from receiving the task to ending. Under ReAct it is a run of `(Thought → Action → Observation)` triples ending in a final answer. One trajectory is roughly an **episode** in reinforcement-learning terms.

**【How it works】**
- The shape: `task → thought → action (call a tool) → observation (tool returns) → thought → … → final answer`. Strung together, that record is the trajectory.
- Four uses:
  - **Evaluation**: judge not only whether the final answer is right but whether the path was sensible — no detours, no loops, tools used appropriately. This is the "end state + trajectory quality" pairing from question 33.
  - **Training data**: collect good trajectories for SFT, or use **rejection sampling / DPO** to pick better-versus-worse pairs from several trajectories so the model learns a stronger action policy.
  - **Reinforcement learning**: a trajectory is an episode, each step a `(state, action)` pair; add a reward and compute policy gradients (RLHF/GRPO for agent behaviour).
  - **Debugging and observability**: replay the trajectory when something breaks and find whether a thought went wrong or a tool was called wrong. This is what the harness's traces and logs are recording.

**【Trade-offs / follow-ups】**
- A common follow-up is **why trajectory-level reward is hard**: it is sparse (signal only at the end) and credit assignment is difficult (which step deserves blame). Process reward models (PRM), per-step scoring and backtracking all help.
- A common follow-up is **how to judge a trajectory**: success rate, step count / tool calls / cost, and whether there were redundant or looping actions. Where the process is open-ended, a stronger model as judge is the usual fallback.
- A common follow-up is **the link to Reflexion** (question 28): Reflexion is exactly the practice of writing a failed trajectory plus its reflection into memory and consulting it on retry — one way of reusing trajectories.

📖 Reference: ReAct — [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629) ｜ Reflexion — [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

---

### 36. The three agent protocols: what MCP, A2A and AG-UI each solve ⭐ `#agent #systems #core`
**【Core answer】** Each protocol owns **one edge of the graph**; they complement rather than compete:
- **MCP** (Model Context Protocol, Anthropic): **agent ↔ tools/data** — standardises how tools and data sources plug in.
- **A2A** (Agent2Agent, Google): **agent ↔ agent** — standardises how multiple agents collaborate.
- **AG-UI** (Agent–User Interaction Protocol, **CopilotKit**): **agent ↔ user/front end** — standardises how an agent surfaces its progress to an interface and accepts user intervention.

```
        ┌──── MCP ────► tools / data sources
Agent ──┼──── A2A ────► other agents
        └──── AG-UI ──► front end / user
```

**【How it works】What AG-UI is (the edge most often overlooked)**
- **What it is**: an **open, lightweight, event-driven** protocol connecting an agent backend to a front end (React, say) — a **two-way bridge**. It grew out of CopilotKit's work with LangGraph and CrewAI and has since spread wider.
- **Why it is needed**: a traditional **request/response** architecture cannot carry an agent. Agents **run for a long time, need to stream intermediate progress, behave non-deterministically, mix structured and unstructured output, and nest and compose**. Hence an event stream instead.
- **How it works**: the two sides exchange a stream of **JSON events**, transported over **SSE, WebSocket or HTTP**.
- **Roughly 16–17 event types in 5 families**:

  | Family | Representative events | Purpose |
  |---|---|---|
  | **Lifecycle** | `RUN_STARTED` / `RUN_ERROR` / `RUN_FINISHED` | Mark the start, end and failure of a run |
  | **Messages** | `TEXT_MESSAGE_START` / `_CONTENT` / `_END` | **Stream** text chunk by chunk |
  | **Tools** | `TOOL_CALL_START` / `_ARGS` / `_RESULT` | Let the front end **see which tool the agent is calling** |
  | **Steps** | `STEP_STARTED` / `STEP_FINISHED` | Fit step-wise frameworks like LangGraph |
  | **State / special** | State snapshots and deltas, custom events | State sync, plus a catch-all for anything else |

  (Drafts also include Activity, Reasoning — visibility into the chain of thought — Meta, and interruptible lifecycle events.)
- **Four capabilities**:
  - **State sync**: **typed shared state** (read-only or read-write), kept in step by **event-sourced streaming diffs with conflict resolution**.
  - **Human-in-the-loop**: supports **interruption** — the user can pause, approve, edit, retry or escalate **without losing state**.
  - **Generative UI**: both app-controlled static components and declarative interfaces where the **agent proposes a UI tree** that is then validated.
  - **Multimodal**: typed attachments plus live media (files, images, audio, transcription).
- **Ecosystem**: adapters in 8+ frameworks (LangGraph, CrewAI, Microsoft Agent Framework, Google ADK, AWS Strands, AG2 and others), with OpenAI and Cloudflare platforms moving in the same direction.

**【Trade-offs / follow-ups】**
- A common follow-up is **why plain REST/request-response will not do**: agents are **long-running, their intermediate process has value, and users need to step in mid-flight**. A single question-and-answer exchange can neither stream "what it is calling and thinking" nor accept intervention along the way.
- A common follow-up is **whether AG-UI and MCP overlap**. They do not. **MCP reaches *down* to tools; AG-UI reaches *up* to people.** An agent typically uses **both** — MCP for capability, AG-UI to expose itself to the user.
- A common follow-up is **the real pain it removes**: before it, **every agent-to-front-end integration was bespoke** — your own SSE format, your own state sync, your own approval flow. AG-UI standardises that last mile.
- A common follow-up is **the link to trajectories** (question 35): AG-UI's event stream is essentially **the trajectory projected onto the UI in real time** — the tool and step events *are* the actions and observations in the trajectory.

📖 Reference: AG-UI docs — [https://docs.ag-ui.com](https://docs.ag-ui.com) ｜ AG-UI (CopilotKit) — [https://www.copilotkit.ai/ag-ui](https://www.copilotkit.ai/ag-ui) ｜ MCP — [https://modelcontextprotocol.io](https://modelcontextprotocol.io) ｜ A2A — [https://a2aproject.github.io/A2A/](https://a2aproject.github.io/A2A/)

---

# Appendix A: Core paper index (agents)

**Agents**
- ✅ ReAct — [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)
- ✅ Toolformer — [https://arxiv.org/abs/2302.04761](https://arxiv.org/abs/2302.04761)
- ✅ Tree of Thoughts — [https://arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601)
- ✅ Reflexion — [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)
- ✅ RAG (Lewis 2020) — [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

**Protocols and specifications** (not papers — see question 36)
- **MCP** (agent ↔ tools/data, Anthropic) — [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **A2A** (agent ↔ agent, Google) — [https://a2aproject.github.io/A2A/](https://a2aproject.github.io/A2A/)
- **AG-UI** (agent ↔ user/front end, CopilotKit) — [https://docs.ag-ui.com](https://docs.ag-ui.com) ｜ [https://www.copilotkit.ai/ag-ui](https://www.copilotkit.ai/ag-ui)
