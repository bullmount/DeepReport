from chief_deep_report_agent import ChiefDeepReportAgent

from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':

    deep_report = ChiefDeepReportAgent()
    # res = deep_report.invoke("ultimi aggiornamenti nella valutazione rischio chimico MoVaRisCh")
    res = deep_report.invoke("turismo ad Ancona")
    print(res)

    with open("final_report.md", "w", encoding="utf-8") as md_file:
        md_file.write(res['final_report'])

    print("**** DONE ****")