# SEALED KEY — mappatura label → metodo (NON mostrare ai giudici)

Generata con shuffle casuale prima della valutazione. Serve all'un-blinding finale e come
audit trail.

| Label blind | Metodo di ricerca |
|---|---|
| `guide_1.md` | **MCP grezzo** (senza skill, lettura full-page) |
| `guide_2.md` | **WebSearch** (Claude built-in) |
| `guide_3.md` | **MCP + skill** (progressive disclosure) |

Materiale grezzo di origine (pre-anonimizzazione):
- guide_1 ← `test/guide_C_mcp_grezzo.md`
- guide_2 ← `test/guide_A_websearch.md`
- guide_3 ← `test/guide_B_searxng.md`

I 3 giudici ricevono SOLO `rubric.md` + i tre `guide_N.md`. Mai questo file.
