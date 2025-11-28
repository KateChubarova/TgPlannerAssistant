location_tool = {
    "type": "function",
    "function": {
        "name": "enrich_event_by_location",
        "description": (
            "Получает дополнительную информацию о месте события по строке локации "
            "(адрес, название заведения и т.п.). "
            "Используй только когда нужно уточнить детали места встречи."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Локация события из календаря: адрес или название места."
                }
            },
            "required": ["location"],
        },
    },
}