from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
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
from datetime import datetime, timedelta
import base64
from io import BytesIO
from fastapi.responses import JSONResponse
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import (
    Chrome as WebDriver,
)  # or use your custom WebDriver class
import os
import time
import uvicorn

import os

import os
import imghdr
from fastapi import FastAPI, HTTPException
import httpx
from typing import Optional

# Twitter client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

GROUP_ID = os.environ.get("GROUP_ID", "")


app = FastAPI()

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")

# Simple mapping from your route {group_name} -> Telegram chat_id.
# Either hardcode or set env vars like GROUP_CHAT_mygroup=-1001234567890
GROUP_CHAT_IDS = {"Teste123": int(os.environ.get("GROUP_ID", 0))}


async def send_photo_to_telegram(
    chat_id: int, image_bytes: bytes, caption: Optional[str] = None
):
    # detect basic type (jpeg/png/gif)
    img_type = imghdr.what(None, h=image_bytes)
    if img_type == "jpeg":
        ext = "jpg"
    elif img_type:
        ext = img_type
    else:
        ext = "jpg"  # fallback

    mime = f"image/{img_type or 'jpeg'}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {"photo": (f"image.{ext}", image_bytes, mime)}
    params = {"chat_id": chat_id}
    if caption:
        params["caption"] = caption  # type: ignore

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, params=params, files=files)
    try:
        data = resp.json()
    except Exception:
        raise HTTPException(
            status_code=502, detail=f"Telegram returned non-json: {resp.text}"
        )

    if not resp.is_success or not data.get("ok"):
        raise HTTPException(status_code=502, detail={"telegram_error": data})
    return data


@app.post("/share_baller/{group_name}")
async def send_baller_to_group(group_name: str):

    baller_name = await fetch_baller_name()

    if not baller_name:
        raise HTTPException(status_code=404, detail="No baller found")

    image_bytes = await fetch_baller_image(baller_name)
    if not image_bytes:
        raise HTTPException(
            status_code=404, detail="No image returned for baller"
        )

    # find chat_id from group_name
    chat_id = GROUP_CHAT_IDS.get(group_name.lower())
    if chat_id is None:
        raise HTTPException(
            status_code=400,
            detail="Unknown group_name. Add it to GROUP_CHAT_ env vars or GROUP_CHAT_IDS mapping.",
        )

    caption = f"{baller_name}"
    telegram_result = await send_photo_to_telegram(
        chat_id=chat_id, image_bytes=image_bytes, caption=caption
    )

    return {"ok": True, "telegram_result": telegram_result}


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


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
