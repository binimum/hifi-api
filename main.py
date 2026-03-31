#!/usr/bin/env python3
import asyncio
import json
import os
import random
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Union

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

import logging

logger = logging.getLogger(__name__)

load_dotenv()

API_VERSION = "2.7"

# Shared HTTP client is created in app lifespan for connection reuse
_http_client: Optional[httpx.AsyncClient] = None
_http_client_lock = asyncio.Lock()

# One lock per credential to avoid global contention during token refreshes
_refresh_locks: Dict[str, asyncio.Lock] = {}

# Loaded credential set from token.json; each entry will be enriched with access cache
_creds: List[dict] = []

# Global semaphore to limit concurrent album track fetches across all requests
_album_tracks_sem = asyncio.Semaphore(20)

# List of proxies loaded from file at startup
_proxies: List[str] = []

# Cache of the last proxy confirmed to be working
_last_known_good_proxy: Optional[str] = None


def _build_http_client(proxy_url: Optional[str] = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        proxies=proxy_url,
        http2=True,
        timeout=httpx.Timeout(connect=3.0, read=12.0, write=8.0, pool=12.0),
        limits=httpx.Limits(
            max_keepalive_connections=500,
            max_connections=1000,
            keepalive_expiry=30.0,
        ),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _http_client
    if _http_client is None:
        proxy_url = None
        if USE_PROXIES:
            proxy_url = await get_working_proxy()
            if not proxy_url and not FALLBACK_TO_DIRECT_CONNECTION:
                logger.error("Could not find a working proxy and FALLBACK_TO_DIRECT_CONNECTION is False. Shutting down.")
                raise RuntimeError("No working proxies available")
            elif not proxy_url and FALLBACK_TO_DIRECT_CONNECTION:
                logger.warning("Could not find a working proxy, falling back to direct connection. HOST IP MAY BE EXPOSED!")
        _http_client = _build_http_client(proxy_url)
    try:
        yield
    finally:
        if _http_client:
            await _http_client.aclose()
            _http_client = None

app = FastAPI(
    title="HiFi-RestAPI",
    version=API_VERSION,
    description="Tidal Music Proxy",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Config (defaults act as fallback if token file missing)
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
REFRESH_TOKEN: Optional[str] = os.getenv("REFRESH_TOKEN")
USER_ID = os.getenv("USER_ID")
TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "US")

USE_PROXIES = os.getenv("USE_PROXIES", "False").lower() in ("true", "1", "yes")
ROTATE_PROXIES_ON_REFRESH = os.getenv("ROTATE_PROXIES_ON_REFRESH", "False").lower() in ("true", "1", "yes")
PROXIES_FILE = os.getenv("PROXIES_FILE", "proxies.txt")
FALLBACK_TO_DIRECT_CONNECTION = os.getenv("FALLBACK_TO_DIRECT_CONNECTION", "False").lower() in ("true", "1", "yes")
# Maximum number of proxy candidates to test per get_working_proxy() call
MAX_PROXY_CANDIDATES = 10
# Maximum number of concurrent proxy tests inside get_working_proxy()
_PROXY_TEST_CONCURRENCY = 5
_max_retries_raw = os.getenv("MAX_RETRIES", "2")
try:
    MAX_RETRIES = int(_max_retries_raw)
except ValueError:
    MAX_RETRIES = 2
if MAX_RETRIES < 1:
    MAX_RETRIES = 1
def load_proxies():
    """Load proxies from file into the global _proxies list."""
    global _proxies
    if not os.path.exists(PROXIES_FILE):
        logger.warning(f"Proxies file {PROXIES_FILE} not found.")
        _proxies = []
        return
    with open(PROXIES_FILE, "r") as f:
        _proxies = [line.strip() for line in f if line.strip()]
    logger.info(f"Loaded {len(_proxies)} proxies.")


async def test_proxy(proxy_url: str) -> bool:
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=5.0) as client:
            resp = await client.get("http://example.com")
            return resp.status_code == 200
    except Exception:
        return False


async def get_working_proxy(avoid_proxy: Optional[str] = None) -> Optional[str]:
    global _last_known_good_proxy

    if not _proxies:
        return None

    # Try the cached proxy first (unless it is the one we want to avoid)
    if _last_known_good_proxy and _last_known_good_proxy != avoid_proxy:
        if await test_proxy(_last_known_good_proxy):
            return _last_known_good_proxy

    shuffled_proxies = _proxies[:]
    random.shuffle(shuffled_proxies)

    if avoid_proxy:
        candidate_proxies = [p for p in shuffled_proxies if p != avoid_proxy]
        if not candidate_proxies:
            candidate_proxies = shuffled_proxies
    else:
        candidate_proxies = shuffled_proxies

    # Exclude the already-tested cached proxy and cap the candidate list
    if _last_known_good_proxy:
        candidate_proxies = [p for p in candidate_proxies if p != _last_known_good_proxy]
    candidate_proxies = candidate_proxies[:MAX_PROXY_CANDIDATES]

    # Test candidates concurrently, returning the first one that succeeds
    sem = asyncio.Semaphore(_PROXY_TEST_CONCURRENCY)
    found_event = asyncio.Event()
    selected_proxy: List[Optional[str]] = [None]

    async def probe(proxy: str) -> None:
        if found_event.is_set():
            return
        async with sem:
            if found_event.is_set():
                return
            if await test_proxy(proxy):
                if not found_event.is_set():
                    selected_proxy[0] = proxy
                    found_event.set()

    await asyncio.gather(*[probe(p) for p in candidate_proxies], return_exceptions=True)

    if selected_proxy[0]:
        _last_known_good_proxy = selected_proxy[0]
    return selected_proxy[0]

async def _delayed_close(client: httpx.AsyncClient):
    await asyncio.sleep(15)
    await client.aclose()

async def update_global_client(force_new_proxy: bool = False):
    global _http_client
    async with _http_client_lock:
        proxy_to_avoid = None
        if force_new_proxy and _http_client and _http_client.proxy:
            proxy_to_avoid = str(_http_client.proxy.url)

        proxy_url = None
        if USE_PROXIES:
            proxy_url = await get_working_proxy(avoid_proxy=proxy_to_avoid)
            if not proxy_url:
                if FALLBACK_TO_DIRECT_CONNECTION:
                    logger.warning("Could not find a working proxy, falling back to direct connection. HOST IP MAY BE EXPOSED!")
                else:
                    logger.error("Could not find a working proxy and FALLBACK_TO_DIRECT_CONNECTION is False.")
                    raise HTTPException(status_code=503, detail="Service Unavailable")

        # Only create a new client if the proxy is actually different
        current_proxy_url: Optional[str] = None
        if _http_client and _http_client.proxy:
            current_proxy_url = str(_http_client.proxy.url)
        if _http_client and current_proxy_url == proxy_url:
            return

        new_client = _build_http_client(proxy_url)
        old_client = _http_client
        _http_client = new_client

        if old_client is not None:
            asyncio.create_task(_delayed_close(old_client))


if USE_PROXIES:
    load_proxies()

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as tok:
        token_data = json.load(tok)
        if isinstance(token_data, dict):
            token_data = [token_data]

        for entry in token_data:
            cred = {
                "client_id": entry.get("client_ID") or CLIENT_ID,
                "client_secret": entry.get("client_secret") or CLIENT_SECRET,
                "refresh_token": entry.get("refresh_token") or REFRESH_TOKEN,
                "user_id": entry.get("userID") or USER_ID,
                # Access tokens in file have unknown expiry; force refresh on first use
                "access_token": None,
                "expires_at": 0,
            }
            if cred["refresh_token"]:
                _creds.append(cred)

# Add env var credential if available and unique (simple check)
if REFRESH_TOKEN:
    env_cred = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "user_id": USER_ID,
        "access_token": None,
        "expires_at": 0,
    }
    # Avoid adding duplicate if it was already loaded from file with same refresh token
    if not any(c["refresh_token"] == REFRESH_TOKEN for c in _creds):
        _creds.append(env_cred)

if _creds:
    CLIENT_ID = _creds[0]["client_id"]
    CLIENT_SECRET = _creds[0]["client_secret"]
    REFRESH_TOKEN = _creds[0]["refresh_token"]


def _pick_credential() -> dict:
    if not _creds:
        raise HTTPException(status_code=500, detail="No Tidal credentials available; populate token.json")
    return random.choice(_creds)


def _lock_for_cred(cred: dict) -> asyncio.Lock:
    key = f"{cred['client_id']}:{cred['refresh_token']}"
    lock = _refresh_locks.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _refresh_locks[key] = lock
    return lock


async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        async with _http_client_lock:
            if _http_client is None:
                proxy_url = None
                if USE_PROXIES:
                    proxy_url = await get_working_proxy()
                    if not proxy_url and not FALLBACK_TO_DIRECT_CONNECTION:
                        raise HTTPException(status_code=503, detail="Service Unavailable")
                    elif not proxy_url and FALLBACK_TO_DIRECT_CONNECTION:
                        logger.warning("Could not find a working proxy, falling back to direct connection. HOST IP MAY BE EXPOSED!")
                _http_client = _build_http_client(proxy_url)
    return _http_client


async def refresh_tidal_token(cred: Optional[dict] = None):
    """Refresh a token for the provided credential set."""
    cred = cred or _pick_credential()

    async with _lock_for_cred(cred):
        if cred["access_token"] and time.time() < cred["expires_at"]:
            return cred["access_token"]

        if USE_PROXIES and ROTATE_PROXIES_ON_REFRESH:
            await update_global_client(force_new_proxy=True)

        max_retries = MAX_RETRIES if USE_PROXIES else 1
        for attempt in range(max_retries):
            try:
                client = await get_http_client()
                res = await client.post(
                    "https://auth.tidal.com/v1/oauth2/token",
                    data={
                        "client_id": cred["client_id"],
                        "refresh_token": cred["refresh_token"],
                        "grant_type": "refresh_token",
                        "scope": "r_usr+w_usr+w_sub",
                    },
                    auth=(cred["client_id"], cred["client_secret"]),
                )
                
                if res.status_code in [400, 401]:
                    try:
                        error_data = res.json()
                        if error_data.get("error") in ["invalid_client", "invalid_grant"]:
                            logger.error(f"Tidal Auth Error: {error_data}")
                            raise HTTPException(status_code=401, detail=f"Tidal Auth Error: {error_data.get('error_description')}")
                    except ValueError:
                        pass
                
                res.raise_for_status()
                data = res.json()
                new_token = data["access_token"]
                expires_in = data.get("expires_in", 3600)

                cred["access_token"] = new_token
                cred["expires_at"] = time.time() + expires_in - 60

                return new_token
            except httpx.RequestError as e:
                if USE_PROXIES and attempt < max_retries - 1:
                    logger.warning(f"Proxy failed during token refresh: {e}. Healing proxy...")
                    await update_global_client(force_new_proxy=True)
                    continue
                raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")
            except httpx.HTTPStatusError as e:
                if USE_PROXIES and e.response.status_code in [403, 429] and attempt < max_retries - 1:
                    logger.warning(f"Proxy blocked during token refresh ({e.response.status_code}). Healing proxy...")
                    await update_global_client(force_new_proxy=True)
                    continue
                raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")


async def get_tidal_token(force_refresh: bool = False):
    return await get_tidal_token_for_cred(force_refresh=force_refresh)


async def get_tidal_token_for_cred(force_refresh: bool = False, cred: Optional[dict] = None):
    """Retrieve an access token for a specific credential; pick random if not provided."""
    cred = cred or _pick_credential()

    if not force_refresh and cred["access_token"] and time.time() < cred["expires_at"]:
        return cred["access_token"], cred

    token = await refresh_tidal_token(cred)
    return token, cred


async def make_request(url: str, token: Optional[str] = None, params: Optional[dict] = None, cred: Optional[dict] = None):
    if token is None:
        token, cred = await get_tidal_token_for_cred(cred=cred)
    client = await get_http_client()
    headers = {"authorization": f"Bearer {token}"}

    try:
        resp = await client.get(url, headers=headers, params=params)

        if resp.status_code == 401:
            # Token expired, refresh and retry
            token, cred = await get_tidal_token_for_cred(force_refresh=True, cred=cred)
            headers = {"authorization": f"Bearer {token}"}
            resp = await client.get(url, headers=headers, params=params)

        resp.raise_for_status()
        return {"version": API_VERSION, "data": resp.json()}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found")
        else:
            logger.error(
                "Upstream API error %s %s %s",
                e.response.status_code,
                url,
                e.response.text,
                exc_info=e,
            )
            raise HTTPException(status_code=e.response.status_code, detail="Upstream API error")
    except httpx.RequestError as e:
        if isinstance(e, httpx.TimeoutException):
            raise HTTPException(status_code=429, detail="Upstream timeout")
        raise HTTPException(status_code=503, detail="Connection error to Tidal")


async def authed_get_json(
    url: str,
    *,
    params: Optional[dict] = None,
    token: Optional[str] = None,
    cred: Optional[dict] = None,
):
    """Perform an authenticated GET, retrying once on 401. Returns payload with updated token/cred."""

    if token is None:
        token, cred = await get_tidal_token_for_cred(cred=cred)

    client = await get_http_client()
    headers = {"authorization": f"Bearer {token}"}

    try:
        resp = await client.get(url, headers=headers, params=params)

        if resp.status_code == 401:
            token, cred = await get_tidal_token_for_cred(force_refresh=True, cred=cred)
            headers["authorization"] = f"Bearer {token}"
            resp = await client.get(url, headers=headers, params=params)

        resp.raise_for_status()
        return resp.json(), token, cred
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Upstream rate limited")
        raise HTTPException(status_code=e.response.status_code, detail="Upstream API error")
    except httpx.RequestError as e:
        if isinstance(e, httpx.TimeoutException):
            raise HTTPException(status_code=429, detail="Upstream timeout")
        raise HTTPException(status_code=503, detail="Connection error to Tidal")

@app.get("/")
async def index():
    return {"version": API_VERSION, "Repo": "https://github.com/binimum/hifi-api"}

@app.get("/info/")
async def get_info(id: int):
    url = f"https://api.tidal.com/v1/tracks/{id}/"
    return await make_request(url, params={"countryCode": COUNTRY_CODE})

@app.get("/track/")
async def get_track(id: int, quality: str = "HI_RES_LOSSLESS", immersiveaudio: bool = False):
    track_url = f"https://api.tidal.com/v1/tracks/{id}/playbackinfo"
    params = {
        "audioquality": quality,
        "playbackmode": "STREAM",
        "assetpresentation": "FULL",
        "immersiveaudio": immersiveaudio
    }
    return await make_request(track_url, params=params)


@app.get("/trackManifests/")
async def get_track_manifests(
    id: str,
    request: Request,
    formats: List[str] = Query(default=["HEAACV1", "AACLC", "FLAC", "FLAC_HIRES", "EAC3_JOC"]),
    adaptive: str = Query(default="true"),
    manifestType: str = Query(default="MPEG_DASH"),
    uriScheme: str = Query(default="HTTPS"),
    usage: str = Query(default="PLAYBACK")
):
    url = f"https://openapi.tidal.com/v2/trackManifests/{id}"
    params = [
        ("adaptive", adaptive),
        ("manifestType", manifestType),
        ("uriScheme", uriScheme),
        ("usage", usage),
    ]
    for f in formats:
        params.append(("formats", f))
    res = await make_request(url, params=params)
    try:
        drm_data = res["data"]["data"]["attributes"]["drmData"]
        if drm_data:
            proxy_url = str(request.base_url).rstrip("/") + "/widevine"
            drm_data["licenseUrl"] = proxy_url
            drm_data["certificateUrl"] = proxy_url
    except (KeyError, TypeError):
        pass
    return res

# Not really necessary but I'm including it anyway
@app.api_route("/widevine", methods=["GET", "POST"])
async def widevine_proxy(request: Request):
    client = await get_http_client()
    body = await request.body()
    url = "https://api.tidal.com/v2/widevine"

    token, cred = await get_tidal_token_for_cred()
    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": request.headers.get("Content-Type", "application/octet-stream")
    }

    try:
        resp = await client.request(request.method, url, headers=headers, content=body)

        if resp.status_code == 401:
            token, cred = await get_tidal_token_for_cred(force_refresh=True, cred=cred)
            headers["authorization"] = f"Bearer {token}"
            resp = await client.request(request.method, url, headers=headers, content=body)

        return fastapi.Response(
            content=resp.content,
            status_code=resp.status_code,
            headers={"Content-Type": resp.headers.get("Content-Type", "application/json")}
        )
    except Exception as e:
        raise fastapi.HTTPException(status_code=502, detail="Error communicating with widevine server")


@app.get("/recommendations/")
async def get_recommendations(id: int):
    recommendations_url = f"https://api.tidal.com/v1/tracks/{id}/recommendations"
    params = {"limit": "20", "countryCode": COUNTRY_CODE}
    return await make_request(recommendations_url, params=params)


@app.api_route("/search/", methods=["GET"])
async def search(
    s: Union[str, None] = Query(default=None),
    a: Union[str, None] = Query(default=None),
    al: Union[str, None] = Query(default=None),
    v: Union[str, None] = Query(default=None),
    p: Union[str, None] = Query(default=None),
    i: Union[str, None] = Query(default=None, description="ISRC query"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=500),
):
    """Search endpoint supporting track/artist/album/video/playlist queries via distinct params."""
    isrc_query = i.strip() if isinstance(i, str) else None
    if isrc_query:
        return await make_request(
            "https://api.tidal.com/v1/tracks",
            params={
                "isrc": isrc_query,
                "limit": limit,
                "offset": offset,
                "countryCode": COUNTRY_CODE,
            },
        )

    queries = (
        (s, "https://api.tidal.com/v1/search/tracks", {
            "query": s,
            "limit": limit,
            "offset": offset,
            "countryCode": COUNTRY_CODE,
        }),
        (a, "https://api.tidal.com/v1/search/top-hits", {
            "query": a,
            "limit": limit,
            "offset": offset,
            "types": "ARTISTS,TRACKS",
            "countryCode": COUNTRY_CODE,
        }),
        (al, "https://api.tidal.com/v1/search/top-hits", {
            "query": al,
            "limit": limit,
            "offset": offset,
            "types": "ALBUMS",
            "countryCode": COUNTRY_CODE,
        }),
        (v, "https://api.tidal.com/v1/search/top-hits", {
            "query": v,
            "limit": limit,
            "offset": offset,
            "types": "VIDEOS",
            "countryCode": COUNTRY_CODE,
        }),
        (p, "https://api.tidal.com/v1/search/top-hits", {
            "query": p,
            "limit": limit,
            "offset": offset,
            "types": "PLAYLISTS",
            "countryCode": COUNTRY_CODE,
        }),
    )

    for value, url, params in queries:
        if value:
            return await make_request(url, params=params)

    raise HTTPException(status_code=400, detail="Provide one of s, a, al, v, p, or i")

@app.get("/album/")
async def get_album(
    id: int = Query(..., description="Album ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    token, cred = await get_tidal_token_for_cred()

    album_url = f"https://api.tidal.com/v1/albums/{id}"
    items_url = f"https://api.tidal.com/v1/albums/{id}/items"

    async def fetch(url: str, params: Optional[dict] = None):
        payload, _, _ = await authed_get_json(
            url,
            params=params,
            token=token,
            cred=cred,
        )
        return payload

    tasks = [fetch(album_url, {"countryCode": COUNTRY_CODE})]

    max_chunk = 100
    current_offset = offset
    remaining_limit = limit

    while remaining_limit > 0:
        chunk_size = min(remaining_limit, max_chunk)
        tasks.append(
            fetch(items_url, {"countryCode": COUNTRY_CODE, "limit": chunk_size, "offset": current_offset})
        )
        current_offset += chunk_size
        remaining_limit -= chunk_size

    results = await asyncio.gather(*tasks)

    album_data = results[0]
    items_pages = results[1:]

    all_items = []
    for page in items_pages:
        page_items = page.get("items", page) if isinstance(page, dict) else page
        if isinstance(page_items, list):
            all_items.extend(page_items)

    album_data["items"] = all_items

    return {
        "version": API_VERSION,
        "data": album_data,
    }


@app.get("/mix/")
async def get_mix(
    id: str = Query(..., description="Mix ID")
):
    """Fetch items from a Tidal mix by its ID."""
    token, cred = await get_tidal_token_for_cred()
    url = "https://api.tidal.com/v1/pages/mix"
    params = {
        "mixId": id,
        "countryCode": COUNTRY_CODE,
        "deviceType": "BROWSER",
    }

    data, _, _ = await authed_get_json(
        url,
        params=params,
        token=token,
        cred=cred,
    )

    header = {}
    items = []

    rows = data.get("rows", [])
    for row in rows:
        modules = row.get("modules", [])
        for module in modules:
            if module.get("type") == "MIX_HEADER":
                header = module.get("mix", {})
            elif module.get("type") == "TRACK_LIST":
                paged_list = module.get("pagedList", {})
                items = paged_list.get("items", [])

    return {
        "version": API_VERSION,
        "mix": header,
        "items": [item.get("item", item) if isinstance(item, dict) else item for item in items],
    }


@app.get("/playlist/")
async def get_playlist(
    id: str = Query(..., min_length=1),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Fetch playlist metadata plus items concurrently, using shared client and single token."""

    token, cred = await get_tidal_token_for_cred()

    playlist_url = f"https://api.tidal.com/v1/playlists/{id}"
    items_url = f"https://api.tidal.com/v1/playlists/{id}/items"

    async def fetch(url: str, params: Optional[dict] = None):
        payload, _, _ = await authed_get_json(
            url,
            params=params,
            token=token,
            cred=cred,
        )
        return payload

    playlist_data, items_data = await asyncio.gather(
        fetch(playlist_url, {"countryCode": COUNTRY_CODE}),
        fetch(items_url, {"countryCode": COUNTRY_CODE, "limit": limit, "offset": offset}),
    )

    return {
        "version": API_VERSION,
        "playlist": playlist_data,
        "items": items_data.get("items", items_data) if isinstance(items_data, dict) else items_data,
    }


def _extract_uuid_from_tidal_url(href: str) -> Optional[str]:
    """Extract and reconstruct a hyphenated UUID from a Tidal resource URL."""
    parts = href.split("/") if href else []
    return "-".join(parts[4:9]) if len(parts) >= 9 else None


@app.get("/artist/similar/")
async def get_similar_artists(
    id: int = Query(..., description="Artist ID"),
    cursor: Union[int, str, None] = None
):
    """Fetch artists similar to another by its ID using V2 API."""
    url = f"https://openapi.tidal.com/v2/artists/{id}/relationships/similarArtists"
    params = {
        "page[cursor]": cursor,
        "countryCode": COUNTRY_CODE,
        "include": "similarArtists,similarArtists.profileArt"
    }

    payload, _, _ = await authed_get_json(url, params=params)
    included = payload.get("included", [])
    artists_map = {i["id"]: i for i in included if i["type"] == "artists"}
    artworks_map = {i["id"]: i for i in included if i["type"] == "artworks"}

    def resolve_artist(entry):
        aid = entry["id"]
        inc = artists_map.get(aid, {})
        attr = inc.get("attributes", {})

        pic_id = None
        if art_data := inc.get("relationships", {}).get("profileArt", {}).get("data"):
            if artwork := artworks_map.get(art_data[0].get("id")):
                if files := artwork.get("attributes", {}).get("files"):
                    pic_id = _extract_uuid_from_tidal_url(files[0].get("href"))

        return {
            **attr,
            "id": int(aid) if str(aid).isdigit() else aid,
            "picture": pic_id or attr.get("selectedAlbumCoverFallback"),
            "url": f"http://www.tidal.com/artist/{aid}",
            "relationType": "SIMILAR_ARTIST"
        }

    return {
        "version": API_VERSION,
        "artists": [resolve_artist(e) for e in payload.get("data", [])]
    }


@app.get("/album/similar/")
async def get_similar_albums(
    id: int = Query(..., description="Album ID"),
    cursor: Union[int, str, None] = None
):
    """Fetch albums similar to another by its ID using V2 API."""
    url = f"https://openapi.tidal.com/v2/albums/{id}/relationships/similarAlbums"
    params = {
        "page[cursor]": cursor,
        "countryCode": COUNTRY_CODE,
        "include": "similarAlbums,similarAlbums.coverArt,similarAlbums.artists"
    }

    payload, _, _ = await authed_get_json(url, params=params)
    included = payload.get("included", [])
    albums_map = {i["id"]: i for i in included if i["type"] == "albums"}
    artworks_map = {i["id"]: i for i in included if i["type"] == "artworks"}
    artists_map = {i["id"]: i for i in included if i["type"] == "artists"}

    def resolve_album(entry):
        aid = entry["id"]
        inc = albums_map.get(aid, {})
        attr = inc.get("attributes", {})

        cover_id = None
        if art_data := inc.get("relationships", {}).get("coverArt", {}).get("data"):
            if artwork := artworks_map.get(art_data[0].get("id")):
                if files := artwork.get("attributes", {}).get("files"):
                    cover_id = _extract_uuid_from_tidal_url(files[0].get("href"))

        artist_list = []
        if art_data := inc.get("relationships", {}).get("artists", {}).get("data"):
             for a_entry in art_data:
                 if a_obj := artists_map.get(a_entry["id"]):
                     a_id = a_obj["id"]
                     artist_list.append({
                         "id": int(a_id) if str(a_id).isdigit() else a_id,
                         "name": a_obj["attributes"]["name"]
                     })

        return {
            **attr,
            "id": int(aid) if str(aid).isdigit() else aid,
            "cover": cover_id,
            "artists": artist_list,
            "url": f"http://www.tidal.com/album/{aid}"
        }

    return {
        "version": API_VERSION,
        "albums": [resolve_album(e) for e in payload.get("data", [])]
    }


@app.get("/artist/")
async def get_artist(
    id: Optional[int] = Query(default=None),
    f: Optional[int] = Query(default=None),
    skip_tracks: bool = Query(default=False),
):
    """Artist detail or album+track aggregation.

    - id: basic artist metadata + cover URLs
    - f: fetch artist albums page and aggregate tracks across albums (capped concurrency)
    - skip_tracks: if true, returns only albums without aggregating tracks (when using 'f')
    """

    if id is None and f is None:
        raise HTTPException(status_code=400, detail="Provide id or f query param")

    token, cred = await get_tidal_token_for_cred()

    if id is not None:
        artist_url = f"https://api.tidal.com/v1/artists/{id}"
        artist_data, token, cred = await authed_get_json(
            artist_url,
            params={"countryCode": COUNTRY_CODE},
            token=token,
            cred=cred,
        )

        picture = artist_data.get("picture")
        fallback = artist_data.get("selectedAlbumCoverFallback")

        if not picture and fallback:
            artist_data["picture"] = fallback
            picture = fallback

        cover = None
        if picture:
            slug = picture.replace("-", "/")
            cover = {
                "id": artist_data.get("id"),
                "name": artist_data.get("name"),
                "750": f"https://resources.tidal.com/images/{slug}/750x750.jpg",
            }

        return {"version": API_VERSION, "artist": artist_data, "cover": cover}

    # Fetch albums and singles/EPs directly in parallel
    albums_url = f"https://api.tidal.com/v1/artists/{f}/albums"
    common_params = {"countryCode": COUNTRY_CODE, "limit": 100}

    tasks = [
        authed_get_json(albums_url, params=common_params, token=token, cred=cred),
        authed_get_json(albums_url, params={**common_params, "filter": "EPSANDSINGLES"}, token=token, cred=cred),
    ]

    if skip_tracks:
        tasks.append(
            authed_get_json(
                f"https://api.tidal.com/v1/artists/{f}/toptracks",
                params={"countryCode": COUNTRY_CODE, "limit": 15},
                token=token,
                cred=cred
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    unique_releases = []
    seen_ids = set()

    # Process albums (first 2 results)
    for res in results[:2]:
        if isinstance(res, tuple) and len(res) > 0:
            data = res[0]
            items = data.get("items", []) if isinstance(data, dict) else data
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get("id") and item["id"] not in seen_ids:
                        unique_releases.append(item)
                        seen_ids.add(item["id"])
        elif isinstance(res, Exception):
            logger.warning("Error fetching artist releases: %s", res)

    album_ids: List[int] = [item["id"] for item in unique_releases]
    page_data = {"items": unique_releases}

    if skip_tracks:
        top_tracks = []
        if len(results) > 2:
            res = results[2]
            if isinstance(res, tuple) and len(res) > 0:
                data = res[0]
                top_tracks = data.get("items", []) if isinstance(data, dict) else data
            elif isinstance(res, Exception):
                logger.warning("Error fetching top tracks: %s", res)

        return {"version": API_VERSION, "albums": page_data, "tracks": top_tracks}

    if not album_ids:
        return {"version": API_VERSION, "albums": page_data, "tracks": []}

    async def fetch_album_tracks(album_id: int):
        async with _album_tracks_sem:
            album_data, _, _ = await authed_get_json(
                "https://api.tidal.com/v1/pages/album",
                params={
                    "albumId": album_id,
                    "countryCode": COUNTRY_CODE,
                    "deviceType": "BROWSER",
                },
                token=token,
                cred=cred,
            )

            rows = album_data.get("rows", [])
            if len(rows) < 2:
                return []
            modules = rows[1].get("modules", [])
            if not modules:
                return []
            paged_list = modules[0].get("pagedList", {})
            items = paged_list.get("items", [])
            tracks = [track.get("item", track) if isinstance(track, dict) else track for track in items]
            return tracks

    results = await asyncio.gather(
        *(fetch_album_tracks(album_id) for album_id in album_ids),
        return_exceptions=True,
    )

    tracks: List[dict] = []
    for res in results:
        if isinstance(res, Exception):
            continue
        tracks.extend(res)

    return {"version": API_VERSION, "albums": page_data, "tracks": tracks}


@app.get("/cover/")
async def get_cover(
    id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None),
):
    """Fetch album cover data for a track id or search query."""

    if id is None and q is None:
        raise HTTPException(status_code=400, detail="Provide id or q query param")

    token, cred = await get_tidal_token_for_cred()

    def build_cover_entry(cover_slug: str, name: Optional[str], track_id: Optional[int]):
        slug = cover_slug.replace("-", "/")
        return {
            "id": track_id,
            "name": name,
            "1280": f"https://resources.tidal.com/images/{slug}/1280x1280.jpg",
            "640": f"https://resources.tidal.com/images/{slug}/640x640.jpg",
            "80": f"https://resources.tidal.com/images/{slug}/80x80.jpg",
        }

    if id is not None:
        track_data, token, cred = await authed_get_json(
            f"https://api.tidal.com/v1/tracks/{id}/",
            params={"countryCode": COUNTRY_CODE},
            token=token,
            cred=cred,
        )

        album = track_data.get("album") or {}
        cover_slug = album.get("cover")
        if not cover_slug:
            raise HTTPException(status_code=404, detail="Cover not found")

        entry = build_cover_entry(
            cover_slug,
            album.get("title") or track_data.get("title"),
            album.get("id") or id,
        )
        return {"version": API_VERSION, "covers": [entry]}

    search_data, token, cred = await authed_get_json(
        "https://api.tidal.com/v1/search/tracks",
        params={"countryCode": COUNTRY_CODE, "query": q, "limit": 10},
        token=token,
        cred=cred,
    )

    items = search_data.get("items", [])[:10]
    if not items:
        raise HTTPException(status_code=404, detail="Cover not found")

    covers = []
    for track in items:
        album = track.get("album") or {}
        cover_slug = album.get("cover")
        if not cover_slug:
            continue
        covers.append(
            build_cover_entry(
                cover_slug,
                track.get("title"),
                track.get("id"),
            )
        )

    if not covers:
        raise HTTPException(status_code=404, detail="Cover not found")

    return {"version": API_VERSION, "covers": covers}


@app.get("/lyrics/")
async def get_lyrics(id: int):
    url = f"https://api.tidal.com/v1/tracks/{id}/lyrics"
    data, token, cred = await authed_get_json(
        url,
        params={"countryCode": COUNTRY_CODE, "locale": "en_US", "deviceType": "BROWSER"},
    )

    if not data:
        raise HTTPException(status_code=404, detail="Lyrics not found")

    return {"version": API_VERSION, "lyrics": data}


@app.get("/topvideos/")
async def get_top_videos(
    countryCode: str = Query(default="US"),
    locale: str = Query(default="en_US"),
    deviceType: str = Query(default="BROWSER"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Fetch recommended videos from Tidal."""
    token, cred = await get_tidal_token_for_cred()
    url = "https://api.tidal.com/v1/pages/mymusic_recommended_videos"
    params = {
        "countryCode": countryCode,
        "locale": locale,
        "deviceType": deviceType,
    }

    data, token, cred = await authed_get_json(
        url,
        params=params,
        token=token,
        cred=cred,
    )

    rows = data.get("rows", [])
    all_videos = []
    for row in rows:
        modules = row.get("modules", [])
        for module in modules:
            module_type = module.get("type")
            if module_type in ("VIDEO_PLAYLIST", "VIDEO_ROW", "PAGED_LIST"):
                paged_list = module.get("pagedList", {})
                if paged_list:
                    items = paged_list.get("items", [])
                    for item in items:
                        video = item.get("item", item) if isinstance(item, dict) else item
                        all_videos.append(video)
            elif module_type == "VIDEO" or (module_type and "video" in module_type.lower()):
                item = module.get("item", module)
                if isinstance(item, dict):
                    all_videos.append(item)

    paginated = all_videos[offset:offset + limit]

    response = {
        "version": API_VERSION,
        "videos": paginated,
        "total": len(all_videos),
    }
    return response

@app.get("/video/")
async def get_video(
    id: int = Query(..., description="Video ID"),
    quality: str = Query(default="HIGH", description="Video quality (HIGH, MEDIUM, LOW)"),
    mode: str = Query(default="STREAM", description="Playback mode (STREAM, OFFLINE)"),
    presentation: str = Query(default="FULL", description="Asset presentation (FULL, PREVIEW)"),
):
    """Fetch video playback info from Tidal."""
    token, cred = await get_tidal_token_for_cred()
    url = f"https://api.tidal.com/v1/videos/{id}/playbackinfo"
    params = {
        "videoquality": quality,
        "playbackmode": mode,
        "assetpresentation": presentation,
    }

    data, token, cred = await authed_get_json(
        url,
        params=params,
        token=token,
        cred=cred,
    )

    return {"version": API_VERSION, "video": data}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
