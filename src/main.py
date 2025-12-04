from threading import Thread

import uvicorn

from client.telegram.bot import run
from server.server import app
from shared.storage.db import Base, engine


def main():
    Base.metadata.create_all(bind=engine)
    bot_thread = Thread(target=run, daemon=True)
    bot_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
