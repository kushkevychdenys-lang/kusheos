# ⚡ QUICK START - Rychlý start pro testování

Chces vyzkoušet aplikaci za 5 minut? Tady máš jak!

## 🚀 Varianta 1: Python (bez Dockeru) - 5 minut

### Krok 1: Instalace závislostí

```bash
cd kusheos/
pip install -r requirements.txt
```

**Výstup:**
```
Successfully installed Flask-3.0.0 requests-2.31.0 Werkzeug-3.0.1
```

### Krok 2: Spuštění bez AI (demo mode)

```bash
# NEPOUŽÍVEJ AI - jen demo chat
python app.py
```

**Výstup:**
```
🚀 Spouštění na 0.0.0.0:8081
📚 OPENAI_BASE_URL: None
📊 OPENAI_MODEL: gemma3:27b
```

### Krok 3: Otevři v prohlížeči

```
http://localhost:8081/
```

**Co vidíš:**
- 💬 Chat vlevo - zkus napsat zprávu!
- 🤖 AI vpravo - nebude fungovat (bez API klíče)

**Test (bez AI):**
1. Napiš jméno (např. "Petr")
2. Napíšu zprávu: "Ahoj!"
3. Tlačítko "Odeslat"
4. Zpráva se objeví vlevo

### Krok 4: Zastavení

```bash
Ctrl+C (v terminálu)
```

---

## 🐳 Varianta 2: Docker - 10 minut

### Krok 1: Build image

```bash
cd kusheos/
docker build -t kushaeos:demo .
```

**Výstup:**
```
Step 1/7 : FROM python:3.11-slim
...
Successfully tagged kushaeos:demo
```

### Krok 2: Run kontejner

```bash
docker run -d --name kushaeos-test -p 8081:8081 kushaeos:demo
```

**Výstup:**
```
abcd1234e5678...
```

### Krok 3: Otevři browser

```
http://localhost:8081/
```

### Krok 4: Zobrazit logy

```bash
docker logs -f kushaeos-test
```

**Výstup:**
```
🚀 Spouštění na 0.0.0.0:8081
```

### Krok 5: Zastavení

```bash
docker stop kushaeos-test
docker rm kushaeos-test
```

---

## 🤖 Varianta 3: S AI serverem (localhost)

### Krok 0: Existuje AI server na localhost:8000?

**Test:**
```bash
curl http://localhost:8000/v1/models
```

Pokud jde, pokračuj dál.

### Krok 1: Spuštění s AI

```bash
export OPENAI_API_KEY="test-key-12345"
export OPENAI_BASE_URL="http://localhost:8000"
export OPENAI_MODEL="gemma3:27b"

python app.py
```

### Krok 2: Test AI endpoint

```bash
curl -X POST http://localhost:8081/ai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Ahoj! Jak se jmenuje hlavní město Česka?",
    "document": "skolni_rad.txt"
  }'
```

**Výstup:**
```json
{
  "status": "ok",
  "response": "Hlavní město Česka se jmenuje Praha...",
  "document_used": "skolni_rad.txt"
}
```

### Krok 3: V prohlížeči

1. Otevři: `http://localhost:8081/`
2. Vyber dokument: "skolni_rad.txt"
3. Napíš otázku: "Jaké jsou předpoklady pro test?"
4. Tlačítko "Poslat"
5. ⏳ Čekej na odpověď (5-30 sekund)

---

## 📋 API CURL Testy

Všechny endpointy bez UI (pro testování):

### Health check

```bash
curl http://localhost:8081/ping
# Output: {"status":"pong"}

curl http://localhost:8081/status
# Output: {"status":"ok","application":"..."}
```

### Chat

```bash
# Přidej zprávu
curl -X POST http://localhost:8081/chat/send \
  -H "Content-Type: application/json" \
  -d '{"user":"Test","message":"Hello!"}'

# Zobraz zprávy
curl http://localhost:8081/chat
# Output: {"messages":[...],"count":1}
```

### Dokumenty

```bash
# Seznam
curl http://localhost:8081/docs
# Output: {"documents":["skolni_rad.txt","it_bezpecnost.txt"],"count":2}

# Obsah
curl http://localhost:8081/docs/get?name=skolni_rad.txt
# Output: {"filename":"skolni_rad.txt","content":"ŠKOLNÍ ŘÁD..."}
```

### AI

```bash
# Bez dokumentu
curl -X POST http://localhost:8081/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Kolik je 2+2?"}'

# S dokumentem
curl -X POST http://localhost:8081/ai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt":"Jaké jsou požadavky na hesla?",
    "document":"it_bezpecnost.txt"
  }'
```

---

## 🐛 Debugging

### Terminal výstup

```bash
# Vidíš toto?
🚀 Spouštění na 0.0.0.0:8081
📚 OPENAI_BASE_URL: None
📊 OPENAI_MODEL: gemma3:27b

# ✅ OK - aplikace běží!
```

### Browser console (F12)

```javascript
// Pokud vracím error
console.error('Chyba: ...')

// Check network tab
Network > fetch /chat > Response
```

### Docker logy

```bash
docker logs kushaeos-test
docker logs -f kushaeos-test  # Follow mode

# Hledej:
# ✅ "Spouštění na 0.0.0.0:8081"
# ❌ "Address already in use" - port obsazený
# ❌ "No module named 'flask'" - chybí dependencies
```

---

## 🎯 Kontrolní seznam

- [ ] Python 3.11+ (test: `python --version`)
- [ ] pip instalován (test: `pip --version`)
- [ ] Git repo klonován (`git clone ...`)
- [ ] Jsi v složce `kusheos/`
- [ ] Spustíš Python nebo Docker
- [ ] Otevřeš `http://localhost:8081/`
- [ ] Vidíš header "Školní interní portál"
- [ ] Zpráva se pošle v chatu
- [ ] (volitelně) AI odpovídá

---

## ⚡ Zřícený Start (bare minimum)

```bash
# Kompletní one-liner pro zapnutí
cd kusheos && pip install -r requirements.txt && python app.py

# V jiném terminálu
# http://localhost:8081/
```

---

## 🆘 SOS

| Problém | Řešení |
|---------|--------|
| "Port 8081 is already in use" | `PORT=8082 python app.py` |
| "No module named 'flask'" | `pip install -r requirements.txt` |
| "Connection refused" | Je aplikace spuštěna? Kontroluj terminal |
| "Cannot find 404" | Zkontroluj URL v prohlížeči |
| "AI říká error" | Kontroluj `OPENAI_BASE_URL` env var |

---

## 📊 Screenshots Flow

```
1. Terminal:     2. Browser:           3. Input:
   python app.py    http://localhost:8081  Chat message
   ✅ Running          ✅ UI loaded          "Ahoj!"
   
4. Chat:         5. Response:          6. Success:
   Zpráva se     DB updated         ✅ Message visible
   přidala        in memory
```

---

## 🚀 Dál?

Másh aplikaci spuštěnou? Skvělé! Teď si přečti:
- **README.md** - Features + API docs
- **PROJECT_STRUCTURE.md** - Jak to funguje
- **DEPLOYMENT.md** - Jak to nasadit

---

**Hotovo! 🎉**  
**Spo naš aplikaci za pár minut bez jakéhokoliv nasazování.**
