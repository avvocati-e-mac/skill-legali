# Tabella completa degli atti (URN base)

Per trovare un atto cerca con Grep la sigla, il numero e l'anno ("115/2002") o una parola del nome ("edilizia", "navigazione"). Ogni riga è: sigla, nome, URN base.

All'URN base aggiungi `~art` + articolo + `!vig=`. Dove l'URN finisce con `:N`, la posizione dell'allegato è già compresa.

Provenienza: ogni riga è stata controllata dall'autore della skill sul portale il 6 e il 7 ottobre 2026, aprendo con `!vig=` un articolo campione (l'art. 2; l'art. 1 negli atti con un solo articolo; la XII per le disposizioni transitorie) e confrontando atto, tipo, data, posizione e articolo mostrati. Per dieci righe c'è anche il riscontro di un valutatore indipendente del 6 ottobre 2026: c.c., preleggi, c.p.c., disp. att. c.p.c., c.p.p., c.p.a., l. 241/1990, St. lav., d.m. 55/2014, d.P.C.M. 159/2013. Sono controlli passati, non una verifica di oggi. Due righe (r.d. 1611/1933 e d.lgs. 101/2018) vengono dalla tabella precedente del repository e sono state controllate il 6 agosto 2026 con l'API: lo dice la colonna Atto. Una riga aggiunta in seguito senza controllo va marcata "(non controllata)" nella colonna Atto.

**Costituzione**

| Sigla | Atto | URN (base) |
|---|---|---|
| Cost. | Costituzione | `urn:nir:stato:costituzione:1947-12-27` |
| disp. trans. Cost. | Disposizioni transitorie e finali (numero arabo) | `urn:nir:stato:costituzione:1947-12-27:1` |

**Codici e atti il cui testo sta in un allegato**

| Sigla | Atto | URN (base) |
|---|---|---|
| c.c. | Codice civile | `urn:nir:stato:regio.decreto:1942-03-16;262:2` |
| disp. prel. c.c. (preleggi) | Disposizioni sulla legge in generale | `urn:nir:stato:regio.decreto:1942-03-16;262:1` |
| disp. att. c.c. | Disposizioni di attuazione e transitorie del codice civile | `urn:nir:stato:regio.decreto:1942-03-30;318:1` |
| c.p.c. | Codice di procedura civile | `urn:nir:stato:regio.decreto:1940-10-28;1443:1` |
| disp. att. c.p.c. | Disposizioni di attuazione del codice di procedura civile | `urn:nir:stato:regio.decreto:1941-12-18;1368:1` |
| c.p. | Codice penale | `urn:nir:stato:regio.decreto:1930-10-19;1398:1` |
| disp. att. c.p.p. | Norme di attuazione, coordinamento e transitorie del c.p.p. | `urn:nir:stato:decreto.legislativo:1989-07-28;271:1` |
| d.P.R. 448/1988 | Processo penale minorile | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;448:1` |
| c.p.m.p. | Codice penale militare di pace | `urn:nir:stato:regio.decreto:1941-02-20;303:1` |
| c.p.m.g. | Codice penale militare di guerra | `urn:nir:stato:regio.decreto:1941-02-20;303:2` |
| cod. nav. | Codice della navigazione | `urn:nir:stato:regio.decreto:1942-03-30;327:1` |
| reg. cod. nav. | Regolamento navigazione marittima | `urn:nir:stato:decreto.del.presidente.della.repubblica:1952-02-15;328:1` |
| c.p.a. | Codice del processo amministrativo | `urn:nir:stato:decreto.legislativo:2010-07-02;104:2` |
| disp. att. c.p.a. | Norme di attuazione del c.p.a. | `urn:nir:stato:decreto.legislativo:2010-07-02;104:3` |
| c.g.c. | Codice di giustizia contabile | `urn:nir:stato:decreto.legislativo:2016-08-26;174:1` |
| l. fall. | Legge fallimentare | `urn:nir:stato:regio.decreto:1942-03-16;267:1` |
| ord. giud. | Ordinamento giudiziario | `urn:nir:stato:regio.decreto:1941-01-30;12:1` |
| TULPS | Testo unico delle leggi di pubblica sicurezza | `urn:nir:stato:regio.decreto:1931-06-18;773:1` |
| l. camb. | Legge cambiaria | `urn:nir:stato:regio.decreto:1933-12-05;1669:1` |
| l. ass. | Legge assegni | `urn:nir:stato:regio.decreto:1933-12-21;1736:1` |
| cod. turismo | Codice del turismo | `urn:nir:stato:decreto.legislativo:2011-05-23;79:1` |
| t.u. C.d.S. | Testo unico delle leggi sul Consiglio di Stato | `urn:nir:stato:regio.decreto:1924-06-26;1054:1` |
| l. 2248/1865, all. E | Abolizione del contenzioso amministrativo | `urn:nir:stato:legge:1865-03-20;2248:5` |
| t.u. giust. trib. | Testo unico della giustizia tributaria | `urn:nir:stato:decreto.legislativo:2024-11-14;175:1` |
| t.u. sanz. trib. | Testo unico delle sanzioni tributarie | `urn:nir:stato:decreto.legislativo:2024-11-05;173:1` |
| t.u. tributi minori | Testo unico dei tributi erariali minori | `urn:nir:stato:decreto.legislativo:2024-11-05;174:1` |
| t.u. riscossione | Testo unico versamenti e riscossione | `urn:nir:stato:decreto.legislativo:2025-03-24;33:1` |
| t.u. registro | Testo unico imposta di registro e altri tributi indiretti | `urn:nir:stato:decreto.legislativo:2025-08-01;123:1` |
| t.u. IVA 2026 | Testo unico IVA | `urn:nir:stato:decreto.legislativo:2026-01-19;10:1` |
| t.u. redditi 2026 | Testo unico imposte sui redditi | `urn:nir:stato:decreto.legislativo:2026-06-19;117:1` |
| t.u. accertamento 2026 | Testo unico accertamento | `urn:nir:stato:decreto.legislativo:2026-08-05;141:1` |
| r.d. 1611/1933 | Avvocatura dello Stato (controllata il 2026-08-06 con l'API, non sul portale) | `urn:nir:stato:regio.decreto:1933-10-30;1611:1` |

**Codici e testi unici con gli articoli nel corpo dell'atto**

| Sigla | Atto | URN (base) |
|---|---|---|
| c.p.p. | Codice di procedura penale | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447` |
| disp. coord. c.p. | Disposizioni di coordinamento e transitorie del codice penale | `urn:nir:stato:regio.decreto:1931-05-28;601` |
| CCII | Codice della crisi d'impresa e dell'insolvenza | `urn:nir:stato:decreto.legislativo:2019-01-12;14` |
| c.d.s. | Codice della strada | `urn:nir:stato:decreto.legislativo:1992-04-30;285` |
| reg. c.d.s. | Regolamento del codice della strada | `urn:nir:stato:decreto.del.presidente.della.repubblica:1992-12-16;495` |
| cod. cons. | Codice del consumo | `urn:nir:stato:decreto.legislativo:2005-09-06;206` |
| c.a.p. | Codice delle assicurazioni private | `urn:nir:stato:decreto.legislativo:2005-09-07;209` |
| cod. privacy | Codice in materia di protezione dei dati personali | `urn:nir:stato:decreto.legislativo:2003-06-30;196` |
| d.lgs. 101/2018 | Adeguamento del codice privacy al GDPR (controllata il 2026-08-06 con l'API, non sul portale) | `urn:nir:stato:decreto.legislativo:2018-08-10;101` |
| CAD | Codice dell'amministrazione digitale | `urn:nir:stato:decreto.legislativo:2005-03-07;82` |
| c.p.i. | Codice della proprietà industriale | `urn:nir:stato:decreto.legislativo:2005-02-10;30` |
| cod. amb. (TUA) | Norme in materia ambientale | `urn:nir:stato:decreto.legislativo:2006-04-03;152` |
| cod. beni cult. | Codice dei beni culturali e del paesaggio | `urn:nir:stato:decreto.legislativo:2004-01-22;42` |
| cod. contratti pubblici | Codice dei contratti pubblici 2023 | `urn:nir:stato:decreto.legislativo:2023-03-31;36` |
| d.lgs. 50/2016 | Codice dei contratti pubblici 2016 (abrogato) | `urn:nir:stato:decreto.legislativo:2016-04-18;50` |
| cod. antimafia | Codice antimafia | `urn:nir:stato:decreto.legislativo:2011-09-06;159` |
| CTS | Codice del Terzo settore | `urn:nir:stato:decreto.legislativo:2017-07-03;117` |
| cod. pari opp. | Codice delle pari opportunità | `urn:nir:stato:decreto.legislativo:2006-04-11;198` |
| c.o.m. | Codice dell'ordinamento militare | `urn:nir:stato:decreto.legislativo:2010-03-15;66` |
| c.c.e. | Codice delle comunicazioni elettroniche | `urn:nir:stato:decreto.legislativo:2003-08-01;259` |
| cod. prot. civ. | Codice della protezione civile | `urn:nir:stato:decreto.legislativo:2018-01-02;1` |
| cod. nautica | Codice della nautica da diporto | `urn:nir:stato:decreto.legislativo:2005-07-18;171` |
| TUB | Testo unico bancario | `urn:nir:stato:decreto.legislativo:1993-09-01;385` |
| TUF | Testo unico della finanza | `urn:nir:stato:decreto.legislativo:1998-02-24;58` |
| TUEL | Testo unico enti locali | `urn:nir:stato:decreto.legislativo:2000-08-18;267` |
| t.u. edilizia | Testo unico edilizia | `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-06;380` |
| t.u. espropri | Testo unico espropriazioni | `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327` |
| t.u. spese giust. | Testo unico spese di giustizia | `urn:nir:stato:decreto.del.presidente.della.repubblica:2002-05-30;115` |
| t.u. doc. amm. | Testo unico documentazione amministrativa | `urn:nir:stato:decreto.del.presidente.della.repubblica:2000-12-28;445` |
| t.u. casellario | Testo unico casellario giudiziale | `urn:nir:stato:decreto.del.presidente.della.repubblica:2002-11-14;313` |
| TUSL | Testo unico sicurezza sul lavoro | `urn:nir:stato:decreto.legislativo:2008-04-09;81` |
| TUPI | Testo unico pubblico impiego | `urn:nir:stato:decreto.legislativo:2001-03-30;165` |
| TUSP | Testo unico società a partecipazione pubblica | `urn:nir:stato:decreto.legislativo:2016-08-19;175` |
| t.u. imm. | Testo unico immigrazione | `urn:nir:stato:decreto.legislativo:1998-07-25;286` |
| t.u. stup. | Testo unico stupefacenti | `urn:nir:stato:decreto.del.presidente.della.repubblica:1990-10-09;309` |
| t.u. maternità | Testo unico maternità e paternità | `urn:nir:stato:decreto.legislativo:2001-03-26;151` |
| t.u. infortuni | Testo unico infortuni sul lavoro | `urn:nir:stato:decreto.del.presidente.della.repubblica:1965-06-30;1124` |
| TUIR | Testo unico imposte sui redditi 1986 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917` |
| d.P.R. 633/1972 | Decreto IVA | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633` |
| d.P.R. 600/1973 | Accertamento imposte sui redditi | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600` |
| d.P.R. 602/1973 | Riscossione imposte sui redditi | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602` |
| d.P.R. 131/1986 | Testo unico registro 1986 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-04-26;131` |
| d.lgs. 546/1992 | Processo tributario | `urn:nir:stato:decreto.legislativo:1992-12-31;546` |
| d.lgs. 472/1997 | Sanzioni amministrative tributarie | `urn:nir:stato:decreto.legislativo:1997-12-18;472` |
| d.lgs. 74/2000 | Reati tributari | `urn:nir:stato:decreto.legislativo:2000-03-10;74` |

**Leggi e decreti molto citati (articoli nel corpo dell'atto)**

| Sigla | Atto | URN (base) |
|---|---|---|
| l. 241/1990 | Procedimento amministrativo | `urn:nir:stato:legge:1990-08-07;241` |
| St. lav. | Statuto dei lavoratori | `urn:nir:stato:legge:1970-05-20;300` |
| l. 604/1966 | Licenziamenti individuali | `urn:nir:stato:legge:1966-07-15;604` |
| l. 533/1973 | Processo del lavoro | `urn:nir:stato:legge:1973-08-11;533` |
| l. 146/1990 | Sciopero nei servizi pubblici essenziali | `urn:nir:stato:legge:1990-06-12;146` |
| l. 223/1991 | Cassa integrazione e licenziamenti collettivi | `urn:nir:stato:legge:1991-07-23;223` |
| l. 92/2012 | Riforma Fornero | `urn:nir:stato:legge:2012-06-28;92` |
| l. 183/2010 | Collegato lavoro | `urn:nir:stato:legge:2010-11-04;183` |
| d.lgs. 276/2003 | Riforma Biagi | `urn:nir:stato:decreto.legislativo:2003-09-10;276` |
| d.lgs. 23/2015 | Tutele crescenti | `urn:nir:stato:decreto.legislativo:2015-03-04;23` |
| d.lgs. 81/2015 | Disciplina dei contratti di lavoro | `urn:nir:stato:decreto.legislativo:2015-06-15;81` |
| d.lgs. 22/2015 | NASpI | `urn:nir:stato:decreto.legislativo:2015-03-04;22` |
| d.lgs. 148/2015 | Ammortizzatori sociali | `urn:nir:stato:decreto.legislativo:2015-09-14;148` |
| l. 81/2017 | Lavoro autonomo e lavoro agile | `urn:nir:stato:legge:2017-05-22;81` |
| l. 104/1992 | Legge quadro sulla disabilità | `urn:nir:stato:legge:1992-02-05;104` |
| l. 68/1999 | Collocamento dei disabili | `urn:nir:stato:legge:1999-03-12;68` |
| l. 689/1981 | Depenalizzazione e sanzioni amministrative | `urn:nir:stato:legge:1981-11-24;689` |
| l. 392/1978 | Equo canone | `urn:nir:stato:legge:1978-07-27;392` |
| l. 431/1998 | Locazioni abitative | `urn:nir:stato:legge:1998-12-09;431` |
| l. 220/2012 | Riforma del condominio | `urn:nir:stato:legge:2012-12-11;220` |
| l. 203/1982 | Contratti agrari | `urn:nir:stato:legge:1982-05-03;203` |
| d.lgs. 122/2005 | Immobili da costruire | `urn:nir:stato:decreto.legislativo:2005-06-20;122` |
| l. 47/1985 | Controllo dell'attività urbanistico-edilizia | `urn:nir:stato:legge:1985-02-28;47` |
| l. 1150/1942 | Legge urbanistica | `urn:nir:stato:legge:1942-08-17;1150` |
| l. div. | Legge sul divorzio | `urn:nir:stato:legge:1970-12-01;898` |
| l. 184/1983 | Adozione e affidamento | `urn:nir:stato:legge:1983-05-04;184` |
| l. 54/2006 | Affidamento condiviso | `urn:nir:stato:legge:2006-02-08;54` |
| l. 219/2012 | Riconoscimento dei figli | `urn:nir:stato:legge:2012-12-10;219` |
| d.lgs. 154/2013 | Riforma della filiazione | `urn:nir:stato:decreto.legislativo:2013-12-28;154` |
| l. 6/2004 | Amministrazione di sostegno | `urn:nir:stato:legge:2004-01-09;6` |
| l. 76/2016 | Unioni civili e convivenze | `urn:nir:stato:legge:2016-05-20;76` |
| l. 194/1978 | Interruzione volontaria della gravidanza | `urn:nir:stato:legge:1978-05-22;194` |
| l. 40/2004 | Procreazione medicalmente assistita | `urn:nir:stato:legge:2004-02-19;40` |
| l. 219/2017 | Consenso informato e DAT | `urn:nir:stato:legge:2017-12-22;219` |
| l. 24/2017 | Legge Gelli-Bianco | `urn:nir:stato:legge:2017-03-08;24` |
| d.P.R. 396/2000 | Ordinamento dello stato civile | `urn:nir:stato:decreto.del.presidente.della.repubblica:2000-11-03;396` |
| l. 218/1995 | Diritto internazionale privato | `urn:nir:stato:legge:1995-05-31;218` |
| l.d.a. | Legge sul diritto d'autore | `urn:nir:stato:legge:1941-04-22;633` |
| l. 287/1990 | Legge antitrust | `urn:nir:stato:legge:1990-10-10;287` |
| l. 108/1996 | Usura | `urn:nir:stato:legge:1996-03-07;108` |
| l. 3/2012 | Sovraindebitamento | `urn:nir:stato:legge:2012-01-27;3` |
| d.lgs. 270/1999 | Amministrazione straordinaria | `urn:nir:stato:decreto.legislativo:1999-07-08;270` |
| d.lgs. 231/2001 | Responsabilità degli enti | `urn:nir:stato:decreto.legislativo:2001-06-08;231` |
| d.lgs. 231/2002 | Ritardi di pagamento | `urn:nir:stato:decreto.legislativo:2002-10-09;231` |
| d.lgs. 231/2007 | Antiriciclaggio | `urn:nir:stato:decreto.legislativo:2007-11-21;231` |
| d.lgs. 70/2003 | Commercio elettronico | `urn:nir:stato:decreto.legislativo:2003-04-09;70` |
| d.lgs. 24/2023 | Whistleblowing | `urn:nir:stato:decreto.legislativo:2023-03-10;24` |
| d.lgs. 33/2013 | Trasparenza amministrativa | `urn:nir:stato:decreto.legislativo:2013-03-14;33` |
| l. 190/2012 | Legge anticorruzione | `urn:nir:stato:legge:2012-11-06;190` |
| l. 20/1994 | Giurisdizione e controllo della Corte dei conti | `urn:nir:stato:legge:1994-01-14;20` |
| l. 1034/1971 | Legge TAR | `urn:nir:stato:legge:1971-12-06;1034` |
| d.P.R. 1199/1971 | Ricorsi amministrativi | `urn:nir:stato:decreto.del.presidente.della.repubblica:1971-11-24;1199` |
| l. 87/1953 | Corte costituzionale | `urn:nir:stato:legge:1953-03-11;87` |
| l. 400/1988 | Attività di Governo | `urn:nir:stato:legge:1988-08-23;400` |
| l. 212/2000 | Statuto del contribuente | `urn:nir:stato:legge:2000-07-27;212` |
| l. 89/2001 | Legge Pinto | `urn:nir:stato:legge:2001-03-24;89` |
| l. 742/1969 | Sospensione feriale dei termini | `urn:nir:stato:legge:1969-10-07;742` |
| l. 890/1982 | Notificazioni a mezzo posta | `urn:nir:stato:legge:1982-11-20;890` |
| l. 53/1994 | Notificazioni degli avvocati | `urn:nir:stato:legge:1994-01-21;53` |
| l. 69/2009 | Riforma del processo civile 2009 | `urn:nir:stato:legge:2009-06-18;69` |
| d.lgs. 28/2010 | Mediazione civile e commerciale | `urn:nir:stato:decreto.legislativo:2010-03-04;28` |
| d.l. 132/2014 | Negoziazione assistita | `urn:nir:stato:decreto.legge:2014-09-12;132` |
| d.lgs. 150/2011 | Semplificazione dei riti civili | `urn:nir:stato:decreto.legislativo:2011-09-01;150` |
| l. 206/2021 | Delega riforma processo civile | `urn:nir:stato:legge:2021-11-26;206` |
| d.lgs. 149/2022 | Riforma Cartabia civile | `urn:nir:stato:decreto.legislativo:2022-10-10;149` |
| d.lgs. 164/2024 | Correttivo Cartabia civile | `urn:nir:stato:decreto.legislativo:2024-10-31;164` |
| l. 134/2021 | Delega riforma processo penale | `urn:nir:stato:legge:2021-09-27;134` |
| d.lgs. 150/2022 | Riforma Cartabia penale | `urn:nir:stato:decreto.legislativo:2022-10-10;150` |
| d.lgs. 274/2000 | Giudice di pace penale | `urn:nir:stato:decreto.legislativo:2000-08-28;274` |
| l. 374/1991 | Istituzione del giudice di pace | `urn:nir:stato:legge:1991-11-21;374` |
| d.lgs. 116/2017 | Magistratura onoraria | `urn:nir:stato:decreto.legislativo:2017-07-13;116` |
| ord. pen. | Ordinamento penitenziario | `urn:nir:stato:legge:1975-07-26;354` |
| d.P.R. 230/2000 | Regolamento penitenziario | `urn:nir:stato:decreto.del.presidente.della.repubblica:2000-06-30;230` |
| l. 69/2019 | Codice rosso | `urn:nir:stato:legge:2019-07-19;69` |
| l. 247/2012 | Ordinamento forense | `urn:nir:stato:legge:2012-12-31;247` |
| r.d.l. 1578/1933 | Vecchia legge professionale forense | `urn:nir:stato:regio.decreto.legge:1933-11-27;1578` |
| l. not. | Legge notarile | `urn:nir:stato:legge:1913-02-16;89` |
| d.l. 179/2012 | Crescita 2.0 (processo telematico) | `urn:nir:stato:decreto.legge:2012-10-18;179` |

**Decreti ministeriali e d.P.C.M. numerati**

| Sigla | Atto | URN (base) |
|---|---|---|
| d.m. 55/2014 | Parametri forensi | `urn:nir:ministero.giustizia:decreto:2014-03-10;55` |
| d.m. 147/2022 | Modifica dei parametri forensi | `urn:nir:ministero.giustizia:decreto:2022-08-13;147` |
| d.m. 140/2012 | Parametri professioni regolamentate | `urn:nir:ministero.giustizia:decreto:2012-07-20;140` |
| d.m. 44/2011 | Regole tecniche processo telematico | `urn:nir:ministero.giustizia:decreto:2011-02-21;44` |
| d.m. 110/2023 | Criteri di redazione degli atti | `urn:nir:ministero.giustizia:decreto:2023-08-07;110` |
| d.m. 150/2023 | Regolamento mediazione | `urn:nir:ministero.giustizia:decreto:2023-10-24;150` |
| d.m. 180/2010 | Regolamento mediazione 2010 | `urn:nir:ministero.giustizia:decreto:2010-10-18;180` |
| d.m. 202/2014 | Organismi di composizione della crisi | `urn:nir:ministero.giustizia:decreto:2014-09-24;202` |
| d.m. 37/2008 | Impianti negli edifici | `urn:nir:ministero.sviluppo.economico:decreto:2008-01-22;37` |
| d.P.C.M. 159/2013 | ISEE | `urn:nir:presidenza.consiglio.ministri:decreto:2013-12-05;159` |
