from datetime import datetime

from langsmith import Client
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

from rag.service import answer_with_rag
from shared.models.embedding import Embedding
from shared.models.user import TgUser

ls_client = Client()

rows = [
    Embedding(
        id="1",
        event_id="evt_123",
        participants=["kate", "team"],
        combined_text="Митинг с командой в 10:00",
        updated_at=datetime.now(),
        message=[0.1, 0.2, 0.3],
        location="офис",
        start_ts=None,
        end_ts=None,
        user_id=999999,
        updated=datetime.now(),
        organizer_email="teamlead@company.com",
        organizer_display_name="Team Lead",
    ),
    Embedding(
        id="2",
        event_id="evt_456",
        participants=["kate", "anton"],
        combined_text="Обед с Антоном в 13:00",
        updated_at=datetime.now(),
        message=[0.4, 0.5, 0.6],
        location="кафе",
        start_ts=None,
        end_ts=None,
        user_id=999999,
        updated=datetime.now(),
        organizer_email="anton@example.com",
        organizer_display_name="Anton",
    ),
]


def fake_embed_fn(_query: str):
    return [0.0, 0.1, 0.2]


def fake_search_fn(_user, _query_embedding, top_k: int = 5):
    return rows


def target(inputs: dict) -> dict:
    fake_user = TgUser(
        id=999999,
        username="test_user",
    )

    answer = answer_with_rag(
        user=fake_user,
        user_query=inputs["question"],
        embed_fn=fake_embed_fn,
        search_fn=fake_search_fn,
    )
    return {"answer": answer or ""}


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        model="openai:o3-mini",
        feedback_key="correctness",
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs,
    )
    return eval_result


experiment_results = ls_client.evaluate(
    target,
    data="events_from_calendar_rus1",
    evaluators=[correctness_evaluator],
    experiment_prefix="test-rag",
    max_concurrency=2,
)
