from langchain_core.runnables import RunnableConfig

from chief_deep_report_agent import ChiefDeepReportAgent
from deep_report_state import DeepReportState
import time

from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':

    deep_report = ChiefDeepReportAgent()
    res = deep_report.invoke("economia città di Ancona")
    print(res)