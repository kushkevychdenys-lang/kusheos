"""
Interní portál pro školu/kancelář
- Veřejný chat
- AI asistenta s dokumenty
"""

import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ===== CONFIG =====
PORT = int(os.environ.get("PORT", 8081))
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")

# ===== STATE =====
chat_messages = []  # In-memory chat storage
DOCS_FOLDER = "docs"

# ===== HELPERS =====
def get_documents():
    """Vrť seznam .txt souborů z docs/ složky"""
    try:
        if not os.path.exists(DOCS_FOLDER):
            return []
        files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith('.txt')]
        return sorted(files)
    except Exception as e:
        print(f"Error reading docs folder: {e}")
        return []


def read_document(filename):
    try:
        if not filename.endswith('.txt'):
            return None

        base = os.path.abspath(DOCS_FOLDER)
        filepath = os.path.abspath(os.path.join(DOCS_FOLDER, filename))

        # zabrání čtení mimo docs/
        if not filepath.startswith(base):
            return None

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        return None

    except Exception as e:
        print(f"Error reading document: {e}")
        return None


def call_openai_api(prompt, document_content=None):
    """Zavolej OpenAI-compatible API s textem dokumentu (pokud je)"""
    try:
        if not OPENAI_API_KEY or not OPENAI_BASE_URL:
            return "❌ Chyba: AI není nakonfigurován (chybí OPENAI_API_KEY nebo OPENAI_BASE_URL)"

        # Příprava systémového promptu
        system_prompt = (
            "Jsi AI správce lokální sítě pro školu nebo kancelář. "
            "Odpovídej stručně, jasně a česky. "
            "Pokud je přiložen dokument, pracuj hlavně s jeho obsahem."
        )

        # Příprava obsahu - pokud je dokument, zahrň ho do kontextu
        if document_content:
            user_message = f"DOKUMENT:\n{document_content}\n\nOTÁZKA:\n{prompt}"
        else:
            user_message = prompt

        # Volání API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(
            f"{OPENAI_BASE_URL}/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"❌ API chyba ({response.status_code}): {response.text[:200]}"

    except requests.exceptions.ConnectionError:
        return "❌ Chyba: Nelze se připojit k AI serveru"
    except requests.exceptions.Timeout:
        return "❌ Chyba: Timeout - AI server neodpovídá"
    except Exception as e:
        return f"❌ Chyba: {str(e)[:200]}"


# ===== ROUTES =====

@app.route('/')
def index():
    """Hlavní stránka s UI"""
    return render_template('index.html')


@app.route('/ping', methods=['GET'])
def ping():
    """Health check"""
    return "pong"


@app.route('/status', methods=['GET'])
def status():
    """Vrť informace o serveru"""
    return jsonify({
        "status": "ok",
        "application": "Školní interní portál",
        "version": "1.0",
        "author": "AI správce",
        "time": datetime.now().isoformat(),
        "port": PORT
    })


@app.route('/chat', methods=['GET'])
def get_chat():
    """Vrť všechny zprávy z chatu"""
    return jsonify({
        "messages": chat_messages,
        "count": len(chat_messages)
    })


@app.route('/chat/send', methods=['POST'])
def send_chat():
    """Přidej zprávu do chatu"""
    try:
        data = request.get_json(silent=True) or {}
        user = data.get('user', 'Anonym').strip()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({"error": "Prázdná zpráva"}), 400

        # Omezení délky
        user = user[:50]
        message = message[:500]

        # Vytvoř záznam
        msg_obj = {
            "user": user,
            "message": message,
            "time": datetime.now().isoformat()
        }

        chat_messages.append(msg_obj)

        # Drž jen posledních 500 zpráv (aby se nejedlo RAM)
        if len(chat_messages) > 500:
            chat_messages.pop(0)

        return jsonify({
            "status": "ok",
            "message": msg_obj
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/docs', methods=['GET'])
def list_docs():
    """Vrť seznam dostupných .txt dokumentů"""
    files = get_documents()
    return jsonify({
        "documents": files,
        "count": len(files)
    })


@app.route('/docs/get', methods=['GET'])
def get_doc():
    """Vrť obsah konkrétního .txt dokumentu"""
    try:
        filename = request.args.get('name', '').strip()
        if not filename:
            return jsonify({"error": "Chybí parametr 'name'"}), 400

        content = read_document(filename)
        if content is None:
            return jsonify({"error": "Dokument nenalezen"}), 404

        return jsonify({
            "filename": filename,
            "content": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ai', methods=['POST'])
def ai_endpoint():
    """Hlavní AI endpoint"""
    try:
        data = request.get_json(silent=True) or {}
        prompt = data.get('prompt', '').strip()
        document_name = data.get('document', '').strip()

        if not prompt:
            return jsonify({"error": "Chybí prompt"}), 400

        # Pokud je vybraný dokument, přečti ho
        document_content = None
        if document_name:
            document_content = read_document(document_name)
            if document_content is None:
                return jsonify({"error": f"Dokument '{document_name}' nenalezen"}), 404

        # Zavolej AI
        response = call_openai_api(prompt, document_content)

        return jsonify({
            "status": "ok",
            "response": response,
            "document_used": document_name if document_name else None,
            "time": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== RUN =====
if __name__ == '__main__':
    print(f"🚀 Spouštění na 0.0.0.0:{PORT}")
    print(f"📚 OPENAI_BASE_URL: {OPENAI_BASE_URL}")
    print(f"📊 OPENAI_MODEL: {OPENAI_MODEL}")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
