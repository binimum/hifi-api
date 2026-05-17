import asyncio
import json
import os
import webbrowser
from pathlib import Path
import base64

import httpx
import rich

TOKEN_FILE = Path(os.getenv("TOKEN_FILE", Path(__file__).resolve().parent.parent / "token.json"))
USER_AGENT = os.getenv("USER_AGENT", "okhttp/5.3.2")


AUTH_CLIENT_ID = base64.b64decode("ZlgySnhkbW50WldLMGl4VA==").decode("iso-8859-1")
AUTH_CLIENT_SECRET = base64.b64decode(
    "MU5tNUFmREFqeHJnSkZKYktOV0xlQXlLR1ZHbUlOdVhQUExIVlhBdnhBZz0=",
).decode("iso-8859-1")
REQUEST_CLIENT_ID = base64.b64decode("bHczdlI2R0UxdnROQnNqdg==").decode("iso-8859-1")
REQUEST_CLIENT_SECRET = base64.b64decode(
    "WTh0SXBxS0p4czlCRUl3WXIwSTliU2JNV0Rzb2dYSng5TGFOM21DSHdENCUzRA==",
).decode("iso-8859-1")

class Hifi:
    def __init__(self, client_id, scope, url, client_secret):
        self.client_id = client_id
        self.scope = scope
        self.url = url
        self.client_secret = client_secret

    @staticmethod
    def Quality(quality):
        rate = {quality: "HI_RES"}
        return rate[quality]


class Auth(Hifi):
    def __init__(self, client_id, scope, url, client_secret):
        super().__init__(client_id, scope, url, client_secret)
        self.response = None

    async def get_auth_response(self):
        data = {"client_id": self.client_id, "scope": self.scope}
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Platform": "android",
        }

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.post(self.url, data=data, headers=headers)
            # We handle status codes in the main loop now

        self.response = response

    def __str__(self):
        return str(self.response)


def load_tokens():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return [data]
    return []


def save_token_entry(entry):
    tokens = load_tokens()
    tokens = [t for t in tokens if not (
        t.get("client_ID") == entry["client_ID"] and t.get("refresh_token") == entry["refresh_token"]
    )]
    tokens.append(entry)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=4)


async def poll_for_authorization(url, data, auth):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Platform": "android",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        while True:
            response = await client.post(url, data=data, auth=auth)
            if response.status_code == 200:
                return response.json()
            await asyncio.sleep(5)

async def main():
    async def run_link_flow():
        rich.print(f"Trying Client ID: {AUTH_CLIENT_ID}")
        authrize = Auth(
            client_id=AUTH_CLIENT_ID,
            scope="r_usr+w_usr+w_sub",
            url="https://auth.tidal.com/v1/oauth2/device_authorization",
            client_secret=AUTH_CLIENT_SECRET,
        )

        try:
            await authrize.get_auth_response()
        except Exception as e:
            rich.print(f"[red]Exception: {e}.[/red]")
            return False

        if authrize.response.status_code != 200:
            rich.print(f"[red]Error {authrize.response.status_code}.[/red]")
            return False

        res = authrize.response.json()

        verifyurl = res["verificationUriComplete"]
        dcode = res["deviceCode"]

        rich.print(verifyurl)
        rich.print(dcode)

        HI_RES = authrize.Quality(quality="True")
        rich.print(HI_RES)

        webbrowser.open(verifyurl)

        url2 = "https://auth.tidal.com/v1/oauth2/token"

        data2 = {
            "client_id": authrize.client_id,
            "scope": authrize.scope,
            "device_code": dcode,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }

        basic = (authrize.client_id, authrize.client_secret)

        auth_response = await poll_for_authorization(url2, data2, basic)

        access_token = auth_response["access_token"]
        refresh_token = auth_response["refresh_token"]
        user_id = auth_response["user"]["userId"]
        accs = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "userID": user_id,
            "client_ID": REQUEST_CLIENT_ID,
            "client_secret": REQUEST_CLIENT_SECRET,
        }
        save_token_entry(accs)
        rich.print(accs)
        acs_tok = access_token

        url3 = f"https://api.tidal.com/v1/tracks/493546859/playbackinfopostpaywall?countryCode=en_US&audioquality={HI_RES}&playbackmode=STREAM&assetpresentation=FULL"

        headers = {
            "authorization": f"Bearer {acs_tok}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Platform": "android",
            "X-Tidal-Platform": "android",
        }

        async with httpx.AsyncClient(headers=headers) as client:
            res3 = await client.get(url3)

        rich.print(res3.json())
        print("TOKEN IS VALID")
        return True

    while True:
        success = await run_link_flow()
        if not success:
            break
        again = input("Add another token? (y/N): ").strip().lower()
        if again not in ("y", "yes"):
            break


if __name__ == "__main__":
    asyncio.run(main())
