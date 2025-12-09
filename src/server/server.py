from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

from shared.storage.users_repo import get_user, save_tokens
from sources.google_calendar.google_auth import exchange_code_for_tokens

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """
    Return the basic health status of the FastAPI service.

    This endpoint is used to verify that the API is running and responding
    correctly by returning a simple JSON payload.

    Return:
        dict: A dictionary containing a status flag and a message confirming
            that the FastAPI server is operational.
    """
    return {"status": "ok", "message": "FastAPI works!"}


@app.get("/google/oauth2callback", response_class=HTMLResponse)
async def google_oauth_callback(request: Request) -> HTMLResponse:
    """
    Handle the OAuth2 callback from Google after user authentication.

    This endpoint processes the query parameters returned by Google, validates
    the OAuth2 state, exchanges the authorization code for access and refresh
    tokens, and saves them for the corresponding user.

    Args:
        request (Request): The FastAPI request object containing the query
            parameters returned by Google's OAuth2 redirect.

    Return:
        HTMLResponse: An HTML response indicating whether the authentication
            process was successful or failed due to an error.
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

    user = get_user(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="No user")

    creds = exchange_code_for_tokens(code=code, state=state)
    save_tokens(user_id, creds.token, creds.refresh_token, creds.expiry)

    return HTMLResponse(
        "Authentication success. Go to Telegram app and use /sync",
        status_code=200,
    )
