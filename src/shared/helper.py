def get_message(inserted: int, updated: int, deleted: int) -> str:
    """
    Build a summary message for calendar synchronization results.

    This function formats a human-readable text message that reports how many
    calendar events were inserted, updated, or deleted during a synchronization
    operation.

    Args:
        inserted (int): Number of newly added calendar events.
        updated (int): Number of events that were modified.
        deleted (int): Number of events that were removed.

    Return:
        str: A formatted message summarizing the synchronization results.
    """
    message = "Готово! ✨ Я синхронизировал твой календарь:\n"

    if inserted > 0:
        message += f"• ➕ Добавил: {inserted}\n"

    if updated > 0:
        message += f"• 🔄 Обновил: {updated}\n"

    if deleted > 0:
        message += f"• ➖ Убрал: {deleted}\n"

    if inserted == 0 and updated == 0 and deleted == 0:
        message += "✨ Никаких изменений не было — всё уже актуально!\n"

    return message