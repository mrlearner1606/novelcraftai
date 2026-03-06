# 📖 NovelCraft AI

> Write · Create · Publish — 100% Local Storage, AI-Powered

NovelCraft AI is a fully browser-based novel writing app. No accounts, no servers, no data leaving your device — just open the HTML file and start writing. Connect [Pollinations AI](https://pollinations.ai) to unlock powerful AI writing features.

---

## ✨ Features

### ✍️ Writing
- Rich text editor with **bold**, *italic*, and smart curly quote support
- Per-chapter word count and live stats (total words, chapters, characters)
- Auto-save to browser localStorage every 2 seconds
- Drag-and-drop chapter reordering
- Insert images directly into chapters

### 🧠 AI Studio (requires Pollinations API key)
- **Continue Story** — AI writes the next 3–4 paragraphs matching your style
- **Improve Writing** — rewrites your prose with richer imagery and stronger verbs
- **Rewrite Selection** — select any text and have AI rework it
- **Summarize Chapter** — instant chapter summary
- **10 AI Studio Tools** — plot twists, world building, dialogue scenes, climax writing, story analysis, and more
- **Custom Prompts** — write your own AI instructions
- Smart context system: small novels send full text, large novels auto-summarize older chapters to stay within limits

### 🎭 Characters
- Full character sheet: name, role, description, backstory
- AI character generation grounded in your story context

### 🎨 Cover Art
- Upload your own cover image (auto-resized to 600×900)
- AI cover generation via Pollinations image models
- Cover embedded in EPUB/PDF exports

### 📋 Notes & Synopsis
- Synopsis editor with AI-assisted generation
- World-building notes section
- AI synopsis reads your full novel and writes back-cover-quality blurbs

### 📤 Export
- **Plain Text (.txt)** — clean export of all chapters
- **EPUB** — standard format for Kindle, Kobo, Apple Books; includes cover, TOC, synopsis
- **PDF** — print-ready with cover page, table of contents, chapter formatting
- **Download as .txt backup** — save/transfer your novel data file

---

## 🌸 BYOP — Bring Your Own Pollen

NovelCraft uses [Pollinations AI](https://pollinations.ai) for all AI features. You pay for your own usage directly — no middleman, no markup.

**To connect:**
1. Click **🔗 Connect with Pollinations** on the login screen
2. You'll be redirected to `enter.pollinations.ai` to authorize
3. After approval, you're sent back automatically with your key stored locally
4. Alternatively, paste your API key manually

**Models available after connecting:**

| Category | Models |
|---|---|
| Text (Fast) | GPT-4o Mini, Claude Fast, Gemini Fast, Nova Fast, Perplexity Fast |
| Text (Smart) | GPT-4o, Gemini Search, Perplexity Reasoning, Mistral, DeepSeek |
| Text (Specialized) | MiniMax, Qwen Character, Qwen Coder, Qwen Safety, Kimi, GLM |
| Image | Flux, GPT Image |

---

## 🚀 Getting Started

1. Download `index.html`
2. Open it in any modern browser (Chrome, Firefox, Edge, Safari)
3. *(Optional)* Connect Pollinations AI for AI features
4. Click **Start Writing →** or **Skip** to write without AI
5. Create your first novel and start writing!

> **No installation. No dependencies. No internet required for writing.**

---

## 💾 Data & Storage

- All novel data is saved in your **browser's localStorage**
- Nothing is sent to any server (except AI API calls to Pollinations)
- Use **📥 Save File** to download a `.txt` backup of your novel
- Use **📂 Import .txt** to restore or transfer a novel to another device
- Storage is per browser — clearing browser data will delete your novels

---

## 🛠️ Technical Details

| Property | Detail |
|---|---|
| Stack | Pure HTML + CSS + Vanilla JS (single file) |
| Storage | Browser localStorage |
| AI Backend | [Pollinations AI](https://gen.pollinations.ai) |
| Image Gen | [Pollinations Image API](https://image.pollinations.ai) |
| EPUB Export | JSZip (via CDN) |
| PDF Export | jsPDF (via CDN) |
| Fonts | Playfair Display, Crimson Pro, JetBrains Mono (Google Fonts) |
| Auth | BYOP OAuth redirect via `enter.pollinations.ai` |

---

## 📁 File Structure

```
index.html          ← The entire app (single file)
README.md           ← This file
```

---

## ⚠️ Known Limitations

- **localStorage limit** is ~5–10MB per browser — very long novels with many embedded images may hit this. Use **Save File** often as a backup.
- AI features require an active internet connection and a valid Pollinations key.
- Clearing browser cache/data will erase all novels not backed up as files.
- Cover images stored in the novel count toward the localStorage limit.

---

## 🔐 Privacy

- Your writing **never leaves your device** unless you trigger an AI call.
- AI calls send chapter content and novel metadata to the Pollinations API.
- Your API key is stored in `localStorage` under `nc_poll_key`.
- No analytics, no tracking, no ads.

---

## 🙌 Credits

Built with [Pollinations AI](https://pollinations.ai) for AI features · [JSZip](https://stuk.github.io/jszip/) for EPUB · [jsPDF](https://github.com/parallax/jsPDF) for PDF
