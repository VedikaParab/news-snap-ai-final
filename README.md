# ⚡ NewsSnap AI

> Paste a news URL. Get instant editorial intelligence.

NewsSnap AI is a full-featured AI-powered news analysis app. Paste any article URL and get a structured editorial breakdown — summary, key points, timeline, named entities, background context cards, sentiment, and more. Supports 12 languages and exports shareable PNG cards and full text reports.

---

## ✨ Features

- 🔗 **Paste any news URL** — works with most major news outlets
- 📰 **Auto article extraction** — via Newspaper3k with BeautifulSoup fallback
- 🧠 **AI editorial analysis** — summary, 5 key points, reading complexity, sentiment, category
- 🗓 **Chronological timeline** — extracts all dates and events from the article
- 🏷 **Named entity recognition** — persons, organisations, and places
- 📚 **Background context cards** — 3 key concepts explained before you read
- 🌐 **12 languages** — English, Hindi, Spanish, French, German, Arabic, Portuguese, Japanese, Chinese, Tamil, Telugu, Bengali
- 💬 **AI Research Chatbot** — ask follow-up questions, powered by live Tavily web search
- 🖼 **Shareable PNG cards** — visual summary card ready to post or share
- ⬇ **Export full report** — download complete editorial analysis as `.txt`
- ⚡ **Fast** — responses in seconds via Groq's LLaMA 3.1

---

## 🧠 How It Works

1. User pastes a news article URL and selects a language
2. Article content is extracted using `newspaper3k` (primary) or `BeautifulSoup` (fallback)
3. Content is sent to **Groq LLaMA 3.1** via LangChain for parallel analysis:
   - TL;DR summary + 5 key bullet points
   - Sentiment, category, reading complexity
   - Named entities (persons, orgs, places)
   - Chronological timeline of events
   - 3 background context cards
4. Results are rendered in a clean editorial UI
5. User can chat with the article via the floating **Research Chatbot** (Tavily-powered live web search)
6. One-click export as PNG share card or `.txt` report

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| LLM | Groq — LLaMA 3.1 8B Instant |
| LLM Orchestration | LangChain + LangChain-Groq |
| Article Extraction | Newspaper3k, BeautifulSoup4 |
| Web Search (Chatbot) | Tavily Search API |
| Image Generation | Pillow (PIL) |
| Environment | python-dotenv |

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/VedikaParab/news-snap-ai.git
cd news-snap-ai
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Get your keys:
- **Groq** — [console.groq.com](https://console.groq.com)
- **Tavily** — [tavily.com](https://tavily.com) (free tier available)

### 5️⃣ Run the app

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
news-snap-ai/
├── app.py              # Main Streamlit app — UI, analysis pipeline, share card generator
├── prompts.py          # LLM prompt templates and language configuration
├── requirements.txt    # Python dependencies
├── packages.txt        # System-level font packages (for Streamlit Cloud)
├── .env                # API keys (not committed)
└── README.md
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Powers all LLM analysis via LLaMA 3.1 |
| `TAVILY_API_KEY` | ⚠️ Optional | Enables the Research Chatbot web search. Chatbot is disabled without it. |

---

*Built using Groq · LLaMA 3.1 · Tavily · Streamlit*
