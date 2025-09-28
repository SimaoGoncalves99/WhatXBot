from fastapi import FastAPI
from fastapi.responses import FileResponse
from typing import Union, Optional, Dict
import logging
import os
import tweepy
from duckduckgo_search import DDGS
from api.utils.messages import (
    fetch_baller_name,
    fetch_baller_image,
    BEARER_TOKEN,
    logger,
)
import tempfile
import pywhatkit
from datetime import datetime, timedelta


# Twitter client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

GROUP_ID = os.environ.get("GROUP_ID", "")


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/baller/")
async def baller_name() -> Dict[str, str]:

    # Fetch the most recent tweet of user x_user_id
    tweet = await fetch_baller_name()

    logger.info(f"Found baller: {tweet}")

    result = {"baller": tweet}

    return result


@app.get("/baller/{baller_name}")
async def baller_image(baller_name: str):

    image_bytes = await fetch_baller_image(baller_name)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg")
    tmp_file.write(image_bytes)
    tmp_file.close()
    return FileResponse(tmp_file.name, media_type="image/jpeg")


@app.post("share_baller/{phone_number}")
async def send_baller_to_group(phone_number: str):
    baller_name = await fetch_baller_name()
    if not baller_name:
        return {"error": "No baller found"}

    image_bytes = await fetch_baller_image(baller_name)

    # Current time + 1 minute
    now = datetime.now() + timedelta(minutes=1)

    # Send to WhatsApp group (example using your bot)
    pywhatkit.sendwhatmsg_to_group(
        GROUP_ID,
        "test message",
        time_hour=now.hour,
        time_min=now.minute,
    )

    return {"status": "sent", "baller": baller_name}


if __name__ == "__main__":

    # Current time + 1 minute
    now = datetime.now() + timedelta(minutes=1)

    pywhatkit.sendwhatmsg_to_group(
        GROUP_ID,
        "Hey! This is a test message, please ignore it.",
        time_hour=now.hour,
        time_min=now.minute,
    )
