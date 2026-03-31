# 📚 STRUKTURA PROJEKTU - DETAILNÍ VYSVĚTLENÍ

## 📂 Přehled složek

```
kusheos/
├── app.py                 # 🔴 HLAVNÍ BACKEND (Flask aplikace)
├── requirements.txt       # 🔴 PYTHON BALÍČKY
├── Dockerfile            # 🔴 DOCKER BUILD
├── README.md             # 📘 Základní dokumentace
├── DEPLOYMENT.md         # 📘 Nasazení na server
├── PROJECT_STRUCTURE.md  # 📘 Toto vysvětlení
├── .gitignore           # 🔧 Git ignore
├── templates/
│   └── index.html        # 🟡 HTML FRONTEND (Chat + AI UI)
└── docs/
    ├── skolni_rad.txt    # 📄 Ukázkový dokument 1
    └── it_bezpecnost.txt # 📄 Ukázkový dokument 2
```

## 🔴 KRITICKÉ SOUBORY (bez těchto nefunguje nic)

### `app.py` - Backend aplikace (500+ řádků)

**Co to je:**
Hlavní Flask aplikace s API endpointy a obchodní logikou.

**Co dělá:**
1. **Chat management**
   - GET `/chat` - vrátí všechny zprávy
   - POST `/chat/send` - přidá zprávu
   - Ukládání v paměti (Python list)

2. **Dokumenty**
   - GET `/docs` - seznam .txt souborů
   - GET `/docs/get?name=...` - obsah souboru
   - Čtení z `docs/` složky

3. **AI integrace**
   - POST `/ai` - hlavní AI endpoint
   - Volá OpenAI-compatible API
   - Pracuje s dokumenty

4. **Health check**
   - GET `/ping` - "pong"
   - GET `/status` - server info

**Klíčové funkce:**
- `get_documents()` - najde .txt v docs/
- `read_document(filename)` - bezpečně přečte soubor
- `call_openai_api(prompt, doc)` - volá AI server
- Flask routes (@app.route)

**Bezpečnostní prvky:**
- Validace vstupů (max. délky)
- Kontrola cest (path traversal)
- Jen .txt soubory
- Limit zpráv (500)

**Environment variables:**
```python
PORT = int(os.environ.get("PORT", 8081))
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")
```

---

### `requirements.txt` - Python balíčky

```
Flask==3.0.0          # Web framework
requests==2.31.0      # HTTP klient pro API
Werkzeug==3.0.1       # WSGI utilit
```

**Proč právě tyhle?**
- **Flask** - nejjednoduší Python framework
- **requests** - jednoduché API volání
- **Werkzeug** - Flask dependency (je tam automaticky)

⚠️ **DŮLEŽITÉ:** Bez websocketů, bez databází, bez ORM!

---

### `Dockerfile` - Docker kontejner

```dockerfile
FROM python:3.11-slim    # Malá image (150MB)
WORKDIR /app
COPY requirements.txt .
COPY app.py .
COPY templates/ templates/
COPY docs/ docs/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8081
CMD ["python", "app.py"]
```

**Proč 3.11-slim?**
- 3.11 = nová verze (fast)
- slim = bez zbytečných balíčků (~150MB vs 900MB)

**Co se kopíruje:**
- `requirements.txt` - závislosti
- `app.py` - backend
- `templates/` - HTML/CSS
- `docs/` - dokumenty

**Port:**
- 8081 (ale lze měnit přes `PORT` env var)

**Start:**
- `python app.py` (spuští Flask na 0.0.0.0:8081)

---

## 🟡 FRONTEND (HTML/JavaScript)

### `templates/index.html` - Webové UI (800+ řádků)

**Struktura:**
```html
<!DOCTYPE html>
<html>
  <head>
    <!-- Meta, CSS -->
  </head>
  <body>
    <div class="container">
      <header><!-- Logo + status --></header>
      <div class="main-content">
        <div class="chat-panel"><!-- Chat --></div>
        <div class="ai-panel"><!-- AI assistant --></div>
      </div>
    </div>
    <script>
      <!-- Interaktivita -->
    </script>
  </body>
</html>
```

**CSS (Flexbox layout):**
- `container` - hlavní flex kontejner
- `chat-panel` / `ai-panel` - vedle sebe (flex)
- Responsive - na mobilu pod sebou
- Gradientní pozadí (fialová)
- Smooth animace

**JavaScript funkce:**
- `loadDocuments()` - GET /docs, naplní select
- `sendChatMessage()` - POST /chat/send
- `sendAIPrompt()` - POST /ai
- `loadChatMessages()` - GET /chat (polling 2s)
- Auto-scroll na nové zprávy
- localStorage pro jméno uživatele

**Polling architektura:**
```
Frontend              Backend
  |                    |
  |---GET /chat------->| 
  |<----messages-------|
  | (každé 2 sec)
  |
  |---POST /chat/send->|
  |<--ok---------------|
```

**Bez WebSocketů:**
- Jednodušší implementace
- Méně připojení
- Stále real-time (2s delay)

---

## 📄 DOKUMENTY - `docs/` složka

Ukázkové .txt soubory:

### `skolni_rad.txt`
- Školní řád s kapitolami
- Docházka, chování, zkoušky
- Příklad co AI může číst

### `it_bezpecnost.txt`
- IT bezpečnostní pravidla
- Hesla, přístup, emaily
- Realistický obsah

**Jak přidat více:**
```bash
# Vytvořit nový soubor
echo "NOVÁ SMĚRNICE" > docs/nova_smernice.txt

# Automaticky se objeví v `/docs` listu
```

⚠️ **Jen .txt!** (bezpečnostní důvod)

---

## 📊 FLOW DIAGRAM - Jak to funguje

```
┌─────────────────────────────────────────────────────────────┐
│                     WEBOVÝ PROHLÍŽEČ                         │
│  [Chat panel]         |          [AI panel]                  │
│  - Jméno              |          - Výběr doc                 │
│  - Zpráva             |          - Otázka                    │
│  - Tlačítko Odeslat   |          - Odpověď AI               │
└──────────┬────────────┼──────────┬──────────────────────────┘
           │            │          │
    POST /chat/send  GET /chat  POST /ai
           │ GET /docs │          │
     ──────┴──────────┴──────────┘
              │
              ▼
      ┌──────────────────┐
      │   app.py(Flask)  │
      │  Backend Server  │
      ├──────────────────┤
      │ State:           │
      │ - chat_messages  │
      │ - DOCS_FOLDER    │
      └──────┬───────────┘
             │
      ┌──────┴─────────────────────┐
      │                            │
      ▼ (read)            ▼ (HTTP POST)
   docs/          OPENAI_BASE_URL:8000
   .txt files     (AI Server)
                  \v1/chat/completions
```

---

## 🔄 REQUEST-RESPONSE PŘÍKLADY

### 1️⃣ Chat zpráva

**Request (POST /chat/send):**
```json
{
  "user": "Honza",
  "message": "Ahoj! Jak se máš?"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": {
    "user": "Honza",
    "message": "Ahoj! Jak se máš?",
    "time": "2026-03-31T14:32:00.123456"
  }
}
```

**Bu v app.py:**
```python
@app.route('/chat/send', methods=['POST'])
def send_chat():
    data = request.json
    msg_obj = {
        "user": data.get('user'),
        "message": data.get('message'),
        "time": datetime.now().isoformat()
    }
    chat_messages.append(msg_obj)
    return jsonify({"status": "ok", "message": msg_obj})
```

---

### 2️⃣ AI dotaz s dokumentem

**Request (POST /ai):**
```json
{
  "prompt": "Jaké jsou požadavky na hesla?",
  "document": "it_bezpecnost.txt"
}
```

**V app.py:**
```python
@app.route('/ai', methods=['POST'])
def ai_endpoint():
    prompt = request.json.get('prompt')
    doc_name = request.json.get('document')
    doc_content = read_document(doc_name)  # Přečte soubor
    response = call_openai_api(prompt, doc_content)  # API call
    return jsonify({"response": response})
```

**HTTP Call na AI server:**
```
POST http://OPENAI_BASE_URL/v1/chat/completions
Headers:
  Authorization: Bearer sk-...
  Content-Type: application/json

Body:
{
  "model": "gemma3:27b",
  "messages": [
    {
      "role": "system",
      "content": "Jsi AI správce..."
    },
    {
      "role": "user",
      "content": "DOKUMENT:\n...it_bezpecnost.txt obsah...\n\nOTÁZKA:\nJaké jsou..."
    }
  ]
}
```

**Response:**
```json
{
  "response": "Hesla musí mít min. 8 znaků..."
}
```

---

## 🚀 SPUŠTĚNÍ - Step by Step

### 1. Lokálně bez Dockeru

```bash
# Python 3.11+ instalován?
python --version

# Závislosti
pip install -r requirements.txt

# Environment
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="http://localhost:8000"

# Spuštění
python app.py
# Output: 🚀 Spouštění na 0.0.0.0:8081

# V prohlížeči
# http://localhost:8081/
```

### 2. Docker lokálně

```bash
# Build
docker build -t kushaeos .

# Run
docker run -d -p 8081:8081 \
  -e OPENAI_API_KEY="sk-..." \
  -e OPENAI_BASE_URL="http://host.docker.internal:8000" \
  kushaeos

# Test
curl http://localhost:8081/ping
```

### 3. Na serveru

Viz `DEPLOYMENT.md`

---

## 💾 DATA STORAGE

**V paměti (dočasné):**
```python
chat_messages = []  # List zpráv (0-500)
```

**Na disku (permanentní):**
```
docs/
  skolni_rad.txt
  it_bezpecnost.txt
  ... (jakýkoli .txt)
```

**V prohlížeči (offline):**
```javascript
localStorage.getItem('userName')  // Jméno uživatele
aiMessages = []  // AI konverzace (jen session)
```

⚠️ **Po restartu app.py = smazané chat zprávy!**

---

## 🎯 OMEZENÍ (z důvodu simplicity)

| Něco | Proč NE | Místo |
|-----|---------|-------|
| Databáze | Komplikace | In-memory list |
| Registrace | Zbytečné | Jen jméno input |
| WebSocket | Komplex | HTTP polling |
| CSS framework | Váha | Custom flexbox CSS |
| TypeScript | Overkill | Vanilla JS |
| Caching | RAM limit | Přímé volání API |

---

## 🔧 TROUBLESHOOTING

| Problém | Řešení |
|---------|--------|
| Port 8081 obsazený | `PORT=8082 python app.py` |
| Import Flask error | `pip install -r requirements.txt` |
| AI neodpovídá | Zkontroluj `OPENAI_BASE_URL` |
| Chat je prázdný | Je po spuštění - normální |
| Dokument nenalezen | Jméno case-sensitive, jen .txt |
| Kontejner nespustí | `docker logs kushaeos` |

---

## 📈 ROZŠÍŘENÍ V BUDOUCNOSTI

**Jednoduché (bez zmíny architektury):**
- ✅ Přidání více dokumentů
- ✅ Jiný model AI
- ✅ Jiný port
- ✅ Lepší CSS design

**Složitější:**
- ❓ Databází (psql/mongodb)
- ❓ WebSocket (real-time chat)
- ❓ Registrace/přihlášení
- ❓ File upload

---

**Vytvořeno: Březen 2026**  
**Verze: 1.0**  
**Status: Stabilní ✅**
