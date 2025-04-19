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

<Argomento del report>
L'argomento del report è:
{topic}
</Argomento del report>

<Organizzazione del report>
Il report dovrebbe seguire questa organizzazione: 
{report_organization}
</Organizzazione del report>

<Contesto>
Ecco il contesto da utilizzare per pianificare le sezioni del report: 
{context}
</Contesto>

<Task>
Genera un elenco di sezioni per il report. Il tuo piano deve essere essenziale e mirato SENZA sezioni sovrapposte o contenuti superflui.

Ad esempio, una buona struttura di report potrebbe essere:
1/ introduzione
2/ panoramica dell'argomento A
3/ panoramica dell'argomento B
4/ confronto tra A e B
5/ conclusione

Ogni sezione dovrebbe avere i seguenti campi:

- Nome - Nome per questa sezione del report.
- Descrizione - Breve panoramica degli argomenti principali trattati in questa sezione.
- Ricerca - Se è necessario effettuare ricerche web per questa sezione del report.
- Contenuto - Il contenuto della sezione, che per ora lascerai vuoto.

Linee guida per l'integrazione:
- Includi esempi e dettagli di implementazione all'interno delle sezioni degli argomenti principali, non come sezioni separate
- Assicurati che ogni sezione abbia uno scopo distinto senza sovrapposizioni di contenuto
- Combina concetti correlati invece di separarli

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

query_writer_instructions="""Sei un redattore tecnico esperto che crea query di ricerca web mirate per raccogliere informazioni esaustive utili alla stesura di una sezione di documento tecnico.

<Argomento del documento>  
{topic}  
</Argomento del documento>

<Argomento della sezione> 
{section_topic}
</Argomento della sezione>

<Task>
Il tuo obiettivo è generare {number_of_queries} query di ricerca che aiutino a raccogliere informazioni esaustive sull’argomento della sezione.

Le query devono:

1. Essere correlate all’argomento  
2. Esplorare diversi aspetti dell’argomento

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
<Report topic>
{topic}
</Report topic>

<Section name>
{section_name}
</Section name>

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Source material>
{context}
</Source material>
"""

section_grader_instructions = """Esamina una sezione del rapporto relativa all'argomento specificato:

<Report topic>
{topic}
</Report topic>

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
Valuta con attenzione e rigore se il contenuto della sezione  tratta in modo completo e pertinente l'argomento della sezione.

Se il contenuto della sezione non affronta in modo completo e pertinente l'argomento, genera {number_of_follow_up_queries} query di ricerca di approfondimento per raccogliere le informazioni mancanti.
</task>

<format>
La risposta deve essere in formato JSON valido secondo questo schema:
{json_format}
)
</format>
"""

final_section_writer_instructions="""You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

<Report topic>
{topic}
</Report topic>

<Section name>
{section_name}
</Section name>

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 50-100 word limit
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 100-150 word limit
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports: 
    * Only use ONE structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
- Focus on your single most important point
</Task>

<Quality Checks>
- For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
- For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
- Markdown format
- Do not include word count or any preamble in your response
</Quality Checks>"""