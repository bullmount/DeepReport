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

query_writer_instructions="""You are an expert technical writer crafting targeted web search queries that will gather comprehensive information for writing a technical report section.

<Report topic>
{topic}
</Report topic>

<Section topic>
{section_topic}
</Section topic>

<Task>
Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information above the section topic. 

The queries should:

1. Be related to the topic 
2. Examine different aspects of the topic

Make the queries specific enough to find high-quality, relevant sources.
</Task>

<Format>
Call the Queries tool 
</Format>
"""

section_writer_instructions = """Write one section of a research report.

<Task>
1. Review the report topic, section name, and section topic carefully.
2. If present, review any existing section content. 
3. Then, look at the provided Source material.
4. Decide the sources that you will use it to write a report section.
5. Write the report section and list your sources. 
</Task>

<Writing Guidelines>
- If existing section content is not populated, write from scratch
- If existing section content is populated, synthesize it with the source material
- Strict 150-200 word limit
- Use simple, clear language
- Use short paragraphs (2-3 sentences max)
- Use ## for section title (Markdown format)
</Writing Guidelines>

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
</Citation Rules>

<Final Check>
1. Verify that EVERY claim is grounded in the provided Source material
2. Confirm each URL appears ONLY ONCE in the Source list
3. Verify that sources are numbered sequentially (1,2,3...) without any gaps
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

section_grader_instructions = """Review a report section relative to the specified topic:

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
Evaluate whether the section content adequately addresses the section topic.

If the section content does not adequately address the section topic, generate {number_of_follow_up_queries} follow-up search queries to gather missing information.
</task>

<format>
Call the Feedback tool and output with the following schema:

grade: Literal["pass","fail"] = Field(
    description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
)
follow_up_queries: List[SearchQuery] = Field(
    description="List of follow-up search queries.",
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