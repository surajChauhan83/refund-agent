# WorkPodd AI Refund Agent

A full-stack AI customer support agent that processes or denies e-commerce refund requests using a LangGraph agent loop powered by Groq (llama-3.3-70b-versatile).

---

## Demo Scenarios

| Order | Customer | Expected Decision | Why |
|-------|----------|-------------------|-----|
| ORD001 | John Doe | ✅ APPROVED | Physical, delivered, within 30 days |
| ORD002 | Alice Smith | ❌ DENIED | Purchased 100+ days ago (expired window) |
| ORD003 | Bob Johnson | ❌ DENIED | Digital product — non-refundable |
| ORD004 | Emma Wilson | ❌ DENIED | Subscription — non-refundable |
| ORD005 | David Brown | ⚠️ MANUAL REVIEW | Order value $1,800 > $1,000 |
| ORD006 | Sophia Davis | ⚠️ MANUAL REVIEW | Product reported damaged |
| ORD007 | Michael Miller | ❌ DENIED | Already refunded |
| ORD008 | Olivia Moore | ❌ DENIED | Status: In Transit (not delivered) |
| ORD009 | James Taylor | ⚠️ MANUAL REVIEW | 4 previous refunds (limit: 3) |
| ORD010 | Ava Anderson | ✅ APPROVED | All rules satisfied |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq API — `llama-3.3-70b-versatile` |
| **Agent Orchestration** | LangGraph (StateGraph) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Pure HTML / CSS / JS (no framework) |
| **Data** | JSON flat-file CRM (15 customer profiles) |

---

## Architecture

```
User Query
    │
    ▼
FastAPI /chat endpoint
    │
    ▼
LangGraph StateGraph
    │
    ├── [1] extract_order_node   → Regex extract Order ID from natural language
    ├── [2] customer_node        → Load customer record from CRM (JSON)
    ├── [3] policy_node          → Load refund_policy.txt
    ├── [4] validation_node      → Run 9-rule policy engine, log each check
    └── [5] response_node        → Groq LLM generates empathetic customer response
    │
    ▼
ChatResponse { response, logs[] }
    │
    ├── Chat bubble (frontend)
    └── Reasoning log sidebar (real-time trace)
```

### Graph Flow

```
START → extract_order → get_customer → load_policy → validate_refund → generate_response → END
```

Each node updates the shared `RefundState` TypedDict and appends to `state["logs"]` for full transparency.

### Refund Policy Rules (enforced in `tools/validation_tool.py`)

1. Refund window: 30 days from purchase
2. Delivery status must be "Delivered"
3. Digital products — non-refundable
4. Subscription products — non-refundable
5. Damaged products → MANUAL_REVIEW
6. Orders > $1,000 → MANUAL_REVIEW (manager approval)
7. Already-refunded orders — no second refund
8. Customers with > 3 prior refunds → MANUAL_REVIEW
9. Cancelled orders — not eligible
10. Agent must never override these rules

---

## Project Structure

```
workpodd-refund-agent/
├── main.py                    # FastAPI app, /chat and /logs endpoints
├── requirements.txt
├── .env                       # GROQ_API_KEY goes here
│
├── graph/
│   ├── state.py               # RefundState TypedDict
│   ├── nodes.py               # 5 agent nodes (Groq LLM in response_node)
│   └── workflow.py            # LangGraph StateGraph definition
│
├── tools/
│   ├── customer_tool.py       # get_customer(order_id) → dict
│   ├── policy_tool.py         # load_policy() → str
│   └── validation_tool.py     # validate_refund(customer) → (decision, checks[])
│
├── models/
│   └── schemas.py             # Pydantic request/response models
│
├── services/
│   └── log_store.py           # In-memory log store for /logs endpoint
│
├── data/
│   ├── customers.json         # 15 mock CRM profiles
│   └── refund_policy.txt      # Policy document loaded into agent context
│
└── templates/
    └── index.html             # Single-page app (Chat + Dashboard tabs)
```

---

## Setup & Run

### 1. Clone / extract the project

```bash
cd workpodd-refund-agent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Groq API key

Get a free key at https://console.groq.com

```bash
# .env
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

Open http://localhost:8000

---

## API Reference

### `POST /chat`

```json
// Request
{ "query": "I want a refund for ORD001" }

// Response
{
  "response": "Hi John! Great news — your refund request for ORD001...",
  "logs": [
    "[1/5] 🔍 Extracted Order ID from query: 'ORD001'",
    "[2/5] 👤 Customer found: John Doe | Product: Wireless Headphones ($120)",
    "[3/5] 📋 Refund policy document loaded (10 rules)",
    "[4/5] ✅ Rule check: Days since purchase: 10 (limit: 30)",
    "[4/5] ⚖️  Validation result → APPROVED: Refund approved under policy.",
    "[5/5] 🤖 Groq LLM (llama-3.3-70b) generated customer response"
  ]
}
```

### `GET /logs`

Returns the reasoning logs from the most recent request (in-memory store).

---

## Frontend Features

- **Chat tab** — natural language input, typing indicator, decision badges (APPROVED / DENIED / MANUAL REVIEW), quick-hint buttons for demo
- **Live reasoning sidebar** — step-by-step agent trace appears alongside each response
- **Dashboard tab** — last decision stats, full log history, CRM grid (all 15 customers), policy rule reference

---

## Key Design Decisions

**Why LangGraph?** The sequential node graph makes the agent's reasoning transparent and debuggable. Each node does exactly one thing — extract, lookup, load, validate, respond. This maps cleanly to the tool-calling pattern the task specifies.

**Why Groq?** Ultra-low latency inference means the LLM response step feels instantaneous. `llama-3.3-70b-versatile` provides strong instruction-following for consistent policy adherence.

**Why validation before LLM?** The policy engine runs as deterministic Python code — the LLM only handles natural language *communication*, not the decision logic. This means the policy is never accidentally overridden by the model.

**Graceful LLM fallback** — if the Groq API is unavailable, `response_node` falls back to a template response so the app never crashes.

---

## Voice Pipeline (Bonus Feature)

**Technology:** Browser-native [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) — zero cost, no API key, no third-party service.

| Component | API Used | Notes |
|-----------|----------|-------|
| **Speech-to-Text (STT)** | `SpeechRecognition` | Mic → transcript, shown live as you speak |
| **Text-to-Speech (TTS)** | `SpeechSynthesis` | Agent response read aloud automatically |

### How to use it

**Mic button (quick):** Click the 🎤 mic button in the chat footer → full-screen voice overlay opens → tap the pulsing orb → speak your request → tap Send.

**Voice Mode toggle (full duplex):** Flip the toggle in the header → both input and output go through voice. Speak via the orb, agent responds in text *and* audio.

### Voice flow

```
User taps orb → SpeechRecognition.start()
    ↓ interim results shown live in overlay
    ↓ final transcript confirmed
User taps Send → query sent to /chat endpoint
    ↓ LangGraph agent processes (same pipeline)
    ↓ response text received
SpeechSynthesis.speak(response) → agent speaks aloud
    ↓ orb turns green while speaking
Done → ready for next voice input
```

### Browser support

| Browser | STT | TTS |
|---------|-----|-----|
| Chrome (desktop) | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Safari 14.1+ | ✅ | ✅ |
| Firefox | ❌ | ✅ |

> The app detects browser support automatically. If the Web Speech API is unavailable, a warning banner is shown and the mic button is disabled — text chat continues to work normally.
