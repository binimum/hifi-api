# hifi-api

![Running on BiniLossless.](https://sachinsenal0x64.github.io/picx-images-hosting/hifi.5fkz01pkwn.webp)

<p align="center">Running on <a href="https://tidal.squid.wtf/">SQUID.WTF</a>.</p>

`hifi-api` is forked from the original project [sachinsenal0x64/hifi](https://github.com/sachinsenal0x64/hifi).

> [!IMPORTANT]
> Music piracy is illegal in most countries. This project is intended for use with a valid Tidal account for educational purposes (for example, in your homelab).

## Setup

Run `pip install -r requirements.txt` in `tidal_auth/`, then run `tidal_auth/tidal_auth.py` and follow the instructions. The script creates/updates `token.json`.

Install main API dependencies with `pip install -r requirements.txt` in the project root.

Run the server with:

```bash
python3 main.py
```

By default, it listens on `0.0.0.0:8000` (could be the open internet - beware!).

## API Schema

These responses are samples and you should host the API yourself.

### `GET /`

#### Params

None.

#### Response

`200 OK`

```json
{
  "version": "2.x",
  "Repo": "https://github.com/binimum/hifi-api"
}
```

### `GET /info/`

Returns info about a track given ID.

#### Params

- `id`: `int` (required) - Tidal track ID.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "data": {
    "id": 144371283,
    "title": "Don't Look Back In Anger",
    "duration": 328,
    "replayGain": -10.46,
    "peak": 0.999969,
    "allowStreaming": true,
    "streamReady": true,
    "payToStream": false,
    "adSupportedStreamReady": true,
    "djReady": true,
    "stemReady": false,
    "streamStartDate": "2020-08-11T00:00:00.000+0000",
    "premiumStreamingOnly": false,
    "trackNumber": 10,
    "volumeNumber": 1,
    "version": "Live at Wembley Stadium, July 2000",
    "popularity": 51,
    "copyright": "(P) 2000 Big Brother Recordings Ltd",
    "bpm": 86,
    "key": "C",
    "keyScale": "MAJOR",
    "url": "http://www.tidal.com/track/144371283",
    "isrc": "GBBQY0002027",
    "editable": false,
    "explicit": true,
    "audioQuality": "LOSSLESS",
    "audioModes": [
      "STEREO"
    ],
    "mediaMetadata": {
      "tags": [
        "LOSSLESS"
      ]
    },
    "upload": false,
    "accessType": "PUBLIC",
    "spotlighted": false,
    "artist": {
      "id": 109,
      "name": "Oasis",
      "handle": null,
      "type": "MAIN",
      "picture": "0491c8eb-c16f-409c-915d-36a79d9e6384"
    },
    "artists": [
      {
        "id": 109,
        "name": "Oasis",
        "handle": null,
        "type": "MAIN",
        "picture": "0491c8eb-c16f-409c-915d-36a79d9e6384"
      }
    ],
    "album": {
      "id": 144371273,
      "title": "Familiar To Millions (Live)",
      "cover": "8f2d544e-2452-46de-ba70-25498434e2ef",
      "vibrantColor": "#cb8784",
      "videoCover": null
    },
    "mixes": {
      "TRACK_MIX": "0010f77179063ef106e2efaac9507a"
    }
  }
}
```

### `GET /track/`

#### Params

- `id`: `int` (required) - Tidal track ID.
- `quality`: `str` (optional, default `HI_RES_LOSSLESS`) - `HI_RES_LOSSLESS`, `LOSSLESS`, `HIGH`, `LOW`.

#### Response

##### CD Lossless/AAC

```json
{
    "version": "2.0",
    "data": {
        "trackId": 48717877,
        "assetPresentation": "FULL",
        "audioMode": "STEREO",
        "audioQuality": "LOSSLESS",
        "manifestMimeType": "application/vnd.tidal.bts",
        "manifestHash": "/smSLXXzSAVB+EsSVgyRzxtDuDo9rxPAH7n4tDwuXU4=",
        "manifest": "eyJtaW1lVHlwZSI6ImF1ZGlvL2ZsYWMiLCJjb2RlY3MiOiJmbGFjIiwiZW5jcnlwdGlvblR5cGUiOiJOT05FIiwidXJscyI6WyJodHRwczovL2xnZi5hdWRpby50aWRhbC5jb20vbWVkaWF0cmFja3MvQ0FFYUt3Z0RFaWRtWWpSaVpUQmlOalUzWWpRNE4yUTVNREJsWkdKaE56bGhPR0ppT1dNME1WODJNUzV0Y0RRLzAuZmxhYz90b2tlbj0xNzY2ODcwMDU3fk5UVmlNamhtWWpkak9UTmlOV1U0TVRNM1l6SXdOVGN4TTJRM05qVmhOakptWTJFeU5EWXdNZz09Il19",
        "albumReplayGain": -12.41,
        "albumPeakAmplitude": 0.999969,
        "trackReplayGain": -11.07,
        "trackPeakAmplitude": 0.999969,
        "bitDepth": 16,
        "sampleRate": 44100
    }
}
```

Where `manifest` is either base64 encoded JSON (use `"manifestMimeType": "application/vnd.tidal.bts"` to identify).

###### Decoded Manifest (formatted)

```json
{
  "mimeType": "audio/flac",
  "codecs": "flac",
  "encryptionType": "NONE",
  "urls": [
    "https://lgf.audio.tidal.com/mediatracks/CAEaKwgDEidmYjRiZTBiNjU3YjQ4N2Q5MDBlZGJhNzlhOGJiOWM0MV82MS5tcDQ/0.flac?token=1766870057~NTViMjhmYjdjOTNiNWU4MTM3YzIwNTcxM2Q3NjVhNjJmY2EyNDYwMg=="
  ]
}
```

##### CD Lossless/Hi-Res Lossless

```json
{
    "version": "2.0",
    "data": {
        "trackId": 194567102,
        "assetPresentation": "FULL",
        "audioMode": "STEREO",
        "audioQuality": "HI_RES_LOSSLESS",
        "manifestMimeType": "application/dash+xml",
        "manifestHash": "yyQEQ8ZX8ITLjQfFu0ADBdh/y03PpUd0NEPBz7RcuHk=",
        "manifest": "PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0nVVRGLTgnPz48TVBEIHhtbG5zPSJ1cm46bXBlZzpkYXNoOnNjaGVtYTptcGQ6MjAxMSIgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHhtbG5zOmNlbmM9InVybjptcGVnOmNlbmM6MjAxMyIgeHNpOnNjaGVtYUxvY2F0aW9uPSJ1cm46bXBlZzpkYXNoOnNjaGVtYTptcGQ6MjAxMSBEQVNILU1QRC54c2QiIHByb2ZpbGVzPSJ1cm46bXBlZzpkYXNoOnByb2ZpbGU6aXNvZmYtbWFpbjoyMDExIiB0eXBlPSJzdGF0aWMiIG1pbkJ1ZmZlclRpbWU9IlBUMy45OTNTIiBtZWRpYVByZXNlbnRhdGlvbkR1cmF0aW9uPSJQVDJNNDIuODc5UyI+PFBlcmlvZCBpZD0iMCI+PEFkYXB0YXRpb25TZXQgaWQ9IjAiIGNvbnRlbnRUeXBlPSJhdWRpbyIgbWltZVR5cGU9ImF1ZGlvL21wNCIgc2VnbWVudEFsaWdubWVudD0idHJ1ZSI+PFJlcHJlc2VudGF0aW9uIGlkPSIwIiBjb2RlY3M9ImZsYWMiIGJhbmR3aWR0aD0iMTY2NzU1MyIgYXVkaW9TYW1wbGluZ1JhdGU9IjQ0MTAwIj48U2VnbWVudFRlbXBsYXRlIHRpbWVzY2FsZT0iNDQxMDAiIGluaXRpYWxpemF0aW9uPSJodHRwczovL3NwLWFkLWNmLmF1ZGlvLnRpZGFsLmNvbS9tZWRpYXRyYWNrcy9HaXNJQXhJbk9XWTBNVGs1WXpVMFpESmpaRGhqTm1RM1ptWXdOV0ZsTVdVNVpqTXpOR1ZmTmpJdWJYQTBJaUFkQUFDQVFDQUNLaENoT1h0R0VnMjNPV3duT3lra0lRRG1NZ1VOQUFDZ1FRLzAubXA0P1BvbGljeT1leUpUZEdGMFpXMWxiblFpT2lCYmV5SlNaWE52ZFhKalpTSTZJbWgwZEhCek9pOHZjM0F0WVdRdFkyWXVZWFZrYVc4dWRHbGtZV3d1WTI5dEwyMWxaR2xoZEhKaFkydHpMMGRwYzBsQmVFbHVUMWRaTUUxVWF6VlplbFV3V2tSS2FscEVhR3BPYlZFeldtMVpkMDVYUm14TlYxVTFXbXBOZWs1SFZtWk9ha2wxWWxoQk1FbHBRV1JCUVVOQlVVTkJRMHRvUTJoUFdIUkhSV2N5TTA5WGQyNVBlV3RyU1ZGRWJVMW5WVTVCUVVOblVWRXZLaUlzSWtOdmJtUnBkR2x2YmlJNmV5SkVZWFJsVEdWemMxUm9ZVzRpT25zaVFWZFRPa1Z3YjJOb1ZHbHRaU0k2TVRjMk5qZzNNRFEzTW4xOWZWMTkmYW1wO1NpZ25hdHVyZT12WH51cFNqWEJVVVRKMmdTMGRoTnVrY1ozLUNIaFNNd2ozUzIzWXVzNGpaMEV3QlNiZEJXT2xmeW5yWmxOYnQ2V0t0QjA4OGppZzM5d1YteHpERUx5RHlnTk4zb2E4Zk01cDVVaFQ3T0JKUWc2Q35pSzlEZ3FleE9ka3ZzeEpMbVlOUFdSYzJ2Qkt+TGRPbG1qNVVybEdmbGhYUHRZTn42d2g0aWQ3MHlQcllyVkNHdFZJT1ZzZlAyanpHRDFNM1EyVTkxMGNuOWdPYU15aU9YSUtncDl4MXhFajhEZW9QVDZPY3hiNC1HfmtBUzBhTDlJSFlNdn42RjMzWnU1Si1KdTFIQmN3MmNHV1IwVWZiNHM0ZUpEaE1kdWxHT1hLRmROVVlkdHVqZGdpcXBiSWlXajVWaUNieHJZa1JQVEZ0OXdncS1yMnVRWE1wOGFIZzd2MFZOV1FfXyZhbXA7S2V5LVBhaXItSWQ9SzE0TFpDWjlRVUk0SkwiIG1lZGlhPSJodHRwczovL3NwLWFkLWNmLmF1ZGlvLnRpZGFsLmNvbS9tZWRpYXRyYWNrcy9HaXNJQXhJbk9XWTBNVGs1WXpVMFpESmpaRGhqTm1RM1ptWXdOV0ZsTVdVNVpqTXpOR1ZmTmpJdWJYQTBJaUFkQUFDQVFDQUNLaENoT1h0R0VnMjNPV3duT3lra0lRRG1NZ1VOQUFDZ1FRLyROdW1iZXIkLm1wND9Qb2xpY3k9ZXlKVGRHRjBaVzFsYm5RaU9pQmJleUpTWlhOdmRYSmpaU0k2SW1oMGRIQnpPaTh2YzNBdFlXUXRZMll1WVhWa2FXOHVkR2xrWVd3dVkyOXRMMjFsWkdsaGRISmhZMnR6TDBkcGMwbEJlRWx1VDFkWk1FMVVhelZaZWxVd1drUkthbHBFYUdwT2JWRXpXbTFaZDA1WFJteE5WMVUxV21wTmVrNUhWbVpPYWtsMVlsaEJNRWxwUVdSQlFVTkJVVU5CUTB0b1EyaFBXSFJIUldjeU0wOVhkMjVQZVd0clNWRkViVTFuVlU1QlFVTm5VVkV2S2lJc0lrTnZibVJwZEdsdmJpSTZleUpFWVhSbFRHVnpjMVJvWVc0aU9uc2lRVmRUT2tWd2IyTm9WR2x0WlNJNk1UYzJOamczTURRM01uMTlmVjE5JmFtcDtTaWduYXR1cmU9dlh+dXBTalhCVVVUSjJnUzBkaE51a2NaMy1DSGhTTXdqM1MyM1l1czRqWjBFd0JTYmRCV09sZnluclpsTmJ0NldLdEIwODhqaWczOXdWLXh6REVMeUR5Z05OM29hOGZNNXA1VWhUN09CSlFnNkN+aUs5RGdxZXhPZGt2c3hKTG1ZTlBXUmMydkJLfkxkT2xtajVVcmxHZmxoWFB0WU5+NndoNGlkNzB5UHJZclZDR3RWSU9Wc2ZQMmp6R0QxTTNRMlU5MTBjbjlnT2FNeWlPWElLZ3A5eDF4RWo4RGVvUFQ2T2N4YjQtR35rQVMwYUw5SUhZTXZ+NkYzM1p1NUotSnUxSEJjdzJjR1dSMFVmYjRzNGVKRGhNZHVsR09YS0ZkTlVZZHR1amRnaXFwYklpV2o1VmlDYnhyWWtSUFRGdDl3Z3EtcjJ1UVhNcDhhSGc3djBWTldRX18mYW1wO0tleS1QYWlyLUlkPUsxNExaQ1o5UVVJNEpMIiBzdGFydE51bWJlcj0iMSI+PFNlZ21lbnRUaW1lbGluZT48UyBkPSIxNzYxMjgiIHI9IjM5Ii8+PFMgZD0iMTM3ODYwIi8+PC9TZWdtZW50VGltZWxpbmU+PC9TZWdtZW50VGVtcGxhdGU+PExhYmVsPkZMQUNfSElSRVM8L0xhYmVsPjwvUmVwcmVzZW50YXRpb24+PC9BZGFwdGF0aW9uU2V0PjwvUGVyaW9kPjwvTVBEPg==",
        "albumReplayGain": -8.91,
        "albumPeakAmplitude": 0.970377,
        "trackReplayGain": -8.91,
        "trackPeakAmplitude": 0.970377,
        "bitDepth": 24,
        "sampleRate": 44100
    }
}
```

Where `manifest` is base64 encoded MPD manifest (use `"manifestMimeType": "application/dash+xml"` to identify).

###### Decoded Manifest (formatted)

```xml
<?xml version='1.0' encoding='UTF-8'?>
<MPD
	xmlns="urn:mpeg:dash:schema:mpd:2011"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:xlink="http://www.w3.org/1999/xlink"
	xmlns:cenc="urn:mpeg:cenc:2013" xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd" profiles="urn:mpeg:dash:profile:isoff-main:2011" type="static" minBufferTime="PT3.993S" mediaPresentationDuration="PT2M42.879S">
	<Period id="0">
		<AdaptationSet id="0" contentType="audio" mimeType="audio/mp4" segmentAlignment="true">
			<Representation id="0" codecs="flac" bandwidth="1667553" audioSamplingRate="44100">
				<SegmentTemplate timescale="44100" initialization="https://sp-ad-cf.audio.tidal.com/mediatracks/GisIAxInOWY0MTk5YzU0ZDJjZDhjNmQ3ZmYwNWFlMWU5ZjMzNGVfNjIubXA0IiAdAACAQCACKhChOXtGEg23OWwnOykkIQDmMgUNAACgQQ/0.mp4?Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vc3AtYWQtY2YuYXVkaW8udGlkYWwuY29tL21lZGlhdHJhY2tzL0dpc0lBeEluT1dZME1UazVZelUwWkRKalpEaGpObVEzWm1Zd05XRmxNV1U1WmpNek5HVmZOakl1YlhBMElpQWRBQUNBUUNBQ0toQ2hPWHRHRWcyM09Xd25PeWtrSVFEbU1nVU5BQUNnUVEvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc2Njg3MDQ3Mn19fV19&amp;Signature=vX~upSjXBUUTJ2gS0dhNukcZ3-CHhSMwj3S23Yus4jZ0EwBSbdBWOlfynrZlNbt6WKtB088jig39wV-xzDELyDygNN3oa8fM5p5UhT7OBJQg6C~iK9DgqexOdkvsxJLmYNPWRc2vBK~LdOlmj5UrlGflhXPtYN~6wh4id70yPrYrVCGtVIOVsfP2jzGD1M3Q2U910cn9gOaMyiOXIKgp9x1xEj8DeoPT6Ocxb4-G~kAS0aL9IHYMv~6F33Zu5J-Ju1HBcw2cGWR0Ufb4s4eJDhMdulGOXKFdNUYdtujdgiqpbIiWj5ViCbxrYkRPTFt9wgq-r2uQXMp8aHg7v0VNWQ__&amp;Key-Pair-Id=K14LZCZ9QUI4JL" media="https://sp-ad-cf.audio.tidal.com/mediatracks/GisIAxInOWY0MTk5YzU0ZDJjZDhjNmQ3ZmYwNWFlMWU5ZjMzNGVfNjIubXA0IiAdAACAQCACKhChOXtGEg23OWwnOykkIQDmMgUNAACgQQ/$Number$.mp4?Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vc3AtYWQtY2YuYXVkaW8udGlkYWwuY29tL21lZGlhdHJhY2tzL0dpc0lBeEluT1dZME1UazVZelUwWkRKalpEaGpObVEzWm1Zd05XRmxNV1U1WmpNek5HVmZOakl1YlhBMElpQWRBQUNBUUNBQ0toQ2hPWHRHRWcyM09Xd25PeWtrSVFEbU1nVU5BQUNnUVEvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc2Njg3MDQ3Mn19fV19&amp;Signature=vX~upSjXBUUTJ2gS0dhNukcZ3-CHhSMwj3S23Yus4jZ0EwBSbdBWOlfynrZlNbt6WKtB088jig39wV-xzDELyDygNN3oa8fM5p5UhT7OBJQg6C~iK9DgqexOdkvsxJLmYNPWRc2vBK~LdOlmj5UrlGflhXPtYN~6wh4id70yPrYrVCGtVIOVsfP2jzGD1M3Q2U910cn9gOaMyiOXIKgp9x1xEj8DeoPT6Ocxb4-G~kAS0aL9IHYMv~6F33Zu5J-Ju1HBcw2cGWR0Ufb4s4eJDhMdulGOXKFdNUYdtujdgiqpbIiWj5ViCbxrYkRPTFt9wgq-r2uQXMp8aHg7v0VNWQ__&amp;Key-Pair-Id=K14LZCZ9QUI4JL" startNumber="1">
					<SegmentTimeline>
						<S d="176128" r="39"/>
						<S d="137860"/>
					</SegmentTimeline>
				</SegmentTemplate>
				<Label>FLAC_HIRES</Label>
			</Representation>
		</AdaptationSet>
	</Period>
</MPD>
```

### `GET /recommendations/`

Finds recommendations to play, given a song. Similar to the mix. Returns 20 songs.

#### Params

- `id`: `int` (required) - Tidal track ID.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "data": {
    "limit": 20,
    "offset": 0,
    "totalNumberOfItems": 26,
    "items": [
      {
        "track": {
          "id": 37160635,
          "title": "Under Pressure (Live at Wembley '86)",
          "duration": 221,
          "replayGain": -11.87,
          "peak": 0.980133,
          "allowStreaming": true,
          "streamReady": true,
          "payToStream": false,
          "adSupportedStreamReady": true,
          "djReady": true,
          "stemReady": false,
          "streamStartDate": "2003-08-19T00:00:00.000+0000",
          "premiumStreamingOnly": false,
          "trackNumber": 7,
          "volumeNumber": 1,
          "version": null,
          "popularity": 55,
          "copyright": "℗ 1986 Hollywood Records, Inc.",
          "bpm": 122,
          "key": "D",
          "keyScale": "MAJOR",
          "url": "http://www.tidal.com/track/37160635",
          "isrc": "GBCEE9200016",
          "editable": false,
          "explicit": false,
          "audioQuality": "LOSSLESS",
          "audioModes": [
            "STEREO"
          ],
          "mediaMetadata": {
            "tags": [
              "LOSSLESS"
            ]
          },
          "upload": false,
          "accessType": "PUBLIC",
          "spotlighted": false,
          "artist": {
            "id": 8992,
            "name": "Queen",
            "handle": null,
            "type": "MAIN",
            "picture": "6ac97166-8aae-458a-b1ea-cfcc9d3cfabf"
          },
          "artists": [
            {
              "id": 8992,
              "name": "Queen",
              "handle": null,
              "type": "MAIN",
              "picture": "6ac97166-8aae-458a-b1ea-cfcc9d3cfabf"
            }
          ],
          "album": {
            "id": 37160628,
            "title": "Live At Wembley Stadium",
            "cover": "c810ba36-a324-4f11-ac82-ab7eeacefb64",
            "vibrantColor": "#c49839",
            "videoCover": null
          },
          "mixes": {
            "TRACK_MIX": "0013f3c9f7ced02e0d9a90e41d95a8"
          }
        },
        "sources": [
          "SUGGESTED_TRACKS"
        ]
      },
      <truncated>
    ]
  }
}
```

### `GET /search/`

#### Params

Specify only one of the following query fields:

- `s`: `str` - track query
- `a`: `str` - artist query
- `al`: `str` - album query
- `v`: `str` - video query
- `p`: `str` - playlist query
- `i`: `str` - ISRC query (exact lookup via `/v1/tracks?filter[isrc]`)

Pagination:

- `offset`: `int` (optional, default `0`, min `0`)
- `limit`: `int` (optional, default `25`, min `1`, max `500`)

#### Response

`200 OK`

##### Track

```json
{
  "version": "2.6",
  "data": {
    "limit": 25,
    "offset": 0,
    "totalNumberOfItems": 300,
    "items": [
      {
        "id": 427520487,
        "title": "Azizam",
        "duration": 162,
        "replayGain": -9.95,
        "peak": 0.988554,
        "allowStreaming": true,
        "streamReady": true,
        "payToStream": false,
        "adSupportedStreamReady": true,
        "djReady": true,
        "stemReady": false,
        "streamStartDate": "2025-04-04T00:00:00.000+0000",
        "premiumStreamingOnly": false,
        "trackNumber": 1,
        "volumeNumber": 1,
        "version": null,
        "popularity": 80,
        "copyright": "Gingerbread Man Records and Atlantic Records UK release, under exclusive licence to Warner Music UK Limited, ℗ 2025 Ed Sheeran Limited",
        "bpm": 128,
        "key": "F",
        "keyScale": "MAJOR",
        "url": "http://www.tidal.com/track/427520487",
        "isrc": "GBAHS2500081",
        "editable": false,
        "explicit": false,
        "audioQuality": "LOSSLESS",
        "audioModes": [
          "STEREO"
        ],
        "mediaMetadata": {
          "tags": [
            "LOSSLESS",
            "HIRES_LOSSLESS"
          ]
        },
        "upload": false,
        "accessType": null,
        "spotlighted": false,
        "artist": {
          "id": 3995478,
          "name": "Ed Sheeran",
          "handle": null,
          "type": "MAIN",
          "picture": "05d72ae4-319f-4237-821f-1d7af9ec8acf"
        },
        "artists": [
          {
            "id": 3995478,
            "name": "Ed Sheeran",
            "handle": null,
            "type": "MAIN",
            "picture": "05d72ae4-319f-4237-821f-1d7af9ec8acf"
          }
        ],
        "album": {
          "id": 427520486,
          "title": "Azizam",
          "cover": "5a2d656d-f965-48ba-a241-bce5ad432015",
          "vibrantColor": "#db899c",
          "videoCover": null
        },
        "mixes": {
          "TRACK_MIX": "001098c806426de17f57eb9d79b8ec"
        }
      },
      <truncated>
    ]
  }
}
```

##### Artist

```json
{
  "version": "2.6",
  "data": {
    "artists": {
      "limit": 25,
      "offset": 0,
      "totalNumberOfItems": 73,
      "items": [
        {
          "id": 8812,
          "name": "Coldplay",
          "artistTypes": [
            "ARTIST",
            "CONTRIBUTOR"
          ],
          "url": "http://www.tidal.com/artist/8812",
          "picture": "b4579672-5b91-4679-a27a-288f097a4da5",
          "selectedAlbumCoverFallback": null,
          "popularity": 92,
          "artistRoles": [
            {
              "categoryId": -1,
              "category": "Artist"
            },
            {
              "categoryId": 1,
              "category": "Producer"
            },
            {
              "categoryId": 11,
              "category": "Performer"
            },
            {
              "categoryId": 2,
              "category": "Songwriter"
            },
            {
              "categoryId": 10,
              "category": "Production team"
            },
            {
              "categoryId": 99,
              "category": "Misc"
            }
          ],
          "mixes": {
            "ARTIST_MIX": "000d63462309f499a611e73b4992bd"
          },
          "handle": null,
          "userId": null,
          "spotlighted": false
        },
        {
          "id": 39476431,
          "name": "Coldplay Piano Covers",
          "artistTypes": [
            "ARTIST",
            "CONTRIBUTOR"
          ],
          "url": "http://www.tidal.com/artist/39476431",
          "picture": "3e88ec5b-0058-4185-8c1c-385098528f40",
          "selectedAlbumCoverFallback": "3e88ec5b-0058-4185-8c1c-385098528f40",
          "popularity": 28,
          "artistRoles": [
            {
              "categoryId": -1,
              "category": "Artist"
            }
          ],
          "mixes": {

          },
          "handle": null,
          "userId": null,
          "spotlighted": false
        },
        <truncated>
    ]
  }
}
```

### `GET /album/`

#### Params

- `id`: `int` (required) - album ID.
- `limit`: `int` (optional, default `100`, min `1`, max `500`) - number of album items.
- `offset`: `int` (optional, default `0`, min `0`) - item offset.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "data": {
    "id": 58990510,
    "title": "OK Computer",
    "duration": 3216,
    "streamReady": true,
    "payToStream": false,
    "adSupportedStreamReady": true,
    "djReady": true,
    "stemReady": false,
    "streamStartDate": "2023-11-21T00:00:00.000+0000",
    "allowStreaming": true,
    "premiumStreamingOnly": false,
    "numberOfTracks": 12,
    "numberOfVideos": 0,
    "numberOfVolumes": 1,
    "releaseDate": "1997-07-01",
    "copyright": "XL Recordings Ltd",
    "type": "ALBUM",
    "version": null,
    "url": "http://www.tidal.com/album/58990510",
    "cover": "e77e4cc0-6cd0-4522-807d-88aeac488065",
    "vibrantColor": "#a8cada",
    "videoCover": null,
    "explicit": false,
    "upc": "634904078164",
    "popularity": 83,
    "audioQuality": "LOSSLESS",
    "audioModes": [
      "STEREO"
    ],
    "mediaMetadata": {
      "tags": [
        "LOSSLESS"
      ]
    },
    "upload": false,
    "artist": {
      "id": 64518,
      "name": "Radiohead",
      "handle": null,
      "type": "MAIN",
      "picture": "600a6117-32bb-4f9a-ac2b-206cbf1db419"
    },
    "artists": [
      {
        "id": 64518,
        "name": "Radiohead",
        "handle": null,
        "type": "MAIN",
        "picture": "600a6117-32bb-4f9a-ac2b-206cbf1db419"
      }
    ],
    "items": [
      {
        "item": {
          "id": 58990511,
          "title": "Airbag",
          "duration": 287,
          "replayGain": -10.77,
          "peak": 0.980682,
          "allowStreaming": true,
          "streamReady": true,
          "payToStream": false,
          "adSupportedStreamReady": true,
          "djReady": true,
          "stemReady": false,
          "streamStartDate": "2023-11-21T00:00:00.000+0000",
          "premiumStreamingOnly": false,
          "trackNumber": 1,
          "volumeNumber": 1,
          "version": null,
          "popularity": 74,
          "copyright": "XL Recordings Ltd",
          "bpm": 166,
          "key": "A",
          "keyScale": null,
          "url": "http://www.tidal.com/track/58990511",
          "isrc": "GBAYE9701274",
          "editable": false,
          "explicit": false,
          "audioQuality": "LOSSLESS",
          "audioModes": [
            "STEREO"
          ],
          "mediaMetadata": {
            "tags": [
              "LOSSLESS"
            ]
          },
          "upload": false,
          "accessType": "PUBLIC",
          "spotlighted": false,
          "artist": {
            "id": 64518,
            "name": "Radiohead",
            "handle": null,
            "type": "MAIN",
            "picture": "0968a9dd-9536-4bc2-84a2-ab65c8926bdc"
          },
          "artists": [
            {
              "id": 64518,
              "name": "Radiohead",
              "handle": null,
              "type": "MAIN",
              "picture": "0968a9dd-9536-4bc2-84a2-ab65c8926bdc"
            }
          ],
          "album": {
            "id": 58990510,
            "title": "OK Computer",
            "cover": "e77e4cc0-6cd0-4522-807d-88aeac488065",
            "vibrantColor": "#a8cada",
            "videoCover": null
          },
          "mixes": {
            "TRACK_MIX": "0015963a9a23be922134195a634872"
          }
        },
        "type": "track"
      },
      <truncated>
    ]
  }
}
```

### `GET /mix/`

Kind of like recommendations, except they are usually 60 tracks.

#### Params

- `id`: `str` (required) - mix ID.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "mix": {
    "id": "0019a6f811ccf59fd0346967a1dea7",
    "title": "Subterranean Homesick Alien",
    "subTitle": "Radiohead",
    "description": null,
    "graphic": {
      "type": "SQUARES_GRID",
      "text": "Subterranean Homesick Alien",
      "images": [
        {
          "id": "dummy-placeholder",
          "vibrantColor": "#FFFFFF",
          "type": "ARTIST"
        }
      ]
    },
    "images": {
      "SMALL": {
        "width": 320,
        "height": 320,
        "url": "https://images.tidal.com/0/EMACGMACIKABKKAB/CAEQBhokZTc3ZTRjYzAvNmNkMC80NTIyLzgwN2QvODhhZWFjNDg4MDY1GiRiMjFmZDJmYy8yZDc2LzRlYmMvYTQzNC84Njg2YzQ3NWZjMTAaJDY4NWYxZjRjLzI5NTYvNDBlNi9iODFjL2ZmYzU0MGQ2NjA2ZCILVHJhY2sgUmFkaW8iG1N1YnRlcnJhbmVhbiBIb21lc2ljayBBbGllbioHI0E4Q0FEQTAC?token=8414f91d1fe7b2e31719b2567707cab310bbe2e9"
      },
      "MEDIUM": {
        "width": 640,
        "height": 640,
        "url": "https://images.tidal.com/0/EIAFGIAFIMACKMAC/CAEQBhokZTc3ZTRjYzAvNmNkMC80NTIyLzgwN2QvODhhZWFjNDg4MDY1GiRiMjFmZDJmYy8yZDc2LzRlYmMvYTQzNC84Njg2YzQ3NWZjMTAaJDY4NWYxZjRjLzI5NTYvNDBlNi9iODFjL2ZmYzU0MGQ2NjA2ZCILVHJhY2sgUmFkaW8iG1N1YnRlcnJhbmVhbiBIb21lc2ljayBBbGllbioHI0E4Q0FEQTAC?token=518de937f6ae775faec893fdc709d4ad146b5e34"
      },
      "LARGE": {
        "width": 1500,
        "height": 1500,
        "url": "https://images.tidal.com/0/ENwLGNwLIO4FKO4F/CAEQBhokZTc3ZTRjYzAvNmNkMC80NTIyLzgwN2QvODhhZWFjNDg4MDY1GiRiMjFmZDJmYy8yZDc2LzRlYmMvYTQzNC84Njg2YzQ3NWZjMTAaJDY4NWYxZjRjLzI5NTYvNDBlNi9iODFjL2ZmYzU0MGQ2NjA2ZCILVHJhY2sgUmFkaW8iG1N1YnRlcnJhbmVhbiBIb21lc2ljayBBbGllbioHI0E4Q0FEQTAC?token=cbfbe06ee9b1e54e59ffb4bd4eaca73b027b7842"
      }
    },
    "sharingImages": null,
    "mixType": "TRACK_MIX",
    "mixNumber": null,
    "contentBehavior": "UNRESTRICTED",
    "master": false,
    "titleColor": "#A8CADA",
    "subTitleColor": "#A8CADA",
    "descriptionColor": null,
    "detailImages": {
      "SMALL": {
        "width": 320,
        "height": 320,
        "url": "https://images.tidal.com/0/EMACGMACIKABKKAB/CAEQBhokZTc3ZTRjYzAvNmNkMC80NTIyLzgwN2QvODhhZWFjNDg4MDY1GiRiMjFmZDJmYy8yZDc2LzRlYmMvYTQzNC84Njg2YzQ3NWZjMTAaJDY4NWYxZjRjLzI5NTYvNDBlNi9iODFjL2ZmYzU0MGQ2NjA2ZCILVHJhY2sgUmFkaW8iG1N1YnRlcnJhbmVhbiBIb21lc2ljayBBbGllbioHI0E4Q0FEQTACOAE?token=daf8f7b393c2285944a7e0c05eb79c2a47b027df"
      },
      "MEDIUM": {
        "width": 640,
        "height": 640,
        "url": "https://images.tidal.com/0/EIAFGIAFIMACKMAC/CAEQBhokZTc3ZTRjYzAvNmNkMC80NTIyLzgwN2QvODhhZWFjNDg4MDY1GiRiMjFmZDJmYy8yZDc2LzRlYmMvYTQzNC84Njg2YzQ3NWZjMTAaJDY4NWYxZjRjLzI5NTYvNDBlNi9iODFjL2ZmYzU0MGQ2NjA2ZCILVHJhY2sgUmFkaW8iG1N1YnRlcnJhbmVhbiBIb21lc2ljayBBbGllbioHI0E4Q0FEQTACOAE?token=3405ef092d0afa08bebb431aa7489b0399470b50"
      },
      "LARGE": {
        "width": 1500,
        "height": 1500,
        "url": "https://images.tidal.com/0/ENwLGNwLIO4FKO4F/CAEQBhokZTc3ZTRjYzAvNmNkMC80NTIyLzgwN2QvODhhZWFjNDg4MDY1GiRiMjFmZDJmYy8yZDc2LzRlYmMvYTQzNC84Njg2YzQ3NWZjMTAaJDY4NWYxZjRjLzI5NTYvNDBlNi9iODFjL2ZmYzU0MGQ2NjA2ZCILVHJhY2sgUmFkaW8iG1N1YnRlcnJhbmVhbiBIb21lc2ljayBBbGllbioHI0E4Q0FEQTACOAE?token=af709901ccac4866e329df7d082a6601d73bf10a"
      }
    },
    "shortSubtitle": "Created by TIDAL"
  },
  "items": [
    {
      "id": 58990513,
      "title": "Subterranean Homesick Alien",
      "duration": 267,
      "version": null,
      "url": "https://tidal.com/browse/track/58990513",
      "artists": [
        {
          "id": 64518,
          "name": "Radiohead",
          "type": "MAIN",
          "picture": "0968a9dd-9536-4bc2-84a2-ab65c8926bdc",
          "handle": null,
          "userId": null
        }
      ],
      "album": {
        "id": 58990510,
        "title": "OK Computer",
        "cover": "e77e4cc0-6cd0-4522-807d-88aeac488065",
        "vibrantColor": "#a8cada",
        "videoCover": null,
        "url": "https://tidal.com/browse/album/58990510",
        "releaseDate": "1997-07-01"
      },
      "explicit": false,
      "volumeNumber": 1,
      "trackNumber": 3,
      "popularity": 76,
      "doublePopularity": 0.7603010414769,
      "allowStreaming": true,
      "streamReady": true,
      "streamStartDate": "2023-11-21T00:00:00.000+0000",
      "adSupportedStreamReady": true,
      "djReady": true,
      "stemReady": false,
      "editable": false,
      "replayGain": -10.77,
      "audioQuality": "LOSSLESS",
      "audioModes": [
        "STEREO"
      ],
      "mixes": {
        "TRACK_MIX": "0019a6f811ccf59fd0346967a1dea7"
      },
      "mediaMetadata": {
        "tags": [
          "LOSSLESS"
        ]
      },
      "upload": false,
      "payToStream": false,
      "accessType": "PUBLIC",
      "spotlighted": false
    },
    <truncated>
  ]
}
```

### `GET /playlist/`

#### Params

- `id`: `str` (required) - playlist UUID.
- `limit`: `int` (optional, default `100`, min `1`, max `500`) - number of playlist items.
- `offset`: `int` (optional, default `0`, min `0`) - item offset.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "playlist": {
    "uuid": "626d146b-04f6-4936-bbf6-a65318f740a1",
    "title": "2010s Pop Hits",
    "numberOfTracks": 100,
    "numberOfVideos": 0,
    "creator": {
      "id": 0
    },
    "description": "The biggest, brightest, and baddest pop hits from the past decade. (Cover: Bruno Mars // Photo: Atlantic Records/Press)",
    "duration": 22651,
    "lastUpdated": "2025-01-27T17:15:24.016+0000",
    "created": "2019-12-13T05:38:27.800+0000",
    "type": "EDITORIAL",
    "publicPlaylist": true,
    "url": "http://www.tidal.com/playlist/626d146b-04f6-4936-bbf6-a65318f740a1",
    "image": "dafff826-e77d-4847-bf56-ad5e2f5c377c",
    "popularity": 0,
    "squareImage": "b15bb487-dd6e-45ff-9e50-ee5083f20669",
    "customImageUrl": null,
    "promotedArtists": [
      {
        "id": 8722,
        "name": "Mark Ronson",
        "handle": null,
        "type": "MAIN",
        "picture": null
      },
      {
        "id": 4332277,
        "name": "Ariana Grande",
        "handle": null,
        "type": "MAIN",
        "picture": null
      },
      {
        "id": 3531205,
        "name": "Katy Perry",
        "handle": null,
        "type": "MAIN",
        "picture": null
      },
      {
        "id": 10665,
        "name": "Rihanna",
        "handle": null,
        "type": "MAIN",
        "picture": null
      }
    ],
    "lastItemAddedAt": "2025-01-22T04:12:16.941+0000"
  },
  "items": [
    {
      "item": {
        "id": 39249713,
        "title": "Uptown Funk (feat. Bruno Mars)",
        "duration": 270,
        "replayGain": -7.79,
        "peak": 0.94406,
        "allowStreaming": true,
        "streamReady": true,
        "payToStream": false,
        "adSupportedStreamReady": true,
        "djReady": true,
        "stemReady": false,
        "streamStartDate": "2015-01-13T00:00:00.000+0000",
        "premiumStreamingOnly": false,
        "trackNumber": 4,
        "volumeNumber": 1,
        "version": null,
        "popularity": 91,
        "copyright": "(P) 2014 Mark Ronson under exclusive licence to Sony Music Entertainment UK Limited",
        "bpm": 115,
        "key": "C",
        "keyScale": "MAJOR",
        "description": null,
        "url": "http://www.tidal.com/track/39249713",
        "isrc": "GBARL1401524",
        "editable": false,
        "explicit": false,
        "audioQuality": "LOSSLESS",
        "audioModes": [
          "STEREO"
        ],
        "mediaMetadata": {
          "tags": [
            "LOSSLESS",
            "HIRES_LOSSLESS"
          ]
        },
        "upload": false,
        "accessType": "PUBLIC",
        "spotlighted": false,
        "artist": {
          "id": 8722,
          "name": "Mark Ronson",
          "handle": null,
          "type": "MAIN",
          "picture": "94adc4e5-b2ab-475d-b2e6-ecb96a77ebcc"
        },
        "artists": [
          {
            "id": 8722,
            "name": "Mark Ronson",
            "handle": null,
            "type": "MAIN",
            "picture": "94adc4e5-b2ab-475d-b2e6-ecb96a77ebcc"
          },
          {
            "id": 3658521,
            "name": "Bruno Mars",
            "handle": null,
            "type": "FEATURED",
            "picture": "12139dfb-f192-4481-9794-c9fb7d1e2476"
          }
        ],
        "album": {
          "id": 39249709,
          "title": "Uptown Special",
          "cover": "2f507eba-07f8-4bf5-a32b-9aa5c1a9840d",
          "vibrantColor": "#f0e76a",
          "videoCover": null,
          "releaseDate": "2015-01-26"
        },
        "mixes": {
          "TRACK_MIX": "001f7dfc4bcd0b25da782de2e5045f"
        },
        "dateAdded": "2023-03-01T23:23:53.167+0000",
        "index": 25000,
        "itemUuid": "729ba2c2-cad0-4e90-a0c3-dd8d1f76c069"
      },
      "type": "track",
      "cut": null
    },
    <truncated>
  ]
}
```

### `GET /artist/similar/`

#### Params

- `id`: `int` (required) - artist ID.
- `cursor`: `int | str` (optional) - cursor for paginated results.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "artists": [
    {
      "name": "Beyoncé",
      "popularity": 0.958293782719296,
      "externalLinks": [
        {
          "href": "https://tidal.com/browse/artist/1566",
          "meta": {
            "type": "TIDAL_SHARING"
          }
        }
      ],
      "spotlighted": false,
      "contributionsEnabled": false,
      "ownerType": "LABEL",
      "id": 1566,
      "picture": "3e712fb2-9610-4cab-ac20-fb63cfcaa45f",
      "url": "http://www.tidal.com/artist/1566",
      "relationType": "SIMILAR_ARTIST"
    },
    <truncated>
  ]
}
```

### `GET /album/similar/`

#### Params

- `id`: `int` (required) - album ID.
- `cursor`: `int | str` (optional) - cursor for paginated results.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "albums": [
    {
      "title": "The College Dropout",
      "barcodeId": "00602567922186",
      "numberOfVolumes": 1,
      "numberOfItems": 21,
      "duration": "PT1H16M24S",
      "explicit": true,
      "releaseDate": "2004-02-10",
      "copyright": {
        "text": "© 2004 UMG Recordings, Inc."
      },
      "popularity": 0.849979392325809,
      "accessType": "PUBLIC",
      "availability": [
        "STREAM",
        "DJ"
      ],
      "mediaTags": [
        "LOSSLESS"
      ],
      "externalLinks": [
        {
          "href": "https://tidal.com/browse/album/92099357",
          "meta": {
            "type": "TIDAL_SHARING"
          }
        }
      ],
      "type": "ALBUM",
      "albumType": "ALBUM",
      "createdAt": "2018-07-16T21:57:06Z",
      "id": 92099357,
      "cover": "cc77193c-a074-4538-a8b5-307b2a44169e",
      "artists": [
        {
          "id": 25022,
          "name": "Kanye West"
        }
      ],
      "url": "http://www.tidal.com/album/92099357"
    },
    <truncated>
  ]
}
```

### `GET /artist/`

#### Params

Provide `id` or `f`.

- `id`: `int` (optional) - fetch artist metadata and generated cover URL.
- `f`: `int` (optional) - fetch artist releases and aggregate tracks.
- `skip_tracks`: `bool` (optional, default `false`) - with `f`, skip album-track aggregation and return top tracks.

#### Response

##### Mode A (`id` provided)

`200 OK`

```json
{
  "version": "2.6",
  "artist": {
    "id": 25022,
    "name": "Kanye West",
    "artistTypes": [
      "ARTIST",
      "CONTRIBUTOR"
    ],
    "url": "http://www.tidal.com/artist/25022",
    "picture": "0948decd-5591-4b83-b188-8314bfbe7fd3",
    "selectedAlbumCoverFallback": null,
    "popularity": 96,
    "artistRoles": [
      {
        "categoryId": -1,
        "category": "Artist"
      },
      {
        "categoryId": 2,
        "category": "Songwriter"
      },
      {
        "categoryId": 1,
        "category": "Producer"
      },
      {
        "categoryId": 11,
        "category": "Performer"
      },
      {
        "categoryId": 10,
        "category": "Production team"
      },
      {
        "categoryId": 3,
        "category": "Engineer"
      },
      {
        "categoryId": 99,
        "category": "Misc"
      }
    ],
    "mixes": {
      "ARTIST_MIX": "000a58346749c76f7f6f58bf9cef7a"
    },
    "handle": null,
    "userId": null,
    "spotlighted": false
  },
  "cover": {
    "id": 25022,
    "name": "Kanye West",
    "750": "https://resources.tidal.com/images/0948decd/5591/4b83/b188/8314bfbe7fd3/750x750.jpg"
  }
}
```

##### Mode B (`f` provided)

Response on this endpoint is much slower because it has to fetch much more metadata.

`200 OK`

```json
{
  "version": "2.6",
  "albums": {
    "items": [
      {
        "id": 440425318,
        "title": "DONDA 2",
        "duration": 3490,
        "streamReady": true,
        "payToStream": false,
        "adSupportedStreamReady": true,
        "djReady": true,
        "stemReady": false,
        "streamStartDate": "2025-06-06T00:00:00.000+0000",
        "allowStreaming": true,
        "premiumStreamingOnly": false,
        "numberOfTracks": 21,
        "numberOfVideos": 0,
        "numberOfVolumes": 1,
        "releaseDate": "2025-05-10",
        "copyright": "2025 YZY",
        "type": "ALBUM",
        "version": null,
        "url": "http://www.tidal.com/album/440425318",
        "cover": "e7a15eaf-494a-4535-ae0e-25f7221ba527",
        "vibrantColor": null,
        "videoCover": null,
        "explicit": true,
        "upc": "0692788674308",
        "popularity": 68,
        "audioQuality": "LOSSLESS",
        "audioModes": [
          "STEREO"
        ],
        "mediaMetadata": {
          "tags": [
            "LOSSLESS",
            "HIRES_LOSSLESS"
          ]
        },
        "upload": false,
        "artist": {
          "id": 5775484,
          "name": "Donda",
          "handle": null,
          "type": "MAIN",
          "picture": null
        },
        "artists": [
          {
            "id": 5775484,
            "name": "Donda",
            "handle": null,
            "type": "MAIN",
            "picture": null
          },
          {
            "id": 25022,
            "name": "Kanye West",
            "handle": null,
            "type": "MAIN",
            "picture": "0948decd-5591-4b83-b188-8314bfbe7fd3"
          },
          {
            "id": 5909698,
            "name": "Ye",
            "handle": null,
            "type": "MAIN",
            "picture": null
          }
        ]
      },
      <truncated>
    ]
  },
  "tracks": [
    {
      "id": 440425319,
      "title": "TRUE LOVE",
      "duration": 137,
      "version": null,
      "url": "https://tidal.com/browse/track/440425319",
      "artists": [
        {
          "id": 5775484,
          "name": "Donda",
          "type": "MAIN",
          "picture": null,
          "handle": null,
          "userId": null
        },
        {
          "id": 25022,
          "name": "Kanye West",
          "type": "MAIN",
          "picture": "0948decd-5591-4b83-b188-8314bfbe7fd3",
          "handle": null,
          "userId": null
        },
        {
          "id": 5909698,
          "name": "Ye",
          "type": "MAIN",
          "picture": null,
          "handle": null,
          "userId": null
        }
      ],
      "album": {
        "id": 440425318,
        "title": "DONDA 2",
        "cover": "e7a15eaf-494a-4535-ae0e-25f7221ba527",
        "vibrantColor": null,
        "videoCover": null,
        "url": "https://tidal.com/browse/album/440425318",
        "releaseDate": "2025-05-10"
      },
      "explicit": true,
      "volumeNumber": 1,
      "trackNumber": 1,
      "popularity": 49,
      "doublePopularity": 0.494079662855111,
      "allowStreaming": true,
      "streamReady": true,
      "streamStartDate": "2025-06-06T00:00:00.000+0000",
      "adSupportedStreamReady": true,
      "djReady": true,
      "stemReady": false,
      "editable": false,
      "replayGain": -9.41,
      "audioQuality": "LOSSLESS",
      "audioModes": [
        "STEREO"
      ],
      "mixes": {
        "TRACK_MIX": "00135a8af60167df440a30b939ce26"
      },
      "mediaMetadata": {
        "tags": [
          "LOSSLESS",
          "HIRES_LOSSLESS"
        ]
      },
      "upload": false,
      "payToStream": false,
      "accessType": "PUBLIC",
      "spotlighted": false
    },
    <truncated>
  ]
}
```

### `GET /cover/`

#### Params

Provide `id` or `q`.

- `id`: `int` (optional) - track ID.
- `q`: `str` (optional) - track search query.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "covers": [
    {
      "id": 311222965,
      "name": "Broke with Expensive Taste",
      "1280": "https://resources.tidal.com/images/c50c9146/3c7a/44e6/a1bc/55b20516eb29/1280x1280.jpg",
      "640": "https://resources.tidal.com/images/c50c9146/3c7a/44e6/a1bc/55b20516eb29/640x640.jpg",
      "80": "https://resources.tidal.com/images/c50c9146/3c7a/44e6/a1bc/55b20516eb29/80x80.jpg"
    }
  ]
}
```

### `GET /lyrics/`

#### Params

- `id`: `int` (required) - track ID.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "lyrics": {
    "trackId": 39249713,
    "lyricsProvider": "MUSIXMATCH",
    "providerCommontrackId": "190482820",
    "providerLyricsId": "37850929",
    "lyrics": "Doh\nDoh-doh-doh, doh-doh-doh, doh-doh\nDoh-doh-doh, doh-doh-doh, doh-doh\nDoh-doh-doh, doh-doh-doh, doh-doh\nDoh-doh-doh, doh-doh (ah, ow)\n\nThis hit, that ice-cold <truncated>",
    "subtitles": "[00:00.04] Doh\n[00:01.98] Doh-doh-doh, doh-doh-doh, doh-doh\n[00:05.93] Doh-doh-doh, doh-doh-doh, doh-doh\n[00:10.22] Doh-doh-doh, doh-doh-doh, doh-doh\n[00:14.44] Doh-doh-doh, doh-doh (ah, ow)\n[00:16.70] This hit, that ice-cold <truncated>",
    "isRightToLeft": false
  }
}
```

### `GET /topvideos/`

#### Params

- `countryCode`: `str` (optional, default `US`) - Tidal country code.
- `locale`: `str` (optional, default `en_US`) - locale.
- `deviceType`: `str` (optional, default `BROWSER`) - device type.
- `limit`: `int` (optional, default `25`, min `1`, max `100`) - videos per page.
- `offset`: `int` (optional, default `0`, min `0`) - pagination offset.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "videos": [
    {
      "id": "eyJwIjoiZmE1MjQ1ZTItYzgyYi00YWE2LTgwN2UtNDE5OTgyOGEyMmU1IiwicFYiOjQsIm0iOiIxMjNiMmI5Mi02NTkwLTQ2ZjMtOGE2Ny1jYjBjNmZlZDljYTMiLCJtViI6MSwibUgiOiJlZTYyYTZjYSJ9",
      "type": "VIDEO_LIST",
      "width": 100,
      "scroll": "VERTICAL",
      "title": "",
      "description": "",
      "showMore": null,
      "pagedList": {
        "dataApiPath": "pages/data/85db1b03-a853-4628-8836-9e883c6fa4bb",
        "limit": 100,
        "offset": 0,
        "totalNumberOfItems": 100,
        "items": [
          {
            "id": 402643865,
            "title": "Winter Ahead (with PARK HYO SHIN)",
            "duration": 372,
            "version": null,
            "url": "https://tidal.com/browse/video/402643865",
            "artists": [
              {
                "id": 29927033,
                "name": "V",
                "type": "MAIN",
                "picture": "fc9f21fd-0384-49c9-921c-ddbfce335156",
                "handle": null,
                "userId": null
              },
              {
                "id": 4239174,
                "name": "Park Hyo Shin",
                "type": "MAIN",
                "picture": "4f43f34e-7c53-4b24-9596-d25ce157f048",
                "handle": null,
                "userId": null
              }
            ],
            "album": null,
            "explicit": false,
            "volumeNumber": 0,
            "trackNumber": 0,
            "popularity": 52,
            "doublePopularity": 0.519117817177637,
            "allowStreaming": true,
            "streamReady": true,
            "streamStartDate": "2024-11-29T00:00:00.000+0000",
            "adSupportedStreamReady": true,
            "djReady": true,
            "stemReady": false,
            "imageId": "efba0086-c3b8-40bd-9b45-721945816ed3",
            "vibrantColor": "#f0090f",
            "releaseDate": "2024-11-29",
            "type": "Music Video",
            "adsUrl": null,
            "adsPrePaywallOnly": true
          },
          <truncated>
        ]
      },
      "supportsPaging": false,
      "showTableHeaders": false,
      "listFormat": null,
      "layout": null,
      "quickPlay": false,
      "preTitle": null
    }
  ],
  "total": 1
}
```

### `GET /video/`

> [!WARNING]
>
> This endpoint is - for some reason - heavily rate limited on Tidal's end. Take care.

#### Params

- `id`: `int` (required) - video ID.
- `quality`: `str` (optional, default `HIGH`) - `HIGH`, `MEDIUM`, `LOW`.
- `mode`: `str` (optional, default `STREAM`) - `STREAM`, `OFFLINE`.
- `presentation`: `str` (optional, default `FULL`) - `FULL`, `PREVIEW`.

#### Response

`200 OK`

```json
{
  "version": "2.6",
  "video": {
    "videoId": 48204106,
    "streamType": "ON_DEMAND",
    "assetPresentation": "FULL",
    "videoQuality": "HIGH",
    "manifestMimeType": "application/vnd.tidal.emu",
    "manifestHash": "fU3b2NNlidH7ZvUhBSKbJCuDlTeOay1RPqptFQLTt1U=",
    "manifest": "eyJtaW1lVHlwZSI6ImFwcGxpY2F0aW9uL3ZuZC5hcHBsZS5tcGVndXJsIiwidXJscyI6WyJodHRwczovL2ltLWZhLm1hbmlmZXN0LnRpZGFsLmNvbS8xL21hbmlmZXN0cy9DQUVTQ0RRNE1qQTBNVEEySWhaWFJXcDJVVUowWjB4aFgxaGpjMGMxTkdkcmEzWkJJaFkyTURWcFR6RnBPREJPVm5sRmVuWlVkRk41TmtwQkloWTRkWGx4ZVVaamJETmtPVWxyTW5wU1ozZDJSRmhuSWhaRVRVNVJkRU4yY2xOcWFFZEJXbk53TlVWbmFIcG5JaFkwTm1KMVozaGtXRXBPWTBJNFptUmpZbVJrWWpSUktBRXdBbEFCLm0zdTg/dG9rZW49MTc3MjU3NDYzMH5NalV5T0RRelpqRmpOakJsWWpSaE5qSmxZV1UwTVRFek56TXdNRFEyWm1Nek56RXhabVkwT0E9PSJdfQ=="
  }
}
```

where `manifest` is base64-encoded JSON containing HLS video.

##### Decoded Manifest

```json
{
  "mimeType":"application/vnd.apple.mpegurl","urls":[
    "https://im-fa.manifest.tidal.com/1/manifests/CAESCDQ4MjA0MTA2IhZXRWp2UUJ0Z0xhX1hjc0c1NGdra3ZBIhY2MDVpTzFpODBOVnlFenZUdFN5NkpBIhY4dXlxeUZjbDNkOUlrMnpSZ3d2RFhnIhZETU5RdEN2clNqaEdBWnNwNUVnaHpnIhY0NmJ1Z3hkWEpOY0I4ZmRjYmRkYjRRKAEwAlAB.m3u8?token=1772574630~MjUyODQzZjFjNjBlYjRhNjJlYWU0MTEzNzMwMDQ2ZmMzNzExZmY0OA=="
  ]
}
```

###### HLS manifest

```text
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=466000,AVERAGE-BANDWIDTH=465999,CODECS="mp4a.40.2,avc1.42C00D",RESOLUTION=320x180
https://im-fa.manifest.tidal.com/1/manifests/CAESCDQ4MjA0MTA2GAEiFjQ2YnVneGRYSk5jQjhmZGNiZGRiNFEoATACUAE.m3u8?token=1772574889~YjIxODgzM2JmOTcwNjU0NGE1ZGU4OGE2ZGZkZmI1NDA4MjYwNmI4Zg==
#EXT-X-STREAM-INF:BANDWIDTH=735000,AVERAGE-BANDWIDTH=734999,CODECS="mp4a.40.2,avc1.4D401E",RESOLUTION=640x360
https://im-fa.manifest.tidal.com/1/manifests/CAESCDQ4MjA0MTA2GAEiFkRNTlF0Q3ZyU2poR0Fac3A1RWdoemcoATACUAE.m3u8?token=1772574889~Y2FmNTU4MTY1OTlkMzJlMWUwZTczN2FiNmQxYTNkMTUxZDhhZWM2Yg==
#EXT-X-STREAM-INF:BANDWIDTH=1425000,AVERAGE-BANDWIDTH=1424999,CODECS="mp4a.40.2,avc1.4D401F",RESOLUTION=854x480
https://im-fa.manifest.tidal.com/1/manifests/CAESCDQ4MjA0MTA2GAEiFjh1eXF5RmNsM2Q5SWsyelJnd3ZEWGcoATACUAE.m3u8?token=1772574889~N2RiMzZiMzI4YWJhMzQ2ZTliMTA2ZDQzN2I3YmE4YjEzZTlhZWVlZg==
#EXT-X-STREAM-INF:BANDWIDTH=2740000,AVERAGE-BANDWIDTH=2740000,CODECS="mp4a.40.2,avc1.64001F",RESOLUTION=1280x720
https://im-fa.manifest.tidal.com/1/manifests/CAESCDQ4MjA0MTA2GAEiFjYwNWlPMWk4ME5WeUV6dlR0U3k2SkEoATACUAE.m3u8?token=1772574889~MzE4YzVjNGM2Njc5YjAxY2E5OWIzYzc5NWExMTExMDc2ZjdmMWM3ZQ==
#EXT-X-STREAM-INF:BANDWIDTH=5447000,AVERAGE-BANDWIDTH=5447000,CODECS="mp4a.40.2,avc1.640028",RESOLUTION=1920x1080
https://im-fa.manifest.tidal.com/1/manifests/CAESCDQ4MjA0MTA2GAEiFldFanZRQnRnTGFfWGNzRzU0Z2trdkEoATACUAE.m3u8?token=1772574889~NGYzNmJjNjU4ZjQwNjZkODVhNThhZWI3Y2MwNTU3NzEzMWUzMWI0MQ==
```
