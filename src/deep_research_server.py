from typing import Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

from api.requests_data import ResearchRequest, FeedbackRequest
from api.response_data import ResearchResponse, AbortResponse
from chief_deep_report_agent import ChiefDeepReportAgent

load_dotenv()

app = Flask(__name__)
CORS(app)  # abilita CORS per tutte le origini


class SessionState:
    def __init__(self):
        self.deep_report: Optional[ChiefDeepReportAgent] = None
        self.topic: Optional[str] = None


# si gestisce una sola sessione
_unique_session = SessionState()


@app.route("/", methods=["GET"])
def hello_world():
    # deep_report = ChiefDeepReportAgent()
    # res = deep_report.invoke("ultimi aggiornamenti su formazione sicurezza lavoro accordo stato regioni")
    return jsonify({"message": "Welcome to DeepReport API!"})


@app.route("/abort_report", methods=["POST"])
def abort_report():
    if _unique_session.deep_report is None:
        return jsonify(AbortResponse(
            success=False,
            message="Processo non trovato."
        ).model_dump())
    try:
        result: bool = _unique_session.deep_report.abort()
        if result:
            return jsonify(ResearchResponse(
                success=True,
                message=""
            ).model_dump())
        else:
            return jsonify(ResearchResponse(
                success=False,
                message="Operazione di abort non riuscita."
            ).model_dump())
    except Exception as e:
        _unique_session.deep_report = None
        _unique_session.topic = None
        return jsonify(ResearchResponse(
            success=False,
            message=f"Errore durante l'operazione di abort: {e}"
        ).model_dump())


@app.route("/feedback_plan", methods=["POST"])
def feedback_plan():
    if _unique_session.deep_report is None:
        return jsonify(ResearchResponse(
            success=False,
            message="Processo non trovato."
        ).model_dump())

    try:
        try:
            data = FeedbackRequest(**request.json)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": f"Errore di validazione: {e.errors()}"
            }), 400
        _unique_session.deep_report.plan_feedback(data.feedback)
        return jsonify(ResearchResponse(
            success=True,
            message=""
        ).model_dump())
    except Exception as e:
        _unique_session.deep_report = None
        _unique_session.topic = None
        return jsonify(ResearchResponse(
            success=False,
            message=f"Errore durante il feedback: {e}"
        ).model_dump())


@app.route("/approve_plan", methods=["POST"])
def approve_plan():
    if _unique_session.deep_report is None:
        return jsonify(ResearchResponse(
            success=False,
            message="Processo non trovato."
        ).model_dump())
    try:
        _unique_session.deep_report.approve()
        return jsonify(ResearchResponse(success=True, message="").model_dump())
    except Exception as e:
        _unique_session.deep_report = None
        _unique_session.topic = None
        return jsonify(
            ResearchResponse(success=False, message=f"Errore durante l'avvio della ricerca: {e}").model_dump())


@app.route("/deepresearch", methods=["POST"])
def deep_research():
    if _unique_session.deep_report is not None:
        if _unique_session.deep_report.is_running():
            return jsonify(ResearchResponse(
                success=False,
                message="Esiste ancora una ricerca in esecuzione, non posso avviara una ulteriore ricerca."
            ).model_dump())
    else:
        _unique_session.topic = None
        _unique_session.deep_report = None

    try:
        # Validazione JSON in ingresso con Pydantic
        try:
            data = ResearchRequest(**request.json)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "message": f"Errore di validazione: {e.errors()}"
            }), 400

        _unique_session.topic = data.topic
        _unique_session.deep_report = ChiefDeepReportAgent(
            number_of_queries=data.config.number_of_queries,
            max_search_depth=data.config.max_search_depth,
            max_results_per_query=data.config.max_results_per_query,
            search_api=data.config.search_api,
            fetch_full_page=data.config.fetch_full_page,
            domains_search_restriction=data.config.sites_search_restriction
        )
        _unique_session.deep_report.invoke(_unique_session.topic)

        return jsonify(ResearchResponse(
            success=True,
            topic=_unique_session.topic,
            message=""
        ).model_dump())
    except Exception as e:
        _unique_session.deep_report = None
        _unique_session.topic = None
        return jsonify(ResearchResponse(
            success=False,
            message=f"Errore durante l'avvio della ricerca: {e}"
        ).model_dump())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8123, debug=False)
