# 🏫 Školní Interní Portál
Jednoduchá webová aplikace ve Flasku pro vnitřní komunikaci škol/kanceláří s veřejným chatem a AI asistentem.

## 🚀 Vlastnosti
- Veřejný chat - komunikace mezi uživateli (bez registrace)
- AI asistent - odpovědi s využitím dokumentů
- RAG (ChromaDB) - vektorové vyhledávání v dokumentech
  - dělení dokumentů na části (chunky)
  - vyhledání relevantních částí podle dotazu
  - použití kontextu při odpovědi AI
- Správa dokumentů - čtení `.txt` souborů z `docs/`
- Docker Compose - aplikace běží ve 2 kontejnerech
- OpenAI-compatible API - napojení na externí AI
- Responsive UI

## 📦 Struktura Projektu
kusheos/
├── app.py
├── compose.yml
├── requirements.txt
├── Dockerfile
├── README.md
├── .env.example
├── templates/
│   └── index.html
└── docs/
    ├── skolni_rad.txt
    └── it_bezpecnost.txt

## 🔧 Setup & Spuštění
Docker Compose:

docker compose up --build

Aplikace poběží na:
http://localhost:8081

## 🏗️ Architektura
Aplikace běží na 2 kontejnerech:

- app → Flask aplikace
- vectordb → ChromaDB

Komunikace:
- app → vectordb (port 8000)
- app → externí AI API

## 🌍 Environment Variables
- PORT
- OPENAI_BASE_URL
- OPENAI_API_KEY
- OPENAI_MODEL
- CHROMA_HOST
- CHROMA_PORT

## 📡 API Endpoints
Chat:
- GET /chat
- POST /chat/send

Dokumenty:
- GET /docs
- GET /docs/get?name=...

AI:
- POST /ai

Health:
- GET /ping
- GET /status

## 🤖 RAG princip
1. načtení `.txt` souborů
2. rozdělení na části
3. uložení do ChromaDB
4. vyhledání relevantních částí
5. poslání kontextu do AI
6. odpověď

## 💾 Data
- chat je uložen jen v paměti
- po restartu se smaže
- dokumenty jsou ve složce docs/
- ChromaDB slouží jen pro běh aplikace

## 🛡️ Bezpečnost
- žádná autentifikace
- omezení délky vstupů
- bezpečné čtení souborů

## 🐛 Troubleshooting
AI nefunguje:
- zkontroluj OPENAI_API_KEY
- zkontroluj OPENAI_BASE_URL

Dokument nenalezen:
- musí být v docs/
- musí končit .txt

Aplikace neběží:
docker compose logs

## 📝 Přidání dokumentů
Stačí přidat .txt soubor do složky docs/.

## 📄 Licence
Projekt pro vzdělávací účely.