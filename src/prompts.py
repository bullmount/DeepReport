report_planner_query_writer_instructions="""Stai svolgendo una ricerca con l’obiettivo di redigere un report aggiornato e approfondito su un determinato argomento.

# CONTESTO
Data attuale: {current_date}

# ARGOMENTO DEL REPORT
{topic}

## Queste sono le prime informazioni raccolte sull’argomento:
{starting_knowledge}

# OBIETTIVO
Il tuo compito è generare {number_of_queries} query di ricerca web che ti permettano di raccogliere informazioni dettagliate, aggiornate e affidabili utili alla stesura del report.

Le query devono:
1. Essere strettamente correlate all’argomento.
2. Aiutare a identificare e comprendere le principali tematiche che andranno affrontate nel report.
3. Essere complementari tra loro, in modo da offrire una visione completa e sfaccettata dell’argomento.

Cerca di formulare query specifiche e mirate, che possano restituire fonti autorevoli e pertinenti attraverso i motori di ricerca. L'obiettivo è coprire l'argomento in modo esaustivo, evitando ridondanze e massimizzando il valore informativo di ogni ricerca.

# FORMATO
La risposta deve essere in formato JSON valido, seguendo lo schema seguente:
{json_format}
"""

report_planner_query_writer_with_feedback_instructions="""Stai svolgendo una ricerca per finalizzare un report aggiornato e approfondito su un determinato argomento.

# CONTESTO
Data attuale: {current_date}

# ARGOMENTO DEL REPORT
{topic}

## Queste sono le prime informazioni raccolte sull’argomento:
{starting_knowledge}

## STRUTTURA PROPOSTA DEL REPORT
Questa è la struttura iniziale delle sezioni prevista:
{proposed_structure}

# OBIETTIVO
Il tuo compito è generare {number_of_queries} query di ricerca web che ti permettano di:
- Approfondire i contenuti richiesti dalla struttura proposta.
- Integrare o modificare la struttura in base ai feedback ricevuti.
- Raccogliere informazioni dettagliate, aggiornate e affidabili per migliorare la qualità complessiva del report.

Le query devono:
1. Essere strettamente correlate all’argomento e al miglioramento della struttura.
2. Concentrarsi sia sulla validazione delle sezioni esistenti, sia sull’approfondimento o aggiunta di temi suggeriti dal feedback.
3. Essere complementari tra loro, evitando sovrapposizioni.

Cerca di formulare query specifiche e mirate, che restituiscano fonti autorevoli e pertinenti attraverso i motori di ricerca.

# FORMATO
La risposta deve essere in formato JSON valido, seguendo lo schema seguente:
{json_format}
"""

report_planner_instructions_initial="""# ISTRUZIONI GENERALI
Il tuo compito è analizzare un argomento e produrre un piano dettagliato per la redazione di un report chiaro, conciso e completo. La struttura deve includere: 

1. Un elenco delle **principali tematiche** da trattare.
2. La suddivisione del report in **sezioni logiche e distinte**, senza sovrapposizioni.

---

## DATI DI INGRESSO

### Argomento del report:
{topic}

### Struttura suggerita (facoltativa):
Il report potrebbe seguire un'organizzazione simile alla seguente:
{report_organization}

### Contesto fornito:
{context}

---

## FASE 1 – ELENCO DELLE TEMATICHE PRINCIPALI

Analizza l’argomento e identifica le **tematiche fondamentali** da trattare nel report. Questo elenco serve come base per organizzare in modo logico e completo le sezioni successive.

Per ogni tematica, includi:
- **Titolo**: un nome sintetico della tematica.
- **Descrizione**: una breve spiegazione del contenuto o del motivo per cui è rilevante.

### Indicazioni specifiche se l'argomento è di natura tecnico/legale:
- Includi riferimenti a normative, leggi, regolamenti, direttive (es. ISO, UNI, D.Lgs, Regolamenti UE).
- Considera anche standard tecnici, linee guida, giurisprudenza, prassi operative, implicazioni applicative.


## FASE 2 – SEZIONI DEL REPORT
Sulla base delle tematiche individuate, definisci la suddivisione del report in **sezioni distinte**, evitando sovrapposizioni o ripetizioni.
Ogni sezione deve avere uno scopo preciso, senza sovrapposizioni o contenuti ridondanti.

Una buona struttura, ad esempio, potrebbe includere:
1. Introduzione generale
2. Panoramica dell'argomento A
3. Panoramica dell'argomento B
4. Confronto tra A e B (se rilevante)
5. Conclusioni

Ogni sezione deve contenere i seguenti campi:
- **Nome**: il titolo della sezione.
- **Descrizione**: una breve panoramica dei temi principali trattati nella sezione.
- **Ricerca**: indica se è necessaria un’ulteriore ricerca web per completare la sezione.
- **Contenuto**: lascia sempre questo campo vuoto per ora; sarà riempito in seguito.
- **Tipo**: tipo di sezione; uno tra questi valori: "introduzione", "conclusioni", "confronto" o "standard".
---

## LINEE GUIDA PER LA GENERAZIONE
- Le sezioni devono essere strettamente correlate alle tematiche identificate nella fase 1.
- Inserisci esempi e dettagli pratici direttamente all'interno delle sezioni rilevanti, evitando sezioni separate solo per esempi.
- Evita contenuti duplicati: ogni sezione deve trattare aspetti unici.
- Unifica concetti affini in un’unica sezione, dove possibile.
- Verifica che tutte le aree chiave indicate nel contesto siano rappresentate.
- Rivedi la struttura per assicurarti che segua un flusso logico e progressivo.
- **non compilare** il contenuto della sezione.

# FORMATO
La risposta deve essere in formato JSON valido, seguendo lo schema seguente:
{json_format}
"""

report_planner_instructions_with_feedback_and_additional_section="""# ISTRUZIONI GENERALI
Il tuo compito è analizzare un argomento e produrre un piano dettagliato per la redazione di un report chiaro, conciso e completo.  
La struttura deve includere:

1. Un elenco delle **principali tematiche** da trattare.
2. La suddivisione del report in **sezioni logiche e distinte**, senza sovrapposizioni.
3. L’integrazione di una **nuova sezione proposta** e il recepimento del **feedback** ricevuto su una bozza precedente.

---

## DATI DI INGRESSO

### Argomento del report:
{topic}

### Struttura suggerita (iniziale):
La proposta precedente delle sezioni è la seguente:
{report_organization}

### Feedback dell’utente:
Questi sono i commenti e le osservazioni forniti sulla struttura proposta:
{user_feedback}

### Contesto aggiuntivo:
{context}

---

## FASE 1 – ELENCO DELLE TEMATICHE PRINCIPALI

Analizza l’argomento considerando anche la nuova sezione proposta e il feedback ricevuto.  
Identifica le **tematiche fondamentali** da trattare nel report.  
Per ogni tematica, includi:
- **Titolo**: nome sintetico della tematica.
- **Descrizione**: breve spiegazione del contenuto o della sua rilevanza.

Indicazioni particolari se l’argomento è tecnico/legale:
- Considera norme, leggi, direttive, standard tecnici e buone pratiche operative.

## FASE 2 – SEZIONI DEL REPORT

Sulla base delle tematiche identificate, definisci la suddivisione in **sezioni distinte**, considerando anche:
- L'inserimento della nuova sezione proposta.
- Le modifiche o aggiunte suggerite dal feedback.

Ogni sezione deve avere i seguenti campi:
- **Nome**: il titolo della sezione.
- **Descrizione**: breve panoramica dei temi trattati nella sezione.
- **Ricerca**: specifica se è necessaria ulteriore ricerca web per completare la sezione.
- **Contenuto**: lascia questo campo vuoto per ora.
- **Tipo**: uno tra "introduzione", "conclusioni", "confronto" o "standard".

---

## LINEE GUIDA PER LA GENERAZIONE
- Rispetta le indicazioni fornite nella struttura iniziale, integrando però correttamente la nuova sezione e il feedback.
- Garantisci un flusso logico e progressivo delle sezioni.
- Evita sovrapposizioni o ripetizioni tra sezioni.
- Unifica temi simili quando opportuno.
- Inserisci esempi pratici e riferimenti normativi dove rilevanti.

# FORMATO
La risposta deve essere in formato JSON valido, seguendo questo schema:
{json_format}
"""

query_writer_instructions="""# OBIETTIVO
Il tuo compito è generare un insieme di query di ricerca web specifiche per raccogliere informazioni utili alla stesura di **una singola sezione** di un report informativo.

---

## CONTESTO GENERALE

- Il report è suddiviso in più sezioni, ciascuna con un proprio titolo e una descrizione.
- **Ogni sezione è assegnata a un soggetto diverso** (umano o sistema).
- Il tuo compito riguarda **solo la sezione che ti è stata affidata**.
- Le query che generi devono servire **esclusivamente per approfondire i contenuti di quella sezione**, evitando temi coperti da altre sezioni.

---

## DATI DISPONIBILI

### Titolo generale del report:
{topic}  

### Data corrente:
{current_date}

### Sezione assegnata a te:
- **Numero**: {section_number}
- **Titolo**: {section_title}
- **Descrizione**: {section_description}

### Altre sezioni del report (gestite da altri soggetti):
{other_sections}

---

## ISTRUZIONI PER LA GENERAZIONE DELLE QUERY

Genera da **{number_of_queries} query di ricerca web**, progettate per:
1. Approfondire tutti i contenuti rilevanti per la sezione assegnata.
2. Ottenere informazioni aggiornate, pertinenti e utili alla scrittura della sezione.
3. Evitare sovrapposizioni con le altre sezioni del report.

### Le query devono:
- Essere formulate in modo chiaro e specifico.
- Coprire aspetti diversi e complementari della sezione.
- Non essere troppo generiche né ripetitive.
- Puntare a raccogliere contenuti da fonti affidabili e pertinenti.
- Rispettare i confini tematici della sezione assegnata, lasciando agli altri soggetti il compito di trattare le rispettive aree.

---

## FORMATO DI USCITA

La risposta deve essere in **JSON valido**, rispettando il seguente schema:
{json_format}
"""

section_writer_instructions_initial = """Sei incaricato di scrivere il contenuto di **una specifica sezione** di un report strutturato.  
Il tuo obiettivo è produrre un testo chiaro, coerente e informativo, basato sui risultati di ricerca forniti, seguendo le istruzioni riportate qui sotto.
Non devi scrivere contenuti che sono attinenti ad altre sezioni che compongono il report. 

---

# CONTESTO DEL REPORT

## Titolo del report
{topic}

## Struttura completa del report
Le seguenti sezioni compongono l'intero report. Ogni sezione è assegnata a un writer diverso.  
Tu dovrai occuparti **solo della sezione indicata come "assegnata"**, evitando qualsiasi sovrapposizione con le altre.

{report_structure}

---

# SEZIONE ASSEGNATA

- **Numero sezione {section_number}**:    
- Titolo sezione: {section_title}  
- Descrizione sezione: {section_description}

---

# RISULTATI DI RICERCA

I seguenti risultati di ricerca sono stati raccolti per aiutarti a scrivere questa sezione.  
Sono numerati progressivamente a partire da 1.  
Durante la scrittura del testo, **cita le fonti utilizzate** usando il formato `[n]`, dove `n` è il numero assegnato alla fonte.

{search_results}

---

# ISTRUZIONI DI SCRITTURA

Scrivi il contenuto completo della sezione assegnata, tenendo conto delle seguenti linee guida:

1. **Leggi attentamente i risultati di ricerca** e seleziona le informazioni più rilevanti per la sezione.
2. **Riformula tutto con parole tue.** Non copiare testo dalle fonti, e fai un lavoro di sintesi.
3. **Inserisci le citazioni nel formato `[n]`** ogni volta che riporti un’informazione basata su una fonte, dove n è il numero assegnato alla fonte.
   - Se più fonti supportano la stessa informazione metti le fonti una dopo altra come esempio: `[2][4][5]`
4. **Non scrivere l'elenco delle fonti.** Le uniche citazioni devono essere inline nel testo.
5. **Non trattare argomenti di competenza di altre sezioni.**
6. Organizza il testo in paragrafi ben strutturati, con una scrittura scorrevole, informativa ed efficace.
7. Il testo prodotto deve essere **in formato markdown** e pronto per l’inserimento nel report finale.
8. **Non includere spiegazioni, introduzioni generali, né conclusioni del report.** Scrivi solo il contenuto della sezione assegnata.
9. Il testo deve essere in una forma immediata da leggere ricorrendo anche ad elenchi puntati.
10. Dare priorità i risultati riportati per primi, in quanto sono riportati in elenco in ordine di priorità.
11. Ogni sezione inizia con il titolo della sezione con titolo a primo livello (es. # Titolo della sezione)

---

# OUTPUT ATTESO

Fornisci **solo il testo completo della sezione assegnata**, in markdown, con eventuali citazioni nel formato `[n]`.  
Non includere altro.
"""

section_writer_instructions_review = """Sei incaricato di **migliorare e integrare** una specifica sezione a te assegnata già esistente di un report composto da più sezioni, sfruttando nuove fonti di ricerca.
Il tuo compito è aggiornare e arricchire il testo esistente in modo coerente, fluido e strutturato, mantenendo intatte le citazioni precedenti e integrando nuove informazioni dove rilevante.  
Non scrivere contenuti che rientrano nella trattazione di altre sezioni, perchè devi restare sul tema della sezione assegnata ed il report non deve avere ripetizioni tra le sezioni. 
Devi scartare le informazioni che non sono strettamente pertinenti all'argomento della sezione assegnata, o che sono correlate ad altre sezioni.

Alla fine, dovrai anche **esprimere un giudizio** sull’effettiva crescita informativa del contenuto, e decidere se è necessario proseguire con ulteriori ricerche.

---

# CONTESTO DEL REPORT

## Titolo del report:
{topic}

## Struttura del report:
Queste sono le sezioni che compongono tutto il report:

{report_structure}

Ogni sezione è assegnata a un writer diverso.

## Sezione assegnata di tua competenza:
 A te è assegnata la sezione numero {section_number} indicata qui sotto.
- **Numero sezione {section_number}** 
- Titolo: {section_title}
- Descrizione: {section_description}

---

# VERSIONE ATTUALE DELLA SEZIONE

Di seguito trovi la versione redatta nella fase precedente della sezione a te assegnata.  
Questo testo include citazioni nel formato `[n]`, dove `n` si riferisce alle fonti usate nella prima fase.  
**Queste citazioni devono essere mantenute intatte e non modificate.**

{section_content}

---

# NUOVE FONTI DISPONIBILI

Hai a disposizione nuove fonti di ricerca, numerate **a partire da un numero successivo rispetto alle fonti precedenti** (es. dalla {numero_prima_fonte} in poi).  
Usa le fonti solo se servono per **migliorare, estendere o integrare** il contenuto della sezione assegnata.
Non andare fuori tema, non scrivere informazioni che saranno trattate in altre sezioni, e scarta le fonti che non contengono informazioni strettamente legate alla sezione assegnata.

{new_sources}

---

# QUERY GIÀ UTILIZZATE IN PRECEDENZA

Sono state già utilizzate le seguenti query nella fase precedente.
**Non devi in alcun modo riproporre, parafrasare o generare varianti analoghe** a queste:

{previous_queries_list}

---

# ISTRUZIONI PER IL MIGLIORAMENTO DEL CONTENUTO

1. **Analizza** il contenuto esistente e le nuove fonti disponibili.
2. Se una nuova fonte approfondisce qualcosa di già presente, **integra nel contenuto esistente**, aggiungendo le nuove citazioni con il numero assegnato alle nuove fonti.
3. Se una fonte introduce informazioni nuove, e se valuti che non è fuori tema per la sezione assegnata e non è corretta riportarla in altre sezioni, allora **aggiungi contenuti con una transizione fluida**, citando le fonti correlate.
4. **Mantieni tutte le citazioni esistenti** che sono nel formato `[n]`, e **non modificarle o rimuoverle**.
5. In caso di più citazioni metterle una dopo l'altra come in esempio: [2][5][6]
6. Il testo prodotto deve essere **in formato markdown** e pronto per l’inserimento nel report finale.
7. **Non includere spiegazioni, introduzioni generali, né conclusioni del report.** Scrivi solo il contenuto della sezione assegnata.
8. Il testo deve essere in una forma immediata da leggere ricorrendo anche ad elenchi puntati.
9. Dare priorità ai risultati riportati per primi, in quanto sono riportati in elenco in ordine di priorità.

---

# VALUTAZIONE DEL BISOGNO DI ULTERIORI RICERCHE

Dopo aver prodotto il testo aggiornato, valuta in modo esigente e rigoroso se il contenuto è significativamente migliorato e non è andato fuori tema.

- Se le nuove fonti **hanno apportato un valore informativo veramente importante in relazione all'argomento primario della sezione assegnata**, scrivi `"RESEARCH"` e **genera {number_of_followup_queries} ulteriori query** per cercare nuove fonti che possano ulteriormente arricchire o approfondire la sezione.
- Se invece **le integrazioni effettuate sono marginali o non tanto ben focalizzate all'argomento della sezione**, scrivi `"PASS"` e **non fornire altre query**.

---

# OUTPUT ATTESO

Restituisci una struttura JSON valido nel seguente formato descritto da questo schema:
{json_format}
"""
# ```json
# {
#   "new_section_content": "Testo completo della sezione in formato markdown con tutte le citazioni.",
#   "grade": "RESEARCH" | "PASS",
#   "follow_up_queries": [
#     "nuova query (solo se giudizio è RESEARCH)",
#     "..."
#   ]
# }


section_grader_instructions_initial = """# OBIETTIVO
Il tuo compito è generare nuove query di ricerca web per approfondire e migliorare il contenuto di **una sezione specifica** di un report, già redatta in una prima versione.
Le nuove query serviranno a raccogliere informazioni aggiuntive e complementari che saranno utilizzate per produrre una **seconda versione più completa, ricca e aggiornata** della sezione.

---

## CONTESTO DEL REPORT

### Titolo del report:
{topic}

### Struttura completa del report:
Ogni sezione è curata da un soggetto diverso. Tu sei incaricato solo della sezione indicata qui sotto.

{report_structure}

### Sezione assegnata:
- **Numero**: {section_number} / {total_sections}
- **Titolo**: {section_title}
- **Descrizione**: {section_description}

---

## CONTENUTO ATTUALE DELLA SEZIONE

Questa è la versione attuale del testo, scritta in una prima fase:

{section_content}

---

## QUERY GIÀ UTILIZZATE IN PRECEDENZA

Le seguenti query sono già state impiegate per raccogliere i contenuti della prima versione.  
**Non devi in alcun modo riproporre, parafrasare o generare varianti analoghe** a queste query:

{previous_queries_list}

---

## OBIETTIVO DELLE NUOVE QUERY

Genera **{number_of_queries} query di ricerca web**, progettate per:

1. Ampliare o approfondire aspetti toccati nel testo attuale.
2. Colmare eventuali mancanze o aree non esplorate.
3. Trovare dati aggiornati, esempi migliori, evidenze empiriche, fonti autorevoli o prospettive alternative.
4. Esplorare **solo contenuti coerenti con la sezione assegnata**, senza sconfinare nei temi di altre sezioni.

---

## ISTRUZIONI

- Le query devono essere **nuove, originali, specifiche e rilevanti** per il miglioramento della sezione assegnata.
- Devono essere formulate in modo chiaro ed efficiente per l’uso su motori di ricerca.
- Ogni query deve esplorare un aspetto diverso e contribuire a rafforzare il contenuto.
- **Non generare query uguali** a quelle già utilizzate.
- Evita qualsiasi sovrapposizione con i contenuti delle altre sezioni del report.

---

## FORMATO DI USCITA

Fornisci la risposta in **JSON valido**, rispettando il seguente schema:
{json_format}
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

2. Approccio alla scrittura:
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


final_report_writer_instructions="""Ricevi in input un report in formato Markdown, suddiviso in sezioni, e contenente citazioni indicate come [n], dove n è il numero della fonte.
Il tuo obiettivo è generare una revisione del report di qualità superiore a quella data in quanto **evita ripetizioni** sia tra sezioni che tra paragrafi e migliora la lettura fluida del testo.  

Segui queste regole:
- Riscrivere il report sezione per sezione, migliorando la chiarezza, la fluidità e l'organizzazione generale, mantenendo il formato Markdown.
- I titoli e i sottotitoli devono essere ben strutturati senza ripetizioni e, se necessario, migliorati per rendere il documento più ordinato e leggibile.
- Ogni sezione deve trattare esclusivamente l'argomento indicato dal suo titolo: se trovi contenuti che non sono pertinenti, spostali nella sezione più adatta.
- Se trovi paragrafi simili o sovrapposti in sezioni diverse, integra i contenuti ed elimina le ripetizioni, mantenendo tutte le informazioni importanti.
- Non devono andare perse informazioni presenti nel testo originale: riorganizza i contenuti ma assicurati che tutte le informazioni vengano mantenute.
- Riorganizza i paragrafi in modo che la lettura sia lineare, coerente e ben suddivisa, facilitando la comprensione del testo.
- Migliora i collegamenti logici tra le sezioni per garantire una transizione naturale e fluida da una sezione all'altra.
- Quando integri testi che contengono citazioni diverse, combina le citazioni tra parentesi quadrate, ad esempio: [2][4][5].
- Non aggiungere nuove fonti che non siano già presenti nel testo originale.
- Non cambiare il numero associato alle citazioni esistenti.
- Numera i titoli delle sezioni a partire da 1, e numera i sottotitoli nella forma 1.1, 1.2, 1.3, ...

Rispondi restituendo solo il nuovo testo revisionato in formato Markdown, senza commenti o spiegazioni aggiuntive.

Report da revisionare:
{report_text}
"""