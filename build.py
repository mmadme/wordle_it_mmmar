from __future__ import annotations
import json, sys, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent
DIST_DIR=BASE_DIR/"dist"
DOCS_DIR=BASE_DIR/"docs"
FILE_HTML=DIST_DIR/"parole-infinito.html"
FILE_API_CONFIG=DIST_DIR/"api-config.js"
FILE_SOL=DIST_DIR/"parole_soluzioni.txt"
FILE_TEN=DIST_DIR/"parole_tentativi.txt"
FILE_LOG=DOCS_DIR/"build_log.md"
FILE_HISTORY=DOCS_DIR/"build_history.md"
TEMPLATE_HTML=BASE_DIR/"src"/"template_parole.html"
URL_SOL="https://raw.githubusercontent.com/pietroppeter/wordle-it/master/dict/curated.txt"
URL_TEN="https://raw.githubusercontent.com/pietroppeter/wordle-it/master/dict/word_list.txt"
LETTERE_OK=set("abcdefghijklmnopqrstuvwxyz")
VOCALI=set("aeiou")

FORESTIERISMI_COMUNI={"album","audio","bazar","bidet","clown","curry","extra","flash","focus","hobby","kappa","karma","koala","lobby","ninja","nylon","relax","rebus","ribes","speck","sport","sushi","virus"}
PRESTITI_STABILI={"alias","focus","ictus","lapis","rebus","ribes","silos","virus"}
FORESTIERISMI_DA_ESCLUDERE={"ebook","jeans","shake","share","shari","sharo","shina","shire","skate","smoke","spike","texta","texte","texti","texto","trans","white"}
VERBI_PRESENTE_AMMESSI={"colgo","conto","copri","entra","fanno","giace","gioca","guida","hanno","invio","opera","pensa","pesco","pongo","posso","punge","sanno","sorge","tengo","tieni","trova","usano","usare","valgo","vanno","venga","vendo","vieni","vinco","vuole"}

SOLUZIONI_SEMPRE_COMUNI={"acqua","aiuto","amore","amici","banca","barca","carne","carta","causa","cielo","cuore","danno","donna","ferro","festa","fiore","forza","gatto","gioco","hotel","latte","madre","metro","mondo","notte","padre","paese","parte","porta","prato","regno","ruota","sasso","scena","sedia","serra","sogno","suono","tempo","terra","testa","vento"}

# Da rimuovere completamente dalle soluzioni (restano nei tentativi)
SOLUZIONI_DA_RIMUOVERE={"bidet","biada","bitta","cruna","sport","torba","alice","nuche","avolo","oneri","acume","bulbo","pepsi"}

# Override forzato al livello altissimo
SOLUZIONI_LIVELLO_ALTISSIMO={"amala","gamma","orgia","tesse","tonno","adula","beffa","lutto","vinti","imita","grata"}

# Override forzato al livello alto
SOLUZIONI_LIVELLO_ALTO={"prete","punge","serpe","greco","omega","colgo","baffi","rossa","folle","motto"}

# Aggiunte manuali: inserite nelle soluzioni a livello medio
SOLUZIONI_AGGIUNTE_MANUALI={"froci","negra"}

# Pesi per ogni livello (devono sommare 100)
# Infinita facile:    bassissima 45% | bassa 30% | media 15% | alta  8% | altissima  2%
# Infinita media:     bassissima 25% | bassa 25% | media 25% | alta 18% | altissima  7%
# Infinita difficile: bassissima  5% | bassa 10% | media 20% | alta 35% | altissima 30%
# Giornaliera:        bassissima 10% | bassa 20% | media 35% | alta 25% | altissima 10%
PESI_INFINITA_FACILE    = [45, 30, 15,  8,  2]
PESI_INFINITA_MEDIA     = [25, 25, 25, 18,  7]
PESI_INFINITA_DIFFICILE = [ 5, 10, 20, 35, 30]
PESI_DAILY              = [10, 20, 35, 25, 10]
LIVELLI                 = ["bassissima", "bassa", "media", "alta", "altissima"]


class Log:
    def __init__(self,path,history):
        self.path=path; self.history=history; self.start=datetime.now()
        self.lines=["# Build log - Parole Infinito\n",
                    f"**Data:** {self.start.strftime('%d/%m/%Y %H:%M:%S')}  ",
                    "**Script:** build.py  ",""]
    def section(self,title): self.lines+=["",f"## {title}\n"]; print(f"\n{title}")
    def info(self,text): self.lines.append(f"- {text}  "); print(f"  {text}")
    def ok(self,text): self.lines.append(f"- OK {text}  "); print(f"  OK {text}")
    def table(self,rows):
        self.lines.append("| "+" | ".join(rows[0])+" |")
        self.lines.append("| "+" | ".join("---" for _ in rows[0])+" |")
        for row in rows[1:]: self.lines.append("| "+" | ".join(str(c) for c in row)+" |")
        self.lines.append("")
    def save(self,summary):
        secs=int((datetime.now()-self.start).total_seconds())
        self.lines+=["\n---\n","**Stato:** OK  ",f"**Durata:** {secs}s  "]
        self.path.write_text("\n".join(self.lines),encoding="utf-8")
        if not self.history.exists():
            self.history.write_text("# Storico Build - Parole Infinito\n\n",encoding="utf-8")
        with self.history.open("a",encoding="utf-8") as fh:
            fh.write(summary.rstrip()+"\n\n")

def ensure_dirs():
    DIST_DIR.mkdir(parents=True,exist_ok=True)
    DOCS_DIR.mkdir(parents=True,exist_ok=True)

def scarica(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=60) as resp:
        return resp.read().decode("utf-8",errors="ignore").splitlines()

def parola_valida(word):
    p=word.strip().lower()
    if len(p)!=5 or not all(c in LETTERE_OK for c in p) or not any(c in VOCALI for c in p): return False
    streak=0
    for c in p:
        streak=0 if c in VOCALI else streak+1
        if streak>=4: return False
    return True

def filtra(lines):
    out=[]; seen=set()
    for line in lines:
        p=line.strip().lower()
        if parola_valida(p) and p not in seen: seen.add(p); out.append(p)
    return sorted(out)

def troppo_forestiera(word):
    if word in FORESTIERISMI_COMUNI or word in PRESTITI_STABILI: return False
    if word in FORESTIERISMI_DA_ESCLUDERE: return True
    if ("sh" in word or "wh" in word) and word not in FORESTIERISMI_COMUNI: return True
    return word.endswith("s") and word not in PRESTITI_STABILI

def screma_tentativi(words):
    rimossi=sorted(w for w in words if troppo_forestiera(w)); banned=set(rimossi)
    return sorted(w for w in words if w not in banned), rimossi

def screma_soluzioni(words):
    eccezioni_ai={"assai","guai","rasoi","solai","ormai","avrai"}
    suffissi=("rei","avo","avi","ava","ivo","ivi","iva","evo","eva")
    keep_suffissi={"bravi","clava","ogiva","privo","stiva","ulivo"}
    borderline={"annoi","berci","berlo","cadde","dillo","dimmi","disto","duole","educa","eludo","epuro","evoco","fremo","narri","opino","parve","pecco","premi","prude","pulsa","sappi","scade","scavo","serro","sfida","sfila","sfogo","studi","tatuo","togli","univa","vegli","vibra","vinse","visse","volle"}
    blacklist={"biada","bioma","blesa","cesio","cespo","coesa","coevo","coffa","crasi","curda","dicco","diade","diodo","drupa","ebete","efebo","egizi","emoji","emulo","etimo","gnosi","jeans","litio","lombi","lonza","lucci","masai","mozzi","muone","nonio","odino","orafe","orcio","ovaia","peana","peplo","prono","prora","probo","prode","pruno","rebbi","ridda","riffa","ronfa","rubli","ruzzo","sabba","saghe","sansa","savio","scolo","sfuso","sinti","solfa","spola","sport","stola","sugna","sunto","svevo","taiga","talea","tallo","tanfo","tarso","teppa","terga","turpe","ubbia","uggia","vieto","vocio","zirlo","zompo","zonzo","zozze"}|SOLUZIONI_DA_RIMUOVERE
    keep={"avrai","cromo","elogi","epica","pacca","plebe","rebus","rughe","scemi","sfizi","sobri","solai","spore"}
    removed=set(); reasons=defaultdict(set)

    for word in words:
        if word in keep or word in SOLUZIONI_AGGIUNTE_MANUALI: continue
        if word.endswith("ii"): removed.add(word); reasons["passati remoti in -ii"].add(word); continue
        if word.endswith("ai") and word not in eccezioni_ai: removed.add(word); reasons["passati remoti in -ai"].add(word); continue
        if word.endswith(suffissi) and word not in keep_suffissi: removed.add(word); reasons["forme verbali complesse"].add(word); continue
        if word in borderline and word not in VERBI_PRESENTE_AMMESSI: removed.add(word); reasons["presenti poco naturali come soluzione"].add(word); continue
        if word in blacklist: removed.add(word); reasons["parole tecniche, arcaiche o borderline"].add(word)

    families=defaultdict(set)
    for word in words:
        if word in removed or word in SOLUZIONI_SEMPRE_COMUNI or word in SOLUZIONI_AGGIUNTE_MANUALI: continue
        for i in range(5): families[word[:i]+"_"+word[i+1:]].add(word)
    for group in families.values():
        if len(group)<6: continue
        for word in group:
            if word in SOLUZIONI_SEMPRE_COMUNI or word in SOLUZIONI_AGGIUNTE_MANUALI: continue
            if len(set(word))<5 or len(group)>=7: removed.add(word); reasons["cluster troppo ambiguo per 6 tentativi"].add(word)

    result=sorted(w for w in words if w not in removed)
    # Aggiungi manuali non presenti nel vocabolario sorgente
    base_set=set(words)
    for w in sorted(SOLUZIONI_AGGIUNTE_MANUALI):
        if w not in base_set and parola_valida(w):
            result=sorted(result+[w])
            reasons["aggiunte manuali"].add(w)

    return result, {k:sorted(v) for k,v in sorted(reasons.items())}

def ha_doppie(parola):
    return any(parola[i]==parola[i+1] for i in range(len(parola)-1))

def classifica_difficolta(words):
    """
    Classifica le soluzioni in 5 livelli di difficoltà.

    Punteggio per ogni parola:
      +alto  = lettere rare nel corpus (più difficile da indovinare)
      +1.2   = ha lettere doppie (cluster punitivo)
      +0.8   = contiene z/q/j/x/k/y/w
      +0.6   = meno di 4 lettere distinte
      -3.0   = parola comunissima (SOLUZIONI_SEMPRE_COMUNI)
      +5.0   = override altissimo manuale
      +2.5   = override alto manuale

    Soglie cumulative (sul ranking ordinato per punteggio):
      bassissima 0-30% | bassa 30-55% | media 55-80% | alta 80-95% | altissima 95-100%

    Pesi estrazione:
      Infinita facile:    bassissima 45% | bassa 30% | media 15% | alta  8% | altissima  2%
      Infinita media:     bassissima 25% | bassa 25% | media 25% | alta 18% | altissima  7%
      Infinita difficile: bassissima  5% | bassa 10% | media 20% | alta 35% | altissima 30%
      Giornaliera:        bassissima 10% | bassa 20% | media 35% | alta 25% | altissima 10%
    """
    if not words:
        return {k:[] for k in LIVELLI}

    letters=Counter("".join(words))
    scored=[]
    for word in words:
        score=sum(1/letters[ch] for ch in word)*1000
        if ha_doppie(word): score+=1.2
        if any(ch in "zqjxkyw" for ch in word): score+=0.8
        if len(set(word))<4: score+=0.6
        if word in SOLUZIONI_SEMPRE_COMUNI: score-=3.0
        if word in SOLUZIONI_LIVELLO_ALTISSIMO: score+=5.0
        if word in SOLUZIONI_LIVELLO_ALTO: score+=2.5
        scored.append((score,word))
    scored.sort()

    n=len(scored)
    cuts=[int(n*0.30), int(n*0.55), int(n*0.80), int(n*0.95), n]
    livello_parola={}
    for i,(soglia,livello) in enumerate(zip(cuts,LIVELLI)):
        prev=cuts[i-1] if i>0 else 0
        for _,w in scored[prev:soglia]:
            livello_parola[w]=livello

    # Override manuali (sovrascrivono il calcolo)
    for word in words:
        if word in SOLUZIONI_SEMPRE_COMUNI:
            livello_parola[word]="bassissima"
        elif word in SOLUZIONI_LIVELLO_ALTISSIMO:
            livello_parola[word]="altissima"
        elif word in SOLUZIONI_LIVELLO_ALTO:
            livello_parola[word]="alta"

    # Aggiunte manuali → media (se non già assegnate da override)
    for word in SOLUZIONI_AGGIUNTE_MANUALI:
        if word in livello_parola and word not in SOLUZIONI_LIVELLO_ALTISSIMO and word not in SOLUZIONI_LIVELLO_ALTO:
            livello_parola[word]="media"

    # Doppie: livello minimo "alta" (a meno che non siano già altissima)
    LIVELLI_SOTTO_ALTA = {"bassissima", "bassa", "media"}
    for word in words:
        if ha_doppie(word) and livello_parola.get(word) in LIVELLI_SOTTO_ALTA:
            livello_parola[word] = "alta"

    result={k:[] for k in LIVELLI}
    for word,livello in sorted(livello_parola.items()):
        result[livello].append(word)
    for k in result:
        result[k]=sorted(result[k])
    return result

def lista_js(words,per_riga=10):
    rows=[]
    for i in range(0,len(words),per_riga):
        rows.append("    "+", ".join(json.dumps(w) for w in words[i:i+per_riga]))
    return "[\n"+",\n".join(rows)+"\n  ]"

def genera_html(soluzioni,tentativi,categorie):
    def cum(pesi):
        out=[]; s=0
        for p in pesi: s+=p; out.append(s)
        return out

    cum_facile=cum(PESI_INFINITA_FACILE)
    cum_media=cum(PESI_INFINITA_MEDIA)
    cum_difficile=cum(PESI_INFINITA_DIFFICILE)
    cum_daily=cum(PESI_DAILY)

    block=(
        f"// --VOCAB-START--\n"
        f"const SOLUZIONI = {lista_js(soluzioni)};\n"
        f"const SOLUZIONI_BASSISSIMA = {lista_js(categorie['bassissima'])};\n"
        f"const SOLUZIONI_BASSA      = {lista_js(categorie['bassa'])};\n"
        f"const SOLUZIONI_MEDIA      = {lista_js(categorie['media'])};\n"
        f"const SOLUZIONI_ALTA       = {lista_js(categorie['alta'])};\n"
        f"const SOLUZIONI_ALTISSIMA  = {lista_js(categorie['altissima'])};\n"
        f"// Pesi cumulativi: facile {cum_facile}  media {cum_media}  difficile {cum_difficile}  daily {cum_daily}\n"
        f"const PESI_CUM_INFINITA_FACILE    = {cum_facile};\n"
        f"const PESI_CUM_INFINITA_MEDIA     = {cum_media};\n"
        f"const PESI_CUM_INFINITA_DIFFICILE = {cum_difficile};\n"
        f"const PESI_CUM_DAILY              = {cum_daily};\n"
        f"const _TENTATIVI_EXTRA = {lista_js(tentativi)};\n"
        f"// --VOCAB-END--"
    )
    html=TEMPLATE_HTML.read_text(encoding="utf-8")
    start=html.index("// --VOCAB-START--\nconst SOLUZIONI")
    end=html.index("// --VOCAB-END--",start)+len("// --VOCAB-END--")
    return html[:start]+block+html[end:]

def write_word_file(path,title,source,words):
    path.write_text(
        f"# {title} - {len(words)} parole\n"
        f"# Fonte: {source}\n"
        f"# Generato da build.py il {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        +"\n".join(words), encoding="utf-8"
    )

def write_api_config(path, api_base=""):
    normalized=api_base.strip().rstrip("/")
    path.write_text(
        "// Configurazione frontend per build statiche o GitHub Pages.\n"
        "// Imposta l'URL base delle API remote; lascia stringa vuota per stesso host.\n"
        f'window.WOORDLE_API_BASE_URL = "{normalized}";\n',
        encoding="utf-8"
    )

def create_summary(sol,ten_raw,ten_fil,ten,cat):
    ts=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dist="\n".join(f"  - {k}: {len(v)}" for k,v in cat.items())
    return (
        f"## Build del {ts}\n\n"
        f"- Stato: successo\n"
        f"- Soluzioni finali: {len(sol):,}\n"
        f"- Distribuzione livelli:\n{dist}\n"
        f"- Tentativi originali: {len(ten_raw):,}\n"
        f"- Tentativi dopo scrematura: {len(ten_fil):,}\n"
        f"- Tentativi finali accettati: {len(ten):,}\n"
        f"- File aggiornati: `dist/parole-infinito.html`, `dist/parole_soluzioni.txt`, `dist/parole_tentativi.txt`, `docs/build_log.md`\n"
    )

def main():
    ensure_dirs()
    log=Log(FILE_LOG,FILE_HISTORY)

    log.section("Download vocabolari")
    sol_src=scarica(URL_SOL); ten_src=scarica(URL_TEN)
    log.ok(f"curated.txt scaricato: {len(sol_src):,} righe")
    log.ok(f"word_list.txt scaricato: {len(ten_src):,} righe")

    log.section("Filtraggio base")
    sol_raw=filtra(sol_src); ten_raw=filtra(ten_src)
    log.ok(f"Soluzioni valide: {len(sol_raw):,}")
    log.ok(f"Tentativi validi: {len(ten_raw):,}")

    log.section("Scrematura soluzioni")
    sol,motivi=screma_soluzioni(sol_raw)
    log.ok(f"Soluzioni finali: {len(sol):,}")
    [log.info(f"{k}: {', '.join(v)}") for k,v in motivi.items() if v]

    log.section("Classificazione difficolta (5 livelli)")
    categorie=classifica_difficolta(sol)
    for livello in LIVELLI:
        log.ok(f"{livello}: {len(categorie[livello]):,} parole")
    log.info(f"Pesi infinita facile:    {PESI_INFINITA_FACILE}")
    log.info(f"Pesi infinita media:     {PESI_INFINITA_MEDIA}")
    log.info(f"Pesi infinita difficile: {PESI_INFINITA_DIFFICILE}")
    log.info(f"Pesi daily:              {PESI_DAILY}")

    log.section("Scrematura tentativi")
    ten_fil,ten_rim=screma_tentativi(ten_raw)
    ten=sorted(set(ten_fil)|set(sol))
    log.ok(f"Tentativi finali: {len(ten):,}")
    ten_rim and log.info(f"Forestierismi rimossi: {', '.join(ten_rim)}")

    log.section("Riepilogo vocabolario")
    log.table([("Lista","Parole"),
               ("Soluzioni iniziali",f"{len(sol_raw):,}"),
               ("Soluzioni finali",f"{len(sol):,}"),
               ("Tentativi iniziali",f"{len(ten_raw):,}"),
               ("Tentativi finali",f"{len(ten):,}")])

    log.section("Scrittura output")
    write_word_file(FILE_SOL,"Parole soluzioni","curated.txt (scremato)",sol)
    write_word_file(FILE_TEN,"Parole tentativi","word_list.txt + curated.txt",ten)
    FILE_HTML.write_text(genera_html(sol,ten,categorie),encoding="utf-8")
    write_api_config(FILE_API_CONFIG)
    log.ok(f"Scritto {FILE_SOL.relative_to(BASE_DIR)}")
    log.ok(f"Scritto {FILE_TEN.relative_to(BASE_DIR)}")
    log.ok(f"Scritto {FILE_HTML.relative_to(BASE_DIR)}")
    log.ok(f"Scritto {FILE_API_CONFIG.relative_to(BASE_DIR)}")

    log.save(create_summary(sol,ten_raw,ten_fil,ten,categorie))
    print(f"\nBuild completata. Apri {FILE_HTML}")

if __name__=="__main__":
    try: main()
    except Exception as exc: print(f"Errore build: {exc}"); sys.exit(1)
