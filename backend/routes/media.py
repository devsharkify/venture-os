from fastapi import APIRouter, HTTPException
from typing import List
import re
from database import db
from models import LiveChannel, LiveChannelCreate, YouTubeShort, YouTubeShortCreate
from helpers import prepare_for_mongo

router = APIRouter(prefix="/api")

def extract_youtube_id(url: str) -> str:
    patterns = [r'(?:v=|\/embed\/|\/live\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', r'([a-zA-Z0-9_-]{11})']
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""

@router.get("/live-tv")
async def get_live_channels():
    channels = await db.live_channels.find({"is_active": True}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return channels

@router.post("/live-tv")
async def add_live_channel(data: LiveChannelCreate):
    yt_id = extract_youtube_id(data.youtube_url)
    channel = LiveChannel(name=data.name, youtube_url=data.youtube_url, youtube_id=yt_id)
    doc = prepare_for_mongo(channel.model_dump())
    await db.live_channels.insert_one(doc)
    return {"status": "added", "channel": channel.model_dump()}

@router.delete("/live-tv/{channel_id}")
async def delete_live_channel(channel_id: str):
    result = await db.live_channels.delete_one({"id": channel_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"status": "deleted"}

@router.get("/shorts")
async def get_shorts():
    shorts = await db.youtube_shorts.find({"is_active": True}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return shorts

@router.post("/shorts")
async def add_short(data: YouTubeShortCreate):
    yt_id = extract_youtube_id(data.youtube_url)
    short = YouTubeShort(title=data.title or f"Short #{yt_id[:6]}", youtube_url=data.youtube_url, youtube_id=yt_id)
    doc = prepare_for_mongo(short.model_dump())
    await db.youtube_shorts.insert_one(doc)
    return {"status": "added", "short": short.model_dump()}

@router.post("/shorts/bulk")
async def add_shorts_bulk(shorts: List[YouTubeShortCreate]):
    added = []
    for data in shorts:
        yt_id = extract_youtube_id(data.youtube_url)
        existing = await db.youtube_shorts.find_one({"youtube_id": yt_id})
        if existing:
            continue
        short = YouTubeShort(title=data.title or f"Short #{yt_id[:6]}", youtube_url=data.youtube_url, youtube_id=yt_id)
        doc = prepare_for_mongo(short.model_dump())
        await db.youtube_shorts.insert_one(doc)
        added.append(short.model_dump())
    return {"status": "added", "count": len(added)}

@router.delete("/shorts/{short_id}")
async def delete_short(short_id: str):
    result = await db.youtube_shorts.delete_one({"id": short_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Short not found")
    return {"status": "deleted"}
