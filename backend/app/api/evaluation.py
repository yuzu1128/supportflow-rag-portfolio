from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore
from app.evaluation.runner import run_evaluation
from app.schemas import EvaluationRunRequest, EvaluationRunResponse


router = APIRouter()


@router.post("/run", response_model=EvaluationRunResponse)
def run(request: EvaluationRunRequest, store: SQLiteStore = Depends(get_store)) -> dict:
    settings = get_settings()
    result = run_evaluation(settings, store, k=request.k)
    saved = store.add_evaluation_run(name=request.name, metrics=result["metrics"])
    return {
        "id": saved["id"],
        "name": request.name,
        **result,
    }


@router.get("/runs")
def runs(store: SQLiteStore = Depends(get_store)) -> dict:
    return {"runs": store.list_evaluation_runs()}
