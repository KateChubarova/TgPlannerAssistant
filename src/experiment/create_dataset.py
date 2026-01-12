from langsmith import Client

from experiment.event_experiment import ls_client

client = Client()

dataset = ls_client.create_dataset(
    dataset_name="events_from_calendar_rus1",
    description="Simple events from calendar",
)

examples = [
    {
        "inputs": {"question": "Что у меня завтра?"},
        "outputs": {
            "answer": "У тебя встреча с командой в 10:00 и обед с Антоном в 13:00."
        },
    },
    {
        "inputs": {"question": "Во сколько у меня обед?"},
        "outputs": {"answer": "Твой обед с Антоном в 13:00."},
    },
]

client.create_examples(dataset_id=dataset.id, examples=examples)
