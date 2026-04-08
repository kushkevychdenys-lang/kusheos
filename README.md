# 🏫 Školní Interní Portál
Jednoduchá webová aplikace ve Flasku pro vnitřní komunikaci škol/kanceláří s veřejným chatem a AI asistentem.

## 🚀 Vlastnosti
- **Veřejný chat** - komunikace mezi uživateli (bez registrace)
- **AI asistent** - příspěvkový AI s podporou textových dokumentů
- **Správa dokumentů** - čtení .txt souborů z `docs/` složky
- **Lehká aplikace** - minimální RAM footprint (~150-200 MB)
- **Docker ready** - jeden kontejner s gunicorn
- **OpenAI-compatible API** - integrace s libovolným AI backendem (Ollama, LM Studio, Hugging Face, atd.)
- **Automatická aktualizace chatu** - real-time polling každé 2 sekundy
- **Responsive design** - funguje na počítači i mobilu

## 📦 Struktura Projektu
```
kusheos/
├── app.py                 # Flask aplikace (backend)
├── requirements.txt       # Python závislosti
├── Dockerfile            # Docker build s gunicorn
├── docker-compose.yml    # Vývojové prostředí s Ollama (volitelné)
├── README.md             # Tato dokumentace
├── templates/
│   └── index.html        # HTML frontend (chat + AI)
└── docs/
    ├── README.md         # Návod na správu dokumentů
    ├── skolni_rad.txt    # Příklad školního řádu
    └── it_bezpecnost.txt  # Příklad IT bezpečnostních pravidel
```

## 🔧 Setup & Instalace

### Lokální vývoj (bez Dockeru)

```bash
# Python 3.11+
pip install -r requirements.txt

# Spuštění
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://kurim.ithope.eu"
python app.py
```

Aplikace běží na: **http://localhost:8081**

### Docker Deploy (produkce)

```bash
# Build image
docker build -t kushaeos:latest .

# Run kontejner
docker run -d \
  --name kushaeos \
  -p 8081:8081 \
  -e OPENAI_API_KEY="sk-..." \
  -e OPENAI_BASE_URL="https://kurim.ithope.eu" \
  -e OPENAI_MODEL="gemma3:27b" \
  kushaeos:latest
```

### Vývoj s docker-compose (s lokálním AI)

```bash
# Spuštění s Ollama (volitelné)
docker-compose up

# Nebo na pozadí
docker-compose up -d

# Zastavení
docker-compose down

# Logy
docker-compose logs -f app
```

## 🌍 Environment Variables

| Proměnná | Default | Popis |
|----------|---------|-------|
| `PORT` | `8081` | Port aplikace (host: 0.0.0.0) |
| `OPENAI_BASE_URL` | `https://kurim.ithope.eu` | URL AI serveru (OpenAI-compatible) |
| `OPENAI_API_KEY` | - | API klíč |
| `OPENAI_MODEL` | `gemma3:27b` | Model na serveru |

## 📡 API Endpoints

### Chat
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `GET` | `/chat` | Vrátí všechny zprávy (max 500) |
| `POST` | `/chat/send` | Pošli novou zprávu |

```json
POST /chat/send
{
  "user": "Jméno",
  "message": "Text zprávy"
}
```

### Dokumenty
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `GET` | `/docs` | Seznam všech .txt souborů v `docs/` |
| `GET` | `/docs/get?name=skolni_rad.txt` | Obsah konkrétního dokumentu |

### AI
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `POST` | `/ai` | Pošli otázku AI (volitelně s dokumentem) |

```json
POST /ai
{
  "prompt": "Jaké jsou požadavky na hesla?",
  "document": "it_bezpecnost.txt"  // volitelné
}
```

### Health & Status
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `GET` | `/ping` | Health check (vrátí "pong") |
| `GET` | `/status` | Server status s metadaty |

## 🤖 AI Integrace

Aplikace používá OpenAI-compatible API pro připojení k různým AI backendům:

### Systémový prompt:
```
Jsi AI správce lokální sítě pro školu nebo kancelář.
Odpovídaj stručně, jasně a česky.
Pokud je přiložen dokument, pracuj hlavně s jeho obsahem.
```

### Příklady použití:
1. **Bez dokumentu:** "Kolik je 2+2?"
2. **S dokumentem:** Vyber `it_bezpecnost.txt` → "Jaké jsou požadavky na hesla?"
3. AI zpracuje obsah dokumentu + otázku → vrátí odpověď z kontextu

### Kompatibilní AI servery:
- **Ollama** (lokální): `http://localhost:11434`
- **LM Studio**: `http://localhost:8000`
- **Hugging Face**: `https://api-inference.huggingface.co`
- **Kurim IT Hope**: `https://kurim.ithope.eu`

## 💾 Data Storage

- **Chat zprávy**: Uloženy v paměti Pythonu (max 500 zpráv)
- **AI historie**: Uložena v localStorage prohlížeče
- **Dokumenty**: Čtení z `docs/` složky (read-only)
- **Žádná databáze** - vše v paměti nebo souborech

⚠️ **Poznámka**: Data se smažou po restartu aplikace!

## 🛡️ Bezpečnost

- **Žádná registrace/autentifikace** - veřejný přístup
- **Žádná databáze** → bez SQL injection
- **Žádné souborové uploady** → bez malware rizika
- **Kontrola vstupů**: Max. délky (uživatel: 50, zpráva: 500 znaků)
- **Path traversal prevence**: Bezpečné čtení souborů
- **HTTPS doporučeno** pro produkci
- **Firewall**: Otevřen jen port 8081

## 🎯 Omezení (záměrná jednoduchost)

- ❌ Žádná registrace/přihlášení
- ❌ Žádné ukládání na disk
- ❌ Žádná databáze
- ❌ Žádné websocketů (pouze polling)
- ❌ Žádné složité knihoven
- ❌ Žádné mikroslužeb

Vše je záměrně **jednoduché** pro hosty s omezenými zdroji!

## 📊 Výkon

- **RAM**: ~150-200 MB (Python + Flask + Gunicorn)
- **CPU**: Minimální (čeká na API volání)
- **Disk**: ~50 MB (bez AI modelů)
- **Doba startu**: <5 sekund
- **Concurrent users**: Omezeno pamětí (každý uživatel ~1-2 MB)

## 🐛 Troubleshooting

### Chyba: "Nelze se připojit k AI serveru"
- Zkontroluj `OPENAI_BASE_URL` (má být dostupný z kontejneru)
- Zkontroluj `OPENAI_API_KEY`
- Zkontroluj firewall/port forwarding
- Test: `curl -X POST $OPENAI_BASE_URL/v1/chat/completions -H "Authorization: Bearer $OPENAI_API_KEY" -d '{"model":"test","messages":[{"role":"user","content":"test"}]}'`

### Chyba: "Dokument nenalezen"
- Zkontroluj název souboru (case-sensitive, musí končit `.txt`)
- Zkontroluj že soubor je v `docs/` složce
- Zkontroluj práva čtení
- Test: `curl http://localhost:8081/docs`

### Chat se nezobrazuje
- Zkontroluj konzoli prohlížeče (F12)
- Zkontroluj že aplikace běží: `curl http://localhost:8081/ping`
- Pokud >500 zpráv: Starší se automaticky mažou

### Docker kontejner neodpovídá
- Zkontroluj port mapping: `docker ps`
- Zkontroluj logy: `docker logs kushaeos`
- Zkontroluj že kontejner běží: `docker stats`

## 📝 Přidávání Dokumentů

Stačí přidat `.txt` soubor do `docs/` složky:

```bash
# Příklad
cat > docs/nova_smernice.txt << EOF
NOVÁ SMĚRNICE
==============

Toto je nový dokument pro AI.
EOF
```

Aplikace ho automaticky najde při příštím načtení seznamu dokumentů.

Podrobný návod: viz `docs/README.md`

## 🤝 Contributing

Projekt je určen pro školy a studenty - vítány příspěvky!

### Jak přispět:
1. Vyzkoušej lokálně (`python app.py`)
2. Otestuj Docker (`docker build . && docker run ...`)
3. Zkontroluj memory usage (< 300 MB)
4. Pull request! 🚀

### Doporučené vylepšení:
- Přidat další dokumenty do `docs/`
- Vylepšit UI/UX
- Přidat další API endpointy
- Optimalizovat výkon

## 📄 Licence

Tento projekt je open-source pro vzdělávací účely.

Vytvořeno pro Škola Kuřim
Březen 2026