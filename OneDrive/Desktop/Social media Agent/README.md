# 🚀 SocialAgent.ai — AI-Powered Social Media Agent (IBM Granite x watsonx.ai)

A **premium, production-ready SaaS platform** that combines 6 specialized AI agents with IBM's Granite foundation models on watsonx.ai to deliver end-to-end social media marketing superpowers.

> Create viral content, predict trends, score engagement potential, analyze sentiment, outperform competitors, and get AI strategy recommendations — all in one beautiful glassmorphic interface.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **AI Content Creator** | Generates platform-optimized posts, captions, blogs, Twitter threads, LinkedIn articles, Instagram + Facebook copy |
| 🔥 **Trend Predictor** | Identifies emerging trends, viral velocity, sentiment, platform distribution + content angle ideas |
| 💯 **Viral Score Predictor** | 8-factor weighted scoring + projected reach/ER/shares with specific improvement prescriptions |
| 🏷️ **Smart Hashtag Generator** | Mixes broad/niche/branded/trending/location tags with realistic post-volume and ER estimates |
| 🗓️ **Content Calendar** | AI-scheduled recommendations with best posting times, formats, categories, and engagement predictions |
| 🎯 **Competitor Analysis** | Ranking matrix, benchmarking, strengths/weaknesses, and 90-day gap-attack action plan |
| 💬 **Sentiment Intelligence** | 5-bucket sentiment, 10-emotion taxonomy, topic-level breakdowns, and risk alerts |
| 📈 **Analytics Dashboard** | 10+ interactive charts, KPIs, platform radar, format analysis, forecast, AI insights |
| 🤖 **AI Chat Assistant** | Natural-language router detects intent and dispatches to the correct specialist agent |

---

## 🤖 Multi-Agent Architecture

Six specialist agents work as a coordinated team:

1. **📝 Content Creation Agent** — Platform-specific copy, storytelling, CTA optimization
2. **📊 Trend Analysis Agent** — Trend velocity, lifecycle prediction, opportunity identification
3. **🏷️ Hashtag Recommendation Agent** — 4-category mix, competitor research, banned-tag avoidance
4. **💭 Sentiment Analysis Agent** — Emotion taxonomy, topic clustering, sarcasm/urgency flags
5. **📈 Analytics Agent** — KPIs, cohort breakdowns, forecasts, AI strategic insights
6. ⚙️ **Content Optimization Agent** — Viral score, 8-factor diagnosis, rewritten optimized variants

All agents run on **IBM Granite** models (13B Chat / 13B Instruct) via **IBM watsonx.ai**, with intelligent fallbacks for local development.

---

## 🎨 UI Highlights

- **Glassmorphism** aesthetic with backdrop blur + gradient glow
- **Light/Dark mode** toggle (OS-aware, persists to localStorage)
- **10+ interactive Chart.js** visualizations (line, bar, radar, gauge, area)
- **Smooth animations**: fade-up, stagger, float, pulse-glow, slide-in
- **Fully responsive** mobile navigation with hamburger menu
- **SaaS-style dashboard**: KPI cards, hero preview, animated score ring
- **AI chat with agent-routing**: tool-usage badges, streaming-like indicators
- **Color system**: Indigo → Violet → Pink gradient theme

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| **Backend** | Python 3.11 · Flask 3 · CORS · Gunicorn (prod) |
| **AI** | IBM watsonx.ai SDK · IBM Granite 13B Chat / Instruct |
| **Frontend** | HTML5 · Tailwind CSS · Chart.js · Vanilla JS (no build step) |
| **Typography** | Inter (UI) + Space Grotesk (Display) from Google Fonts |
| **Deployment** | Docker · Docker Compose · Healthchecks |
| **Security** | `.env` secrets · CORS allow-list · No inline credentials |

---

## 📁 Project Structure

```
Social media Agent/
├── backend/
│   ├── app.py                          # Flask entrypoint
│   ├── config.py                       # ⭐ AGENT_INSTRUCTIONS + app config
│   ├── agents/
│   │   ├── content_agent.py            # Content Creation Agent
│   │   ├── trend_agent.py              # Trend Analysis Agent
│   │   ├── hashtag_agent.py            # Hashtag Recommendation Agent
│   │   ├── sentiment_agent.py          # Sentiment Analysis Agent
│   │   ├── analytics_agent.py          # Analytics Agent
│   │   └── optimization_agent.py       # Viral Score + Optimization Agent
│   ├── services/
│   │   └── watsonx_service.py          # IBM watsonx.ai integration + fallbacks
│   ├── routes/
│   │   ├── content_routes.py           # /api/content/* (generate, hashtags, viral, calendar, competitor)
│   │   ├── analysis_routes.py          # /api/analysis/* (trends, sentiment, analytics, health)
│   │   └── chat_routes.py              # /api/chat/message (intent-routed assistant)
│   ├── templates/
│   │   └── index.html                  # Premium frontend (single-page)
│   └── static/
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🛠️ AGENT_INSTRUCTIONS — Your Control Panel

**Open `backend/config.py` and edit the `AGENT_INSTRUCTIONS` dictionary.** Customize every aspect of your agents:

```python
AGENT_INSTRUCTIONS = {
    "brand_voice":          # Personality, tone, style, language, words to avoid
    "content_style":        # Lengths, paragraphs, emojis, hashtag counts, CTA position
    "platforms":            # Enable/disable platforms, best times/days, content types, limits
    "posting_strategy":     # Posts/week, content mix %, A/B testing, recycling
    "safety_rules":         # Prohibited content, disclosures, thresholds
    "marketing_goals":      # Primary goal, KPIs, target audience, brand messages, CTAs
    "trend_settings":       # Sources, freshness, min volume, relevance threshold
    "hashtag_settings":     # Type mix %, location-based, industry-specific, competitor research
    "analytics_settings":   # Tracking period, competitors, benchmark industry, AI insight frequency
}
```

---

## 🚀 Quick Start (Local Development)

### Step 1: Get your IBM Cloud credentials

1. Go to [https://cloud.ibm.com](https://cloud.ibm.com) → Create an account (free tier works)
2. Create a **watsonx.ai** project → Go to **Manage → General** → Copy the **Project ID**
3. Create an **API Key** → IAM → API Keys → Create (save it, shown only once)

### Step 2: Configure environment

```powershell
# Copy template
copy .env.example .env
```

Edit `.env`:
```
IBM_CLOUD_API_KEY=YOUR_KEY_HERE
IBM_WATSONX_PROJECT_ID=YOUR_PROJECT_ID_HERE
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_GENERATION_MODEL_ID=granite-13b-chat-v2
IBM_REASONING_MODEL_ID=granite-13b-instruct-v2
```

> 💡 **No credentials yet?** No problem. The platform falls back to high-quality heuristic + template mode so you can test the UI/UX fully offline.

### Step 3: Install + run

```powershell
cd "Social media Agent"
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
cd backend
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## 🐳 Docker Deployment

```powershell
# From the project root
docker-compose up -d --build
```

Then open **http://localhost:5000**. Container uses Gunicorn with 4 workers, 2 threads, 120s timeout.

```powershell
# View logs
docker-compose logs -f social-media-agent

# Check health
curl http://localhost:5000/api/health
```

---

## ☁️ Production Deployment Options

### IBM Cloud Code Engine
```bash
ibmcloud login
ibmcloud ce project create --name social-agent
ibmcloud ce app create --name social-agent \
  --image . --registry-secret YOUR-REGISTRY-SECRET \
  --env-from-secret watsonx-credentials \
  --port 5000 --min-scale 1 --max-scale 4
```

### Heroku / Render / Railway
- Use the root Dockerfile (container-based deployment)
- Set env vars in the platform dashboard
- Attach a custom domain + SSL

### AWS / GCP / Azure
- Deploy as container on ECS/Cloud Run/ACI
- Put behind HTTPS load balancer with WAF + CDN

---

## 🧩 API Reference

All JSON, all `POST` (except where noted):

| Endpoint | Purpose |
|---|---|
| **POST** `/api/content/generate` | Create content. `{platform, topic, tone, keywords, audience, cta}` |
| **POST** `/api/content/hashtags` | Hashtag strategy. `{content, topic, platform, location, count}` |
| **POST** `/api/content/viral-score` | Viral score + projected metrics + improvements. `{content, platform, hashtags, topic}` |
| **POST/GET** `/api/content/calendar` | AI schedule. `{days, platforms}` or query params |
| **POST** `/api/content/competitor` | Competitive benchmarks. `{competitors[], platforms, niche, days}` |
| **GET/POST** `/api/analysis/trends` | Trending topics. niche + platforms |
| **POST** `/api/analysis/sentiment` | `{texts[], detail_level, include_emotions, include_topics}` |
| **GET/POST** `/api/analysis/analytics` | Dashboard data. platforms + days + forecast |
| **GET** `/api/analysis/health` | Health check + available agents |
| **POST** `/api/chat/message` | Intent-routed assistant. `{messages[]}` or `{message}` |
| **GET** `/api/health` | Top-level service health |

---

## 🧪 Verification Checklist

```
☐ Homepage loads with hero + KPI cards + all 8 sections
☐ Dark/light toggle works, persists on reload
☐ "Generate Content" produces platform-specific copy (LinkedIn / X / IG / FB / Blog)
☐ "Generate Hashtags" returns mixed tags with realistic volumes
☐ "Run Full Analysis" animates viral score ring + factor breakdown
☐ Trends / Calendar / Competitor sections populate with sample data
☐ Sentiment gauge renders + emotion + topic charts populate
☐ All 10 Chart.js canvases render, update on theme switch
☐ AI chat accepts quick asks, shows typing indicator, returns agent-routed responses
☐ /api/health reports 6 agents + supported platforms
☐ Docker build succeeds: docker-compose up --build
```

---

## 🔒 Security Notes

- ✅ **Never commit `.env`** (already gitignored by convention)
- ✅ IBM API key used server-side only (never exposed to frontend)
- ✅ CORS restricted to configured origins
- ✅ All watsonx.ai calls authenticated via IAM tokens (managed by SDK)
- 🔒 For production: add HTTPS, API auth (JWT), rate limiting, WAF
- 🔒 Add CSRF + session management for multi-user functionality

---

## 🛣️ Roadmap & Extensions

- **Authentic integrations**: Twitter/X v2 API, Meta Graph API, LinkedIn Pages
- **Post scheduler**: Queue + cron publishing across platforms
- **A/B testing engine**: Auto-rotate caption variants, pick winners by ER
- **Multi-user + teams**: Workspaces, roles, approvals workflows
- **CRM / CDP connectors**: Segment audience signals into content briefs
- **Advanced reports**: Exportable PDF + CSV analytics exports
- **LLM caching**: Semantic cache of frequent prompts → lower latency + cost

---

## 📝 License

Commercial-friendly MIT-style — use freely for internal teams, customer projects, or as the base of your own SaaS product.

---

## 🙏 Acknowledgments

- **IBM Granite models** + **watsonx.ai** platform for world-class enterprise-grade inference
- **Tailwind CSS** (CDN) and **Chart.js** for the zero-build-step premium UI layer
- **Flask** for the lightweight, modular Python foundation

---

**Ready to launch?** Drop your credentials into `.env`, then:
```
cd backend
pip install -r ../requirements.txt
python app.py
```

Then open **http://localhost:5000** and start scaling your social media presence with AI agents 🚀
