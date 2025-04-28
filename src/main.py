from chief_deep_report_agent import ChiefDeepReportAgent

from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    deep_report = ChiefDeepReportAgent(
        # sites_search_restriction=["biblus.acca.it", "puntosicuro.it"]
    )
    # res = deep_report.invoke("ultimi aggiornamenti della valutazione rischio chimico MoVaRisCh")

    # res = deep_report.invoke("cosa c'è da visitare ad Ancona")
    # res = deep_report.invoke("ultimi aggiornamenti su formazione sicurezza lavoro accordo stato regioni")
    res = deep_report.invoke("Decreto legge 11/04/2025, n. 48")
    print(res)

    with open("final_report.md", "w", encoding="utf-8") as md_file:
        md_file.write(res['final_report'])

    print("**** DONE ****")
