from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse

from ingest.providers.google_auth import exchange_code_for_tokens
from shared.db import SessionLocal
from shared.storage.users_repo import save_tokens, get_user

app = FastAPI()


@app.get("/")
def read_root():
    """
    Корневой эндпоинт для проверки работоспособности сервера.
    """
    return {"status": "ok", "message": "FastAPI works!"}


@app.get("/google/oauth2callback", response_class=HTMLResponse)
async def google_oauth_callback(request: Request):
    """
    Обрабатывает OAuth2 callback от Google после авторизации пользователя.
    Выполняет:
    - проверку наличия ошибок,
    - извлечение кода авторизации и состояния (state),
    - проверку корректности user_id,
    - обмен authorization code на токены,
    - сохранение токенов для пользователя.
    """

    params = request.query_params

    if "error" in params:
        error = params["error"]
        return HTMLResponse(
            f"Authentication error:{error}",
            status_code=400,
        )

    code = params.get("code")
    state = params.get("state")

    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Incorrect 'state'")

    with SessionLocal() as session:
        user = get_user(session, user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="No user")

        creds = exchange_code_for_tokens(code=code, state=state)
        save_tokens(user_id, creds.token, creds.refresh_token, creds.expiry)

    return HTMLResponse(
        "Authentication success. Go to Telegram app and use /sync",
        status_code=200,
    )
