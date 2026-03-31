# 📄 DOKUMENTY - Jak přidávat a spravovat

Klíčové soubory, které AI může čít v prohlíži.

## 📂 Složka `docs/`

Všechny .txt soubory v `docs/` se automaticky načítají aplikací.

```
docs/
├── skolni_rad.txt
├── it_bezpecnost.txt
├── metodika_komunikace.txt
├── knihovna_katalog.txt
└── ... (jakýkoli .txt)
```

## ➕ Přidání nového dokumentu

### Postup:

1. **Vytvoř nový .txt soubor** v `docs/` složce
   ```bash
   # Linux/Mac
   echo "OBSAH" > docs/nový_dokument.txt
   
   # Windows PowerShell
   "OBSAH" | Out-File -Encoding utf8 docs/nový_dokument.txt
   ```

2. **Formátování (doporučené):**
   ```
   NÁZEV DOKUMENTU
   ===============
   
   SEKCE 1
   -------
   Text obsahu
   
   SEKCE 2
   -------
   Více textu
   ```

3. **Zkontroluj seznam:**
   ```bash
   curl http://localhost:8081/docs
   ```
   Output:
   ```json
   {
     "documents": ["skolni_rad.txt", "it_bezpecnost.txt", "nový_dokument.txt"],
     "count": 3
   }
   ```

4. **Vyzkoušej v AI:**
   - V prohlížeči otevři aplikaci
   - Vyber: "nový_dokument.txt"
   - Napíš otázku
   - AI by měl mít obsah!

## 📝 Příklady obsahu

### Školní dokumenty

#### školní_řád.txt
```
ŠKOLNÍ ŘÁD
==========

KAPTIOLA 1: OBECNÉ PRINCIPY
-----------------------------
Obsah...

KAPITOLA 2: DOCHÁZKA
---------------------
Obsah...
```

#### Informace pro třídu
```
INFORMACE PRO 3.A
=================

SCHŮZKY
-------
Čtvrtek 15:00 v místnosti 205

PROJEKTY
--------
Projekt matematika: Deadline 30.3.

KONTAKTY
--------
Třídní učitel: mgr. Novotný
```

#### Interní postupy IT
```
IT PROCEDURAND
===============

NOVÝ POČÍTAČ
- Instalace Windows
- Instalace balíků
- Konfigurace

HESLA
-----
Minimálně 12 znaků...
```

## 🔍 Obsah Dokumentu

Zkontroluj obsah:
```bash
curl http://localhost:8081/docs/get?name=skolni_rad.txt
```

Output:
```json
{
  "filename": "skolni_rad.txt",
  "content": "ŠKOLNÍ ŘÁD\n========...",
}
```

## ✏️ Editace dokumentu

1. Otevři soubor v editoru
2. Uprav obsah
3. Ulož soubor
4. Aplikace automaticky načte nový obsah

```bash
# V terminálu
nano docs/skolni_rad.txt

# Ulož: Ctrl+O, Enter, Ctrl+X
```

## 🗑️ Smazání dokumentu

```bash
# Linux/Mac
rm docs/stary_dokument.txt

# Windows PowerShell
Remove-Item docs/stary_dokument.txt
```

Aplikace ho hned už nenajde!

## ⚠️ Omezení

- **Jen .txt soubory** (bez .pdf, .docx, .html)
- **Max. velikost**: ~100KB na soubor (bezpečnostní limit)
- **Encoding**: UTF-8 (česká diakritika OK)
- **Cesty**: Jen soubory v `docs/` (bez podsložek)

## 🚀 Praktické příklady

### Přidej Školní katalog

```bash
cat > docs/katalog_kurikulum.txt << 'EOF'
KURIKULUM PRO ŠKOLNÍ ROK 2025-2026
==================================

MATEMATIKA - 3. ROČNÍK
-----------------------
Témata:
- Lineární rovnice
- Geometrie
- Pravděpodobnost

ČEŠTINA
-------
Témata:
- Slohové práce
- Literární analýza
EOF
```

### Přidej Pracovní řád

```bash
cat > docs/pracovni_rad.txt << 'EOF'
PRACOVNÍ ŘÁD PRO ZAMĚSTNANCE
=============================

PRACOVNÍ DOBA
-----------
Pondělí-Pátek: 8:00 - 16:30
Přestávka: 12:00 - 13:00

DOVOLENÁ
--------
Základní: 20 dní
Přídavné: Bylo nařízeno

SICK LEAVE
----------
Hlášení do 9:00 školit
Max. 3 dny bez lékařského potvrzení
EOF
```

### Přidej FAQ

```bash
cat > docs/faq.txt << 'EOF'
ČASTO KLADENÉ OTÁZKY
====================

P: Jak se přihlásím do wifi?
O: Síť: KURIM_5GHz, Heslo: ...

P: Kde je serverovna?
O: Místnost 101, 1. patro

P: Jak reportuju problém?
O: Email na IT@kurim.cz
EOF
```

## 🔗 AI dotazy na dokumenty

```bash
# Příklad 1
Dokument: katalog_kurikulum.txt
Otázka: "Co patří do programu matematiky?"
Odpověď: AI přečte obsah a odpoví

# Příklad 2
Dokument: pracovni_rad.txt
Otázka: "Kolik dní dovolené mám?"
Odpověď: "Máš 20 dní základní..."

# Příklad 3
Dokument: faq.txt
Otázka: "Jak se přihlásím do wifi?"
Odpověď: "Síť je KURIM..."
```

## 📊 Management documentů

### Jak sledovat dokumenty

```bash
# Počet souborů
ls -la docs/ | wc -l

# Velikost
du -sh docs/

# Seznam
ls docs/
```

### Backup dokumentů

```bash
# Zálohuj docs/ složku
cp -r docs/ docs_backup_2026_03_31/

# Nebo z Dockeru
docker cp kushaeos:/app/docs ./backup-docs
```

### Monitoring AI requests

Kontroluj které dokumenty se nejvíc používají:
```bash
# V terminálu kde běží app.py se zobrazí logs
# POST /ai ... document_used: skolni_rad.txt
```

## 🎯 Best Practices

1. **Krátké dokumenty** (1-20 KB)
   - Rychlejší čtení AI
   - Lepší relevance
   - Jednodušší pro vyhledávání

2. **Jasná struktura**
   ```
   NÁZEV
   =====
   
   SEKCE
   -----
   Obsah
   ```

3. **Čeština** ✅
   - AI rozumí česky
   - Používej diakritiku

4. **Bez obrázků**
   - Jen text (.txt)
   - Obrázky nejsou čitelné AI

5. **Pravidelné aktualizace**
   - Kontroluj relevanci
   - Smaž zastaralé verze

## 🆘 Problémy

### Dokument se nenačítá

```bash
# Zkontroluj název
ls docs/

# Zkontroluj příponu (.txt)
file docs/muj_dokument.txt

# Zkontroluj encoding
file -i docs/muj_dokument.txt
# Měl by být: text/plain; charset=utf-8
```

### AI neví odpověď z dokumentu

1. Zkontroluj že je dokument vybrán v UI
2. Zkontroluj že obsah existuje
3. Zkontroluj relevanci otázky
4. Otázky musí být v češtině (AI je tuned pro češtinu)

### Soubor je moc velký

AI má limit (přibližně 8000 tokenů):
- ~2000 slov = ~10 KB
- Pokud je větší, rozdělte na menší soubory

---

**Konec dokumentace o dokumentech!** 📚

Pokud máš otázka, kontaktuj IT správce.
