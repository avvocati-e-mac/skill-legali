#!/usr/bin/env zsh
# Alternativa a scarica.py quando python3 non c'e'. Richiede solo zsh (o bash) e curl.
#
# Uso:  zsh scarica.sh <piano.tsv> <cartella_pdf>
#
# piano.tsv: una riga per file, 4 colonne separate da TABULAZIONE, nessuna vuota
# (se un dato manca scrivi - ):
#     url_file <TAB> url_scheda <TAB> nome_file <TAB> formato
# nome_file ASCII, di solito AAAA-MM-GG_ufficio_numero_<id>.pdf; formato = pdf oppure html.
# Righe vuote o che iniziano con # sono ignorate.
#
# Stessa logica di scarica.py: user-agent da browser, Referer = url_scheda, 2 nuovi
# tentativi, 2 secondi tra un file e l'altro, salta i file gia' presenti, rispetta
# robots.txt, tiene il file solo se inizia con %PDF (o e' HTML), altrimenti lo elimina
# e lo annota in errori.txt (accanto al piano). Non disattiva mai i controlli dei certificati.
# Codice di uscita: 0 = nessun errore, 1 = almeno un errore.

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
PIANO="$1"
DEST="$2"

if [ -z "$PIANO" ] || [ -z "$DEST" ]; then
  echo "Uso: zsh scarica.sh <piano.tsv> <cartella_pdf>"
  exit 2
fi
if [ ! -r "$PIANO" ]; then
  echo "File del piano non trovato: $PIANO"
  exit 2
fi
mkdir -p "$DEST" || exit 2

ERR="$(cd "$(dirname "$PIANO")" && pwd)/errori.txt"
: > "$ERR"
TMPD="$(mktemp -d)"
trap 'rm -rf "$TMPD"' EXIT

n_ok=0
n_skip=0
n_err=0
primo=1

registra_errore() {
  echo "$1" >> "$ERR"
  echo "  - $1"
  n_err=$((n_err + 1))
}

# Ritorna 0 se robots.txt non vieta l'URL (solo http/https). Gestisce solo le regole
# semplici (User-agent: *, Allow, Disallow a prefisso); i caratteri jolly sono ignorati.
robots_ok() {
  case "$1" in
    http://*|https://*) ;;
    *) return 0 ;;
  esac
  r_scheme="${1%%://*}"
  r_rest="${1#*://}"
  r_host="${r_rest%%/*}"
  if [ "$r_rest" = "$r_host" ]; then
    r_pth="/"
  else
    r_pth="/${r_rest#*/}"
  fi
  r_cache="$TMPD/robots_$(printf '%s' "$r_host" | tr -c 'A-Za-z0-9\n' '_')"
  if [ ! -f "$r_cache" ]; then
    curl -sS -f -L -m 20 -A "$UA" -o "$r_cache" "$r_scheme://$r_host/robots.txt" 2>/dev/null || : > "$r_cache"
  fi
  r_esito="$(awk -v p="$r_pth" '
    BEGIN { ingruppo = 0; regole = 0; dis = 0; all = 0 }
    {
      sub(/\r$/, ""); l = $0; sub(/#.*/, "", l)
      low = tolower(l)
      if (low ~ /^[ \t]*user-agent[ \t]*:/) {
        v = l; sub(/^[^:]*:[ \t]*/, "", v); gsub(/[ \t]+$/, "", v)
        if (regole) { ingruppo = 0; regole = 0 }
        if (v == "*") ingruppo = 1
      } else if (low ~ /^[ \t]*(dis)?allow[ \t]*:/) {
        regole = 1
        if (ingruppo) {
          v = l; sub(/^[^:]*:[ \t]*/, "", v); gsub(/[ \t]+$/, "", v)
          if (v != "" && v !~ /[*$]/ && index(p, v) == 1) {
            if (low ~ /^[ \t]*disallow/) { if (length(v) > dis) dis = length(v) }
            else { if (length(v) > all) all = length(v) }
          }
        }
      }
    }
    END { if (dis > 0 && dis > all) print "VIETATO"; else print "OK" }
  ' "$r_cache")"
  [ "$r_esito" = "OK" ]
}

valido() {
  # $1 = file, $2 = formato
  if [ "$2" = "html" ]; then
    head -c 2000 "$1" | LC_ALL=C tr 'A-Z' 'a-z' | grep -Eq '<html|<!doctype html'
  else
    [ "$(head -c 4 "$1")" = "%PDF" ]
  fi
}

while IFS="$(printf '\t')" read -r url_file url_scheda nome formato || [ -n "$url_file" ]; do
  url_file="${url_file%$(printf '\r')}"
  formato="${formato%$(printf '\r')}"
  [ -z "$url_file" ] && continue
  case "$url_file" in \#*) continue ;; esac
  [ -z "$formato" ] && formato="pdf"
  if [ -z "$nome" ] || [ "$nome" = "-" ]; then
    registra_errore "riga senza nome_file: $url_file"
    continue
  fi
  f_dest="$DEST/$nome"
  if [ -s "$f_dest" ]; then
    n_skip=$((n_skip + 1))
    continue
  fi
  if [ "$url_file" = "-" ]; then
    registra_errore "$nome: url_file mancante"
    continue
  fi
  if [ "$primo" = "0" ]; then sleep 2; fi
  primo=0
  if ! robots_ok "$url_file"; then
    registra_errore "$nome: robots.txt del sito vieta questo percorso, non scaricato ($url_file)"
    continue
  fi
  f_tmp="$f_dest.part"
  rm -f "$f_tmp"
  if [ "$url_scheda" = "-" ] || [ -z "$url_scheda" ]; then
    curl -L --fail --retry 2 -sS -A "$UA" -o "$f_tmp" "$url_file" 2>"$TMPD/curl.err"
  else
    curl -L --fail --retry 2 -sS -A "$UA" -e "$url_scheda" -o "$f_tmp" "$url_file" 2>"$TMPD/curl.err"
  fi
  rc=$?
  if [ "$rc" -ne 0 ]; then
    rm -f "$f_tmp"
    registra_errore "$nome: download non riuscito (curl $rc: $(head -c 200 "$TMPD/curl.err" | tr '\n' ' ')) ($url_file)"
    continue
  fi
  if valido "$f_tmp" "$formato"; then
    mv "$f_tmp" "$f_dest"
    n_ok=$((n_ok + 1))
  else
    rm -f "$f_tmp"
    registra_errore "$nome: il file scaricato non e' $formato valido (probabile pagina di errore o di login) ($url_file)"
  fi
done < "$PIANO"

echo "Scaricati: $n_ok   Saltati (gia' presenti): $n_skip   Errori: $n_err"
if [ "$n_err" -gt 0 ]; then
  echo "Dettaglio in $ERR"
  exit 1
fi
rm -f "$ERR"
exit 0
