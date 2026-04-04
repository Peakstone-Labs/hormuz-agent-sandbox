<div align="center">

<img src="frontend/public/logo.png" alt="Peakstone Labs" width="200" />

# Strait of Hormuz Simulator

### Multi-Agent Geopolitical Sandbox

*Each nation is an independent AI agent. Tune the parameters. Watch the game theory emerge.*

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](#license)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Vue 3](https://img.shields.io/badge/Vue-3-green.svg)](https://vuejs.org)

[Live Demo](https://www.peakstone-labs.com/hormuz_simulator) · [Report Bug](https://github.com/Peakstone-Labs/hormuz-agent-sandbox/issues) · [Add a Country](#add-a-new-country)

**[English](#what-is-this)** | **[中文](#zh-cn)**

</div>

---

## What Is This?

A real-time geopolitical simulation powered by multiple AI agents, set against the **2026 Strait of Hormuz crisis** — a real, ongoing conflict as of April 2026.

Each country (Iran, US, Israel, Gulf States) is controlled by an independent LLM agent with its own:
- **Strategic doctrine** — goals, red lines, behavioral tendencies
- **Constraints** — missile stockpiles, economic tolerance, domestic politics
- **Information** — shared situation briefing + rolling memory of prior rounds

You configure the chaos level, activate scenario modifiers ("tags"), adjust each nation's parameters, and watch how the AI agents interact — producing emergent geopolitical dynamics that no single agent was programmed to create.

### Key Features

- 🎭 **4 AI-driven nations** with deeply researched behavioral profiles
- 🏷️ **11 pluggable scenario tags** (Houthi Wildcard, Nuclear Brinkmanship, China Mediator...)
- 🛢️ **Real-time oil market agent** that prices in geopolitical risk
- 🎛️ **20+ adjustable parameters** — aggressiveness, constraints, chaos factor
- 🌊 **SSE streaming** — watch each agent "think" in real-time
- 🌐 **Bilingual** — full Chinese/English support (UI + LLM output)
- 📊 **Shareable report cards** — download as image with QR code
- 🔑 **BYOK** — bring your own API key, supports 8+ models
- 🆓 **Free trial pool** — powered by Gemini Flash

<div align="center">
<img src="https://img.shields.io/badge/Gemini-Flash-blue?logo=google" />
<img src="https://img.shields.io/badge/GPT--4o-supported-green?logo=openai" />
<img src="https://img.shields.io/badge/Claude-supported-orange?logo=anthropic" />
<img src="https://img.shields.io/badge/DeepSeek-supported-purple" />
</div>

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Frontend (Vue 3 + Tailwind)                         │
│  ┌─────────────┐  ┌──────────────────────────────┐   │
│  │ Config Panel │  │ Terminal Output (SSE stream)  │   │
│  │  - Chaos     │  │  🇮🇷 Iran: action...          │   │
│  │  - Tags      │  │  🇺🇸 US: action...            │   │
│  │  - Actors    │  │  📊 Oil: $128 ↑16%           │   │
│  └─────────────┘  └──────────────────────────────┘   │
└──────────────────────┬───────────────────────────────┘
                       │ POST /api/simulate (SSE)
┌──────────────────────▼───────────────────────────────┐
│  Backend (FastAPI + LiteLLM)                         │
│                                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │
│  │  Iran    │ │   US    │ │ Israel  │ │   Gulf    │  │
│  │  Agent   │ │  Agent  │ │  Agent  │ │  States   │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └─────┬─────┘  │
│       └───────────┴───────────┴─────────────┘        │
│                       │                               │
│              ┌────────▼────────┐                      │
│              │  Market Agent   │                      │
│              │  (Oil pricing)  │                      │
│              └─────────────────┘                      │
│                       │                               │
│              ┌────────▼────────┐                      │
│              │    LiteLLM      │ → Gemini / GPT-4o /  │
│              │   (any model)   │   Claude / DeepSeek   │
│              └─────────────────┘                      │
└──────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Gemini API key ([free at Google AI Studio](https://aistudio.google.com/))

### 1. Clone & Setup Backend

```bash
git clone https://github.com/Peakstone-Labs/hormuz-agent-sandbox.git
cd hormuz-simulator/backend

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — add your GEMINI_API_KEY
```

### 2. Setup Frontend

```bash
cd ../frontend
npm install
```

### 3. Run

```bash
# Terminal 1 — Backend
cd backend
python main.py
# → http://localhost:8000

# Terminal 2 — Frontend
cd frontend
npm run dev
# → http://localhost:5173
```

Open http://localhost:5173 and start simulating.

---

## Project Structure

```
hormuz-simulator/
├── backend/
│   ├── souls/                  # 🎭 One markdown per country — fork & customize
│   │   ├── iran.md
│   │   ├── us.md
│   │   ├── israel.md
│   │   └── gulf_states.md
│   ├── tags/                   # 🏷️ Pluggable scenario modifiers
│   │   ├── houthi_wildcard.md
│   │   ├── nuclear_brinkmanship.md
│   │   ├── china_mediator.md
│   │   └── ... (11 tags)
│   ├── agents.py               # Multi-agent engine
│   ├── config_loader.py        # YAML frontmatter parser
│   ├── models.py               # Pydantic schemas
│   ├── main.py                 # FastAPI app
│   ├── presets.json             # Scenario config
│   └── i18n.json               # UI strings (en/zh)
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/         # Vue components
│   │   └── composables/        # State management
│   └── public/
│       └── logo.png
└── README.md
```

---

## Customization

### Add a New Country

Create `backend/souls/china.md`:

```markdown
---
id: China
display_name: People's Republic of China
emoji: "🇨🇳"
i18n:
  zh:
    display_name: 中华人民共和国
    short_name: 中国
    description: Your description here
  en:
    display_name: People's Republic of China
    short_name: China
    description: Your description here
default_profile:
  aggressiveness: 0.3
  economic_tolerance: 0.8
  red_lines:
    - Direct military attack on Chinese assets
  constraints:
    economic_leverage: 0.9
    military_projection: 0.4
---

# China — Politburo Standing Committee

Your system prompt here. Describe China's strategic doctrine,
goals, constraints, and behavioral tendencies...
```

Restart the backend. China automatically appears in the UI.

### Add a New Tag

Create `backend/tags/your_tag.md` with the same frontmatter pattern. See existing tags for examples.

### Change the Scenario

Edit `backend/presets.json` to change the background briefing, initial oil price, or market agent prompt. The current scenario is calibrated to real events as of April 4, 2026.

---

## Supported Models

| Provider | Models | Notes |
|----------|--------|-------|
| Google Gemini | `gemini/gemini-3-flash-preview`, `gemini/gemini-2.5-pro-preview-05-06` | Free trial default |
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `o3-mini` | Best structured output |
| Anthropic | `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` | Strong reasoning |
| DeepSeek | `deepseek/deepseek-chat`, `deepseek/deepseek-reasoner` | Cheapest option |

BYOK users select their model in the UI. The backend uses [LiteLLM](https://github.com/BerriAI/litellm) for unified model access.

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/presets?locale=en` | GET | Scenario config, actors, tags |
| `/api/i18n?locale=zh` | GET | UI strings |
| `/api/simulate` | POST | Run one round → SSE stream |

### POST /api/simulate

```json
{
  "client_uuid": "abc-123",
  "chaos_factor": 0.5,
  "round_num": 1,
  "step_unit": "day",
  "active_tags": ["houthi_wildcard", "nuclear_brinkmanship"],
  "locale": "zh",
  "api_key": "optional-your-key",
  "model": "gpt-4o",
  "previous_summaries": [],
  "previous_oil_price": null
}
```

Returns SSE stream with events: `actor`, `market`, `round_complete`.

---

## Deployment

### Docker (Recommended)

```bash
docker build -t hormuz-sim .
docker run -p 8000:8000 -e GEMINI_API_KEY=your-key hormuz-sim
```

### VPS + Cloudflare

1. Deploy backend to a VPS (Hetzner/Vultr, ~$5/mo)
2. Build frontend: `cd frontend && npm run build`
3. Serve `frontend/dist/` via FastAPI or Nginx
4. Point `api.peakstone-labs.com` → VPS IP via Cloudflare (orange cloud)

---

## Acknowledgments

- Scenario research informed by [Odysseus](https://mp.weixin.qq.com/) geopolitical analysis reports
- Inspired by [MiroFish](https://github.com/666ghj/MiroFish) swarm intelligence engine
- Built with [LiteLLM](https://github.com/BerriAI/litellm), [FastAPI](https://fastapi.tiangolo.com/), [Vue 3](https://vuejs.org/)

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Peakstone Labs](https://www.peakstone-labs.com)**

*Geopolitics is the ultimate multiplayer game. This is the sandbox.*

</div>

---

<a id="zh-cn"></a>

## 🇨🇳 这是什么

一个基于**多智能体（Multi-Agent）架构**的实时地缘政治推演沙盒，以 **2026 年霍尔木兹海峡危机**（真实进行中的冲突）为背景。

每个国家（伊朗、美国、以色列、海湾国家）由独立的 LLM 智能体控制，拥有各自的：
- **战略信条** — 目标、红线、行为倾向
- **约束条件** — 导弹库存、经济承受力、国内政治
- **信息环境** — 共享态势简报 + 滚动记忆

你调节混沌指数、激活情景标签、微调各国参数，然后观察 AI 智能体之间的博弈如何涌现出 — 没有任何单一智能体被编程产生的 — 地缘政治动态。

### 核心特性

- 🎭 **4 个 AI 驱动的国家**，基于深度研究的行为画像
- 🏷️ **11 个可插拔的情景标签**（胡塞牌、核边缘博弈、中国斡旋...）
- 🛢️ **实时油价智能体**，对地缘风险进行定价
- 🎛️ **20+ 可调参数** — 激进度、约束条件、混沌指数
- 🌊 **SSE 流式传输** — 实时观看每个智能体"思考"
- 🌐 **中英双语** — UI + LLM 输出完整支持
- 📊 **可分享的报告卡片** — 下载为图片，带二维码
- 🔑 **BYOK 自带密钥**，支持 8+ 模型
- 🆓 **免费试玩池** — 由 Gemini Flash 驱动

### 快速开始

```bash
# 克隆项目
git clone https://github.com/Peakstone-Labs/hormuz-agent-sandbox.git
cd hormuz-simulator

# 后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # 编辑 .env，填入 GEMINI_API_KEY
python main.py             # → http://localhost:8000

# 前端（新终端）
cd frontend
npm install
npm run dev                # → http://localhost:5173
```

### 自定义

**添加新国家**：在 `backend/souls/` 下创建 markdown 文件，写好 frontmatter 和系统提示词，重启后端自动加载。

**添加新标签**：在 `backend/tags/` 下创建 markdown 文件，格式参考已有标签。

**修改场景**：编辑 `backend/presets.json` 中的背景简报、初始油价或市场智能体提示词。

详细文档请参阅上方英文部分。

---

<div align="center">

**由 [Peakstone Labs](https://www.peakstone-labs.com) 构建**

*地缘政治是终极多人博弈。这是沙盒。*

</div>
