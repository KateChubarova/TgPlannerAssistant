from threading import Thread

import uvicorn

from client.telegram.bot import run
from server.server import app


def main():
    bot_thread = Thread(target=run, daemon=True)
    bot_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8020)


if __name__ == "__main__":
    main()
