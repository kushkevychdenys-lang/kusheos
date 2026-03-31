# 🏫 Školní Interní Portál

Jednoduchá webová aplikace ve Flasku pro vnitřní komunikaci škol/kanceláří s veřejným chatem a AI asistentem.

## 🚀 Vlastnosti

- **Veřejný chat** - komunikace mezi uživateli (bez registrace)
- **AI asistent** - příspěvkový AI s podporou textových dokumentů
- **Správa dokumentů** - čtení .txt souborů
- **Lehká aplikace** - minimální RAM footprint
- **Docker ready** - jeden kontejner, ready to deploy
- **OpenAI-compatible API** - integrace s libovolným AI backendem

## 📦 Struktura Projektu

```
kusheos/
├── app.py                 # Flask aplikace (backend)
├── requirements.txt       # Python závislosti
├── Dockerfile            # Docker build
├── README.md             # Tato dokumentace
├── templates/
│   └── index.html        # HTML frontend (chat + AI)
└── docs/
    ├── skolni_rad.txt    # Příklad dokumentu
    └── it_bezpecnost.txt # Příklad dokumentu
```

## 🔧 Setup & Instalace

### Lokální vývoj (bez Dockeru)

```bash
# Python 3.11+
pip install -r requirements.txt

# Spuštění
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="http://localhost:8000"
python app.py
```

Aplikace běží na: **http://localhost:8081**

### Docker Deploy

```bash
# Build image
docker build -t kushaeos:latest .

# Run kontejner (příklad)
docker run -d \
  --name kushaeos \
  -p 8081:8081 \
  -e OPENAI_API_KEY="sk-..." \
  -e OPENAI_BASE_URL="http://ai-server:8000" \
  -e OPENAI_MODEL="gemma3:27b" \
  kushaeos:latest
```

## 🌍 Environment Variables

| Proměnná | Default | Popis |
|----------|---------|-------|
| `PORT` | `8081` | Port aplikace (host: 0.0.0.0) |
| `OPENAI_BASE_URL` | - | URL AI serveru (OpenAI-compatible) |
| `OPENAI_API_KEY` | - | API klíč |
| `OPENAI_MODEL` | `gemma3:27b` | Model na serveru |

## 📡 API Endpoints

### Chat
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `GET` | `/chat` | Vrátí všechny zprávy |
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
| `GET` | `/docs` | Seznam .txt souborů |
| `GET` | `/docs/get?name=skolni_rad.txt` | Obsah souboru |

### AI
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `POST` | `/ai` | Pošli otázku AI |

```json
POST /ai
{
  "prompt": "Jaké jsou požadavky na hesla?",
  "document": "it_bezpecnost.txt"  // volitelný
}
```

### Health
| Metoda | Endpoint | Popis |
|--------|----------|-------|
| `GET` | `/ping` | Health check |
| `GET` | `/status` | Server status |

## 🤖 AI Integrace

Aplikace používá OpenAI-compatible API (LM Studio, Ollama s API, Hugging Face, atd.)

### Systémový prompt:
```
Jsi AI správce lokální sítě pro školu nebo kancelář.
Odpovídaj stručně, jasně a česky.
Pokud je přiložen dokument, pracuj hlavně s jeho obsahem.
```

### Příklad použití:
1. Uživatel vybere dokument "it_bezpecnost.txt"
2. Napíše otázku: "Jaké jsou požadavky na hesla?"
3. AI zpracuje obsah dokumentu + otázku
4. Vrátí odpověď z kontextu

## 💾 Data Storage

- **Chat**: Uloženo v paměti (Python list)
- **Dokumenty**: Čtení z `docs/` složky (read-only)
- **AI history**: Uloženo v frontendě (localStorage)

⚠️ **Pozn.**: Data se vymažou po restartu aplikace!

## 🛡️ Bezpečnost

- Bez databáze → bez SQL injection
- Bez složité aktualizace → méně zranitelností
- Kontrola vstupů (max. délky)
- Bezpečnostní kontrola cest (path traversal)
- Žádné stahování souborů

## 🎯 Omezení (záměrná)

- ❌ Žádná registrace/přihlášení
- ❌ Bez ukládání na disk
- ❌ Bez databáze
- ❌ Bez websocketů
- ❌ Bez složitých knihoven
- ❌ Bez mikroslužeb

Vše je záměrně **jednoduché** pro hosty s omezenými zdroji!

## 📊 Výkon

- **RAM**: ~150-200 MB (Python + Flask)
- **CPU**: Minimální (čeká na API)
- **Disk**: ~50 MB (bez modely)
- **Doba startu**: <5 sekund

## 🐛 Troubleshooting

### Chyba: "Nelze se připojit k AI serveru"
- Zkontroluj `OPENAI_BASE_URL`
- Zkontroluj firewall
- Zkontroluj API klíč

### Chyba: "Dokument nenalezen"
- Zkontroluj jméno souboru (case-sensitive)
- Zkontroluj že je v `docs/` složce
- Zkontroluj že je `.txt` formát

### Chat se nezobrazuje
- Obsah > 500 MB? → Smaž starší zprávy
- Zkontroluj F12 console na chyby

## 📝 Přidávání Dokumentů

Stačí přidat `.txt` soubor do `docs/` složky:

```bash
cat > docs/nova_smernice.txt << EOF
NOVÁ SMĚRNICE
==============
```

Aplikace ho automaticky najde!

## 🤝 Contributing

Projekt je určen pro studenti - kdyžchcete rozšíření:
1. Vyzkoušej lokálně
2. Otestuj Docker
3. Zkontroluj memory usage
4. Pull request! 🚀

## 📄 Licence

Vnitřní projektu. Používej dle potřeby.

---

**Vytvořeno pro školu Kuřim**  
**V1.0 - Březen 2026**
