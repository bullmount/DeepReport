report_planner_query_writer_instructions="""Stai svolgendo ricerche per un report.

<Argomento del report>
{topic}
</Argomento del report>

<Organizzazione del report>
{report_organization}
</Organizzazione del report>

<Task>
Il tuo obiettivo è generare {number_of_queries} query di ricerca web che aiuteranno a raccogliere informazioni per pianificare le sezioni del report.

Le query devono:

1. Essere correlate all'argomento del report
2. Aiutare a soddisfare i requisiti specificati nell'organizzazione del report

Crea query sufficientemente specifiche per trovare fonti rilevanti e di alta qualità, coprendo allo stesso tempo l'ampiezza necessaria per la struttura del report.
</Task>

<Format>
La risposta deve essere in formato JSON secondo questo schema:
{json_format}
</Format>
"""

report_planner_instructions="""Voglio un piano per un report che sia conciso e mirato.

<Report topic>
L'argomento del report è:
{topic}
</Report topic>

<Report organization>
Il report dovrebbe seguire questa organizzazione: 
{report_organization}
</Report organization>

<Context>
Questo è il contesto da utilizzare per pianificare le sezioni del report: 
{context}
</Context>

<Task>
Genera un elenco di sezioni per il report. 
Il tuo piano deve essere essenziale e mirato SENZA sezioni che si sovrappongono nei contenuti o con contenuti superflui.

Ad esempio, una buona struttura di report potrebbe essere:
1/ introduzione
2/ panoramica dell'argomento A
3/ panoramica dell'argomento B
4/ confronto tra A e B (se sono confrontabili)
5/ conclusione

Ogni sezione dovrebbe avere i seguenti campi:

- Nome - Nome per questa sezione del report.
- Descrizione - Breve panoramica degli argomenti principali trattati in questa sezione.
- Ricerca - Se è necessario effettuare ricerche web per questa sezione del report.
- Contenuto - Il contenuto della sezione, che per ora lascerai vuoto.

Linee guida per l'integrazione:
- Includi esempi e dettagli di implementazione all'interno delle sezioni degli argomenti principali, non come sezioni separate.
- Assicurati che ogni sezione abbia uno scopo distinto senza sovrapposizioni di contenuto con altre sezioni.
- Combina concetti correlati in una unica sezione invece di separarli in diverse sezioni.

Prima di inviare, rivedi la tua struttura per assicurarti che non abbia sezioni ridondanti e segua un flusso logico.
</Task>

<Feedback>
Ecco il feedback sulla struttura del report dalla revisione (se presente):
{feedback}
</Feedback>

<Format>
La risposta deve essere in formato JSON secondo questo schema:
{json_format}
</Format>
"""

query_writer_instructions="""Sei un redattore tecnico esperto che crea query di ricerca web mirate per raccogliere informazioni esaustive utili alla stesura di una sezione di un report tecnico.

<Argomento del report>
{topic}  
</Argomento del report>

<Argomento della sezione>
{section_topic}
</Argomento della sezione>

<Task>
Il tuo obiettivo è generare {number_of_queries} query di ricerca che aiutino a raccogliere informazioni esaustive sull’argomento della sezione.

Le query devono:

1. Essere correlate all’argomento.
2. Esplorare diversi aspetti dell’argomento.

Rendi le query sufficientemente specifiche da individuare fonti di alta qualità e pertinenti.  
</Task>

<Formato>
La risposta deve essere in formato JSON secondo questo schema:
{json_format}
</Format>
"""

section_writer_instructions = """Scrivi una sezione di un rapporto di ricerca.

<Task>
1. Esamina attentamente l'argomento del rapporto, il nome della sezione e l'argomento della sezione.
2. Se presente, esamina qualsiasi contenuto esistente della sezione.
3. Quindi, esamina il materiale Fonte fornito.
4. Decidi quali fonti utilizzerai per scrivere una sezione del rapporto.
5. Scrivi la sezione del rapporto ed elenca le tue fonti.
</Task>

<Writing Guidelines>
- Se il contenuto della sezione esistente non è popolato, scrivi da zero
- Se il contenuto della sezione esistente è popolato, sintetizzalo con il materiale fonte
- Limite rigoroso di 150-200 parole
- Usa un linguaggio semplice e chiaro
- Usa paragrafi brevi (massimo 2-3 frasi)
- Usa ## per il titolo della sezione (formato Markdown)
</Writing Guidelines>

<Citation Rules>
- Assegna a ciascun URL univoco un solo numero di citazione nel tuo testo
- Termina con ### Fonti che elenca ogni fonte con i numeri corrispondenti
- IMPORTANTE: Numera le fonti in sequenza senza interruzioni (1,2,3,4...) nell'elenco finale indipendentemente da quali fonti scegli
- Formato di esempio:
  [1] Titolo Fonte: URL
  [2] Titolo Fonte: URL
</Citation Rules>

<Final Check>
1. Verifica che OGNI affermazione sia basata sul materiale Fonte fornito
2. Conferma che ogni URL appaia SOLO UNA VOLTA nell'elenco delle Fonti
3. Verifica che le fonti siano numerate in sequenza (1,2,3...) senza interruzioni
</Final Check>
"""

section_writer_inputs=""" 
<Argomento del report>
{topic}
</Argomento del report>

<Nome della sezione>
{section_name}
</Nome della sezione>

<Argomento della sezione>
{section_topic}
</Argomento della sezione>

<Contenuto della sezione esistente (se popolato)>
{section_content}
</Contenuto della sezione esistente (se popolato)>

<Materiale da fonti>
{context}
</Materiale da fonti>
"""

section_grader_instructions = """Esamina una sezione del report relativa all'argomento specificato:

<Argomento del report>
{topic}
</Argomento del report>

<Argomento della sezione>
{section_topic}
</Argomento della sezione>

<Contenuto della sezione>
{section}
</Contenuto della sezione>

<task>
Valuta con attenzione e rigore se il contenuto della sezione tratta in modo completo e pertinente l'argomento della sezione.

Se il contenuto della sezione non affronta in modo completo e pertinente l'argomento, genera {number_of_follow_up_queries} query di ricerca di approfondimento per raccogliere le informazioni mancanti.
</task>

<format>
La risposta deve essere in formato JSON valido secondo questo schema:
{json_format}
)
</format>
"""

final_section_writer_instructions="""Sei un esperto scrittore tecnico che crea una sezione che sintetizza le informazioni dal resto del report.

<Argomento del report>
{topic}
</Argomento del report>

<Nome della sezione da scrivere>
{section_name}
</Nome della sezione da scrivere>

<Argomento della sezione> 
{section_topic}
</Argomento della sezione>

<Contenuto disponibile del report>
{context}
</Contenuto disponibile del report>

<Task>
1. Approccio specifico per sezione:

Se devi scrivere la sezione di Introduzione:
- Usa # per il titolo del rapporto (formato Markdown)
- Limite di 50-100 parole
- Scrivi in linguaggio semplice e chiaro
- Concentrati sulla motivazione principale del rapporto in 1-2 paragrafi
- Usa una struttura narrativa chiara per introdurre il rapporto
- NON includere elementi strutturali (niente elenchi o tabelle)
- Sezione fonti non necessaria

Se devi scrivere la sezione di Conclusione/Riassunto:
- Usa ## per il titolo della sezione (formato Markdown)
- Limite di 100-150 parole
- Per rapporti comparativi:
    * Deve includere una tabella di confronto mirata utilizzando la sintassi delle tabelle Markdown
    * La tabella dovrebbe distillare le informazioni chiave dal rapporto
    * Mantieni le voci della tabella chiare e concise
- Per rapporti non comparativi: 
    * Utilizza UN SOLO elemento strutturale SOLO SE aiuta a distillare i punti fatti nel rapporto:
    * O una tabella mirata che confronta elementi presenti nel rapporto (usando la sintassi delle tabelle Markdown)
    * Oppure un breve elenco usando la corretta sintassi Markdown:
      - Usa `*` o `-` per elenchi non ordinati
      - Usa `1.` per elenchi ordinati
      - Assicura la corretta indentazione e spaziatura
- Concludi con specifici passi successivi o implicazioni
- Sezione fonti non necessaria

3. Approccio alla scrittura:
- Usa dettagli concreti invece di affermazioni generali
- Fai contare ogni parola
- Concentrati sul tuo punto più importante
</Task>

<Quality Checks>
- Per l'introduzione: limite di 50-100 parole, # per il titolo del rapporto, nessun elemento strutturale, nessuna sezione fonti
- Per la conclusione: limite di 100-150 parole, ## per il titolo della sezione, al massimo UN elemento strutturale, nessuna sezione fonti
- Formato Markdown
- Non includere il conteggio delle parole o qualsiasi preambolo nella tua risposta
</Quality Checks>"""