def get_message(inserted: int, updated: int, deleted: int) -> str:
    message = "Готово! ✨ Я синхронизировал твой календарь:\n"

    if inserted > 0:
        message += f"• ➕ Добавил: {inserted}\n"

    if updated > 0:
        message += f"• 🔄 Обновил: {updated}\n"

    if deleted > 0:
        message += f"• ➖ Убрал: {deleted}\n"

    return message
