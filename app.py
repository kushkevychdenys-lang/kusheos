"""
Interní portál pro školu/kancelář
- Veřejný chat
- AI asistenta s dokumenty
- Vektorové vyhledávání přes ChromaDB (RAG)
"""

import os
import time
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import chromadb

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 8081))
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "vectordb")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))

chat_messages = []  # In-memory chat storage
DOCS_FOLDER = "docs"
chroma_client = None
chroma_collection = None


def init_chroma():
    """Inicializuj ChromaDB klienta s retry logikou"""
    global chroma_client, chroma_collection
    
    for i in range(10):
        try:
            print(f"[{i+1}/10] Pokus o připojení k ChromaDB na {CHROMA_HOST}:{CHROMA_PORT}...")
            chroma_client = chromadb.HttpClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT
            )
            chroma_client.heartbeat()
            print("✓ ChromaDB připojen")
            break
        except Exception as e:
            print(f"✗ Chyba připojení k ChromaDB: {e}")
            if i < 9:
                time.sleep(2)
            else:
                print("✗ ChromaDB není dostupný - pokračuji bez RAG")
                chroma_client = None
                return
    
    if chroma_client:
        try:
            chroma_collection = chroma_client.get_or_create_collection(
                name="dokumenty",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ ChromaDB kolekce vytvořena")
            load_documents_to_chroma()
        except Exception as e:
            print(f"✗ Chyba vytvoření kolekce: {e}")


def chunk_document(text, chunk_size=1000, overlap=200):
    """Rozděluj text na chunks s překrytím pro lepší RAG"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks if chunks else [text]


def load_documents_to_chroma():
    """Načti všechny .txt dokumenty do ChromaDB s chunkingem"""
    global chroma_collection
    
    if not chroma_collection or not os.path.exists(DOCS_FOLDER):
        return
    
    try:
        files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith('.txt')]
        if not files:
            print("ℹ Žádné .txt dokumenty k indexování")
            return
        
        chunk_counter = 0
        for filename in files:
            try:
                filepath = os.path.join(DOCS_FOLDER, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = chunk_document(content, chunk_size=1000, overlap=200)
                base_id = filename.replace('.txt', '')
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{base_id}_chunk_{chunk_idx}"
                    chroma_collection.upsert(
                        documents=[chunk],
                        metadatas=[{
                            "filename": filename,
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks)
                        }],
                        ids=[chunk_id]
                    )
                    chunk_counter += 1
                
                print(f"✓ Dokument '{filename}' rozděleno na {len(chunks)} chunků a indexováno v ChromaDB")
            except Exception as e:
                print(f"✗ Chyba indexování '{filename}': {e}")
        
        print(f"✓ Celkem indexováno {chunk_counter} chunků")
    
    except Exception as e:
        print(f"✗ Chyba při načítání dokumentů: {e}")

def search_in_chroma(query, document_name=None, n_results=3):
    """Vyhledej nejrelevantnější chunks v ChromaDB pro RAG"""
    global chroma_collection
    
    if not chroma_collection:
        return None, []
    
    try:
        query_args = {
            "query_texts": [query],
            "n_results": n_results
        }

        if document_name:
            query_args["where"] = {"filename": document_name}

        try:
            results = chroma_collection.query(**query_args)
        except Exception:
            results = chroma_collection.query(
                query_texts=[query],
                n_results=n_results
            )

        if results and results.get('documents') and results['documents'][0]:
            chunks = results['documents'][0]
            metadata = results['metadatas'][0] if results.get('metadatas') else []

            if document_name and metadata:
                filtered = [
                    (chunk, meta)
                    for chunk, meta in zip(chunks, metadata)
                    if isinstance(meta, dict) and meta.get('filename') == document_name
                ]
                if not filtered:
                    return None, []
                chunks, metadata = zip(*filtered)
                chunks = list(chunks)
                metadata = list(metadata)

            context = "\n---\n".join(chunks)
            return context, metadata
        
        return None, []
    except Exception as e:
        print(f"Chyba vyhledávání v ChromaDB: {e}")
        return None, []

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

        if os.path.commonpath([base, filepath]) != base:
            return None

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        return None

    except Exception as e:
        print(f"Error reading document: {e}")
        return None


def call_openai_api(prompt, document_name=None, document_content=None, use_chroma=True):
    """Zavolej OpenAI-compatible API s RAG pipeline (ChromaDB)"""
    try:
        if not OPENAI_API_KEY or not OPENAI_BASE_URL:
            return "❌ Chyba: AI není nakonfigurován (chybí OPENAI_API_KEY nebo OPENAI_BASE_URL)"

        system_prompt = (
            "Jsi AI správce lokální sítě pro školu nebo kancelář. "
            "Odpovídej stručně, jasně a česky. "
            "Pokud je poskytnut kontext z dokumentů, pracuj hlavně s jeho obsahem."
        )

        context_text = ""
        metadata_info = {}
        
        if use_chroma:
            context_text, metadata_list = search_in_chroma(prompt, document_name=document_name)
            if context_text:
                print(f"ℹ RAG: Nalezeno {len(metadata_list)} relevantních chunků")
                if metadata_list and isinstance(metadata_list, list):
                    sources = set(m.get('filename', 'unknown') if isinstance(m, dict) else 'unknown' 
                                 for m in metadata_list)
                    metadata_info['sources'] = list(sources)
        
        if not context_text and document_content:
            context_text = document_content
            metadata_info['fallback'] = 'specific_document'
        
        if context_text:
            user_message = f"KONTEXT Z DOKUMENTŮ:\n{context_text}\n\nOTÁZKA:\n{prompt}"
        else:
            user_message = prompt

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
            f"{OPENAI_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
            verify=False
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


@app.route('/')
def index():
    """Hlavní stránka s UI"""
    return render_template('index.html')


@app.route('/ping', methods=['GET'])
def ping():
    """Health check"""
    return "pong"


def get_chroma_stats():
    """Vrť statistiky ChromaDB"""
    global chroma_collection
    
    files_count = len(get_documents())
    if not chroma_collection:
        return {
            "status": "disconnected",
            "documents": files_count,
            "indexed_chunks": 0
        }
    
    try:
        chunk_count = chroma_collection.count()
        return {
            "status": "connected",
            "documents": files_count,
            "indexed_chunks": chunk_count
        }
    except Exception:
        return {
            "status": "error",
            "documents": files_count,
            "indexed_chunks": 0
        }


@app.route('/status', methods=['GET'])
def status():
    """Vrť informace o serveru a RAG"""
    chroma_stats = get_chroma_stats()
    return jsonify({
        "status": "ok",
        "application": "RAG - Školní interní portál",
        "version": "1.0",
        "port": PORT,
        "model": OPENAI_MODEL,
        "ai_api": OPENAI_BASE_URL,
        "chroma": chroma_stats,
        "time": datetime.now().isoformat()
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

        user = user[:50]
        message = message[:500]

        msg_obj = {
            "user": user,
            "message": message,
            "time": datetime.now().isoformat()
        }

        chat_messages.append(msg_obj)

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

        document_content = None
        if document_name:
            document_content = read_document(document_name)
            if document_content is None:
                return jsonify({"error": f"Dokument '{document_name}' nenalezen"}), 404

        response = call_openai_api(
            prompt,
            document_name=document_name,
            document_content=document_content
        )

        return jsonify({
            "status": "ok",
            "response": response,
            "document_used": document_name if document_name else None,
            "time": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🚀 RAG Aplikace - Školní Interní Portál")
    print(f"{'='*60}")
    print(f"📌 Port: 0.0.0.0:{PORT}")
    print(f"🤖 AI Model: {OPENAI_MODEL}")
    print(f"🌐 API URL: {OPENAI_BASE_URL}")
    print(f"🗃️  ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}")
    print(f"{'='*60}\n")
    
    init_chroma()
    
  
    app.run(host='0.0.0.0', port=PORT, debug=False)
