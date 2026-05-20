"""YouTube API integration — multi-channel hub with proper Shorts/Videos/Live separation via playlist prefixes + Redis caching."""
from fastapi import APIRouter, Query
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from database import logger
import os
import json
import redis

router = APIRouter(prefix="/api/youtube")

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
CACHE_TTL = 900  # 15 minutes

# YouTube playlist prefix magic:
# UC -> UULF (regular videos only, no shorts/live)
# UC -> UUSH (shorts only)
# UC -> UULV (live streams only)
# UC -> UULP (popular videos)

# The pre-populated channel list from the source repo was Telangana/Andhra political
# Telugu news channels — irrelevant to a startup intelligence platform. Empty by default;
# admins can populate via the admin UI or an env-loaded list.
CHANNELS = []

try:
    cache = redis.Redis(host="localhost", port=6379, db=2, decode_responses=True)
    cache.ping()
except Exception:
    cache = None
    logger.warning("Redis not available for YouTube cache")


def get_youtube():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False)


def cache_get(key):
    if not cache:
        return None
    try:
        val = cache.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


def cache_set(key, data, ttl=CACHE_TTL):
    if not cache:
        return
    try:
        cache.setex(key, ttl, json.dumps(data))
    except Exception:
        pass


def _channel_to_playlist(channel_id: str, prefix: str) -> str:
    """Convert channel ID to special playlist ID.
    UC -> UULF (videos), UC -> UUSH (shorts), UC -> UULV (live)"""
    if channel_id.startswith("UC"):
        return prefix + channel_id[2:]
    return channel_id


def _parse_playlist_item(item, channel_id=""):
    """Parse a playlistItems response item."""
    snippet = item["snippet"]
    vid = snippet.get("resourceId", {}).get("videoId", "")
    return {
        "id": vid,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", "")[:200],
        "thumbnail": snippet.get("thumbnails", {}).get("high", snippet.get("thumbnails", {}).get("default", {})).get("url", ""),
        "published_at": snippet.get("publishedAt", ""),
        "channel_title": snippet.get("channelTitle", snippet.get("videoOwnerChannelTitle", "")),
        "channel_id": snippet.get("videoOwnerChannelId", channel_id),
    }


@router.get("/channels")
async def get_all_channels():
    """Return all channels with stats (cached 15 min)."""
    cached = cache_get("yt:channels_info")
    if cached:
        return cached

    try:
        youtube = get_youtube()
        ids_str = ",".join(c["id"] for c in CHANNELS)
        res = youtube.channels().list(part="snippet,statistics", id=ids_str).execute()

        channel_map = {}
        for item in res.get("items", []):
            channel_map[item["id"]] = item

        result = []
        for ch in CHANNELS:
            yt_data = channel_map.get(ch["id"])
            if yt_data:
                stats = yt_data["statistics"]
                snippet = yt_data["snippet"]
                result.append({
                    "id": ch["id"],
                    "handle": ch["handle"],
                    "name": ch["name"],
                    "thumbnail": snippet["thumbnails"].get("high", snippet["thumbnails"].get("default", {})).get("url", ""),
                    "subscriber_count": int(stats.get("subscriberCount", 0)),
                    "video_count": int(stats.get("videoCount", 0)),
                    "view_count": int(stats.get("viewCount", 0)),
                })

        result.sort(key=lambda x: x["subscriber_count"], reverse=True)
        response = {"channels": result, "total": len(result)}
        cache_set("yt:channels_info", response)
        return response

    except HttpError as e:
        logger.error(f"YouTube channels API error: {e}")
        return {
            "channels": [{"id": c["id"], "handle": c["handle"], "name": c["name"],
                          "thumbnail": "", "subscriber_count": 0, "video_count": 0, "view_count": 0} for c in CHANNELS],
            "total": len(CHANNELS)
        }


@router.get("/videos")
async def get_channel_videos(
    channel_id: str = Query(default="all"),
    max_results: int = Query(default=12, ge=1, le=50),
):
    """Fetch REGULAR VIDEOS (no shorts, no live) using UULF playlist prefix. Costs only 1 unit per call!"""
    cache_key = f"yt:videos_uulf:{channel_id}:{max_results}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        youtube = get_youtube()

        if channel_id == "all":
            top_channels = [c["id"] for c in CHANNELS[:5]]
            per_channel = max(3, max_results // len(top_channels) + 1)
            all_videos = []
            for cid in top_channels:
                playlist_id = _channel_to_playlist(cid, "UULF")
                try:
                    res = youtube.playlistItems().list(
                        part="snippet", playlistId=playlist_id, maxResults=per_channel,
                    ).execute()
                    for item in res.get("items", []):
                        all_videos.append(_parse_playlist_item(item, cid))
                except HttpError:
                    continue
            all_videos.sort(key=lambda x: x["published_at"], reverse=True)
            result = {"videos": all_videos[:max_results], "total": len(all_videos[:max_results])}
        else:
            playlist_id = _channel_to_playlist(channel_id, "UULF")
            res = youtube.playlistItems().list(
                part="snippet", playlistId=playlist_id, maxResults=max_results,
            ).execute()
            videos = [_parse_playlist_item(item, channel_id) for item in res.get("items", [])]
            result = {"videos": videos, "total": len(videos)}

        cache_set(cache_key, result)
        return result

    except HttpError as e:
        logger.error(f"YouTube videos API error: {e}")
        return {"videos": [], "total": 0, "error": str(e)}


@router.get("/shorts")
async def get_shorts(
    channel_id: str = Query(default="all"),
    max_results: int = Query(default=20, ge=1, le=50),
):
    """Fetch YouTube Shorts using UUSH playlist prefix. YouTube's own categorization — includes shorts up to 3 min."""
    cache_key = f"yt:shorts_uush:{channel_id}:{max_results}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        youtube = get_youtube()

        if channel_id == "all":
            top_channels = [c["id"] for c in CHANNELS[:5]]
            per_channel = max(4, max_results // len(top_channels) + 1)
            all_shorts = []
            for cid in top_channels:
                playlist_id = _channel_to_playlist(cid, "UUSH")
                try:
                    res = youtube.playlistItems().list(
                        part="snippet", playlistId=playlist_id, maxResults=per_channel,
                    ).execute()
                    for item in res.get("items", []):
                        v = _parse_playlist_item(item, cid)
                        v["is_short"] = True
                        all_shorts.append(v)
                except HttpError:
                    continue
            all_shorts.sort(key=lambda x: x["published_at"], reverse=True)
            result = {"shorts": all_shorts[:max_results], "total": len(all_shorts[:max_results])}
        else:
            playlist_id = _channel_to_playlist(channel_id, "UUSH")
            res = youtube.playlistItems().list(
                part="snippet", playlistId=playlist_id, maxResults=max_results,
            ).execute()
            shorts = []
            for item in res.get("items", []):
                v = _parse_playlist_item(item, channel_id)
                v["is_short"] = True
                shorts.append(v)
            result = {"shorts": shorts, "total": len(shorts)}

        cache_set(cache_key, result)
        return result

    except HttpError as e:
        logger.error(f"YouTube shorts API error: {e}")
        return {"shorts": [], "total": 0, "error": str(e)}


@router.get("/live")
async def get_live_streams(
    channel_id: str = Query(default="all"),
):
    """Get current live streams using search API (eventType=live requires search)."""
    cache_key = f"yt:live:{channel_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        youtube = get_youtube()
        all_streams = []
        channels_to_check = [c["id"] for c in CHANNELS] if channel_id == "all" else [channel_id]

        for cid in channels_to_check:
            try:
                res = youtube.search().list(
                    part="snippet", channelId=cid, eventType="live",
                    type="video", maxResults=3,
                ).execute()
                for item in res.get("items", []):
                    snippet = item["snippet"]
                    all_streams.append({
                        "id": item["id"]["videoId"],
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", "")[:200],
                        "thumbnail": snippet["thumbnails"].get("high", snippet["thumbnails"].get("default", {})).get("url", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "channel_title": snippet.get("channelTitle", ""),
                        "channel_id": cid,
                        "is_live": True,
                    })
            except HttpError:
                continue

        result = {"streams": all_streams, "is_live": len(all_streams) > 0}
        cache_set(cache_key, result, ttl=300)
        return result

    except Exception as e:
        logger.error(f"YouTube live API error: {e}")
        return {"streams": [], "is_live": False, "error": str(e)}


@router.get("/channel")
async def get_channel_info(
    channel_id: str = Query(default=CHANNELS[0]["id"]),
):
    """Get single channel statistics (cached)."""
    cache_key = f"yt:channel:{channel_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        youtube = get_youtube()
        res = youtube.channels().list(part="snippet,statistics", id=channel_id).execute()

        if not res.get("items"):
            return {"channel": None}

        item = res["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]

        result = {
            "channel": {
                "id": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:300],
                "thumbnail": snippet["thumbnails"].get("high", snippet["thumbnails"].get("default", {})).get("url", ""),
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
            }
        }
        cache_set(cache_key, result)
        return result

    except HttpError as e:
        logger.error(f"YouTube channel API error: {e}")
        return {"channel": None, "error": str(e)}
