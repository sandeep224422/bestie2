import asyncio
import os
import re
import json
import glob
import random
from typing import Union

import yt_dlp
import httpx
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from RishuMusic.utils.database import is_on_off
from RishuMusic.utils.formatters import time_to_seconds


def cookie_txt_file() -> str:
    cookies_dir = os.path.join(os.getcwd(), "cookies")
    log_path = os.path.join(cookies_dir, "logs.csv")
    txt_files = glob.glob(os.path.join(cookies_dir, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the cookies directory.")
    chosen = random.choice(txt_files)
    with open(log_path, "a") as log:
        log.write(f"Chosen file: {chosen}\n")
    return f"cookies/{os.path.basename(chosen)}"


async def check_file_size(link: str) -> Union[int, None]:
    async def query_format_info(url: str):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "--cookies", cookie_txt_file(), "-J", url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
        if proc.returncode != 0:
            print(f"Error:\n{err.decode()}")
            return None
        return json.loads(out.decode())

    def total_bytes(formats_list):
        return sum(f.get("filesize", 0) for f in formats_list)

    info = await query_format_info(link)
    if not info or not info.get("formats"):
        print("No format info available.")
        return None

    return total_bytes(info["formats"])


async def shell_cmd(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    if err:
        err_text = err.decode("utf-8").lower()
        if "unavailable videos are hidden" in err_text:
            return out.decode("utf-8")
        return err.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.escape_re = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = False) -> bool:
        url = (self.base + link) if videoid else link
        return True if re.search(self.regex, url) else False

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)

        for msg in messages:
            entities = msg.entities or msg.caption_entities or []
            for ent in entities:
                if ent.type == MessageEntityType.URL:
                    text = msg.text or msg.caption or ""
                    return text[ent.offset : ent.offset + ent.length]
                elif ent.type == MessageEntityType.TEXT_LINK and ent.url:
                    return ent.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = False):
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        res = VideosSearch(url, limit=1)
        data = (await res.next())["result"][0]
        title = data["title"]
        duration_str = data["duration"]
        duration_sec = int(time_to_seconds(duration_str)) if duration_str and duration_str != "None" else 0
        thumb = data["thumbnails"][0]["url"].split("?")[0]
        vidid = data["id"]
        return title, duration_str, duration_sec, thumb, vidid

    async def title(self, link: str, videoid: Union[bool, str] = False) -> str:
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        res = VideosSearch(url, limit=1)
        return (await res.next())["result"][0]["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = False) -> str:
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        res = VideosSearch(url, limit=1)
        return (await res.next())["result"][0]["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = False) -> str:
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        res = VideosSearch(url, limit=1)
        return (await res.next())["result"][0]["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = False):
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "--cookies", cookie_txt_file(), "-g", "-f", "best[height<=?720][width<=?1280]", url,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        return (1, out.decode().split("\n")[0]) if out else (0, err.decode())

    async def playlist(self, link: str, limit: int, user_id: int, videoid: Union[bool, str] = False):
        url = (self.listbase + link) if videoid else link
        url = url.split("&")[0]
        cmd = f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {url}"
        out = await shell_cmd(cmd)
        ids = [item for item in out.splitlines() if item.strip()]
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = False):
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        res = VideosSearch(url, limit=1)
        data = (await res.next())["result"][0]
        return (
            {
                "title": data["title"],
                "link": data["link"],
                "vidid": data["id"],
                "duration_min": data["duration"],
                "thumb": data["thumbnails"][0]["url"].split("?")[0],
            },
            data["id"],
        )

    async def formats(self, link: str, videoid: Union[bool, str] = False):
        url = (self.base + link) if videoid else link
        url = url.split("&")[0]
        opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        ydl = yt_dlp.YoutubeDL(opts)
        with ydl:
            info = ydl.extract_info(url, download=False)
        fmts = [
            {
                "format": f["format"],
                "filesize": f.get("filesize"),
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "format_note": f.get("format_note"),
                "yturl": url,
            }
            for f in info.get("formats", []) if "dash" not in (f.get("format", "").lower())
        ]
        return fmts, url

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = False,
        videoid: Union[bool, str] = False,
        songaudio: Union[bool, str] = False,
        songvideo: Union[bool, str] = False,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> Union[tuple[str, bool], None]:
        url = (self.base + link) if videoid else link

        async def try_external_api(url: str) -> Union[str, None]:
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get("https://apikeyy-zeta.vercel.app/api", params={"url": url})
                    if r.status_code == 200 and (data := r.json()).get("url"):
                        download_url = data["url"]
                        filepath = f"downloads/external_{url[-11:]}.mp3"
                        async with client.stream("GET", download_url) as resp:
                            with open(filepath, "wb") as f:
                                async for chunk in resp.aiter_bytes():
                                    f.write(chunk)
                        return filepath
            except Exception as e:
                print(f"External API failed: {e}")
            return None

        loop = asyncio.get_running_loop()

        # First attempt via external API for audio-only requests
        if not video and not songvideo:
            ext_path = await try_external_api(url)
            if ext_path:
                return ext_path, True
            print("External API fallback failed; proceeding with yt-dlp.")

        # yt-dlp fallback download functions
        def audio_dl():
            opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "cookiefile": cookie_txt_file(), "no_warnings": True,
            }
            ydl = yt_dlp.YoutubeDL(opts)
            info = ydl.extract_info(url, download=False)
            path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(path):
                return path
            ydl.download([url])
            return path

        def video_dl():
            opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "cookiefile": cookie_txt_file(), "no_warnings": True,
            }
            ydl = yt_dlp.YoutubeDL(opts)
            info = ydl.extract_info(url, download=False)
            path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(path):
                return path
            ydl.download([url])
            return path

        def song_video_dl():
            fmt = f"{format_id}+140"
            out_tmpl = f"downloads/{title}"
            ydl_opts = {
                "format": fmt,
                "outtmpl": out_tmpl,
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "cookiefile": cookie_txt_file(),
                "prefer_ffmpeg": True, "merge_output_format": "mp4",
            }
            yt_dlp.YoutubeDL(ydl_opts).download([url])

        def song_audio_dl():
            out_tmpl = f"downloads/{title}.%(ext)s"
            ydl_opts = {
                "format": format_id,
                "outtmpl": out_tmpl,
                "geo_bypass": True, "nocheckcertificate": True,
                "quiet": True, "cookiefile": cookie_txt_file(),
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
                ],
            }
            yt_dlp.YoutubeDL(ydl_opts).download([url])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4", True

        if songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3", True

        if video:
            if await is_on_off(1):
                path = await loop.run_in_executor(None, video_dl)
                return path, True
            else:
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp", "--cookies", cookie_txt_file(), "-g",
                    "-f", "best[height<=?720][width<=?1280]", url,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                out, err = await proc.communicate()
                if out:
                    return out.decode().split("\n")[0], False
                size = await check_file_size(url)
                if not size:
                    print("Could not determine file size.")
                    return None
                mb = size / (1024 * 1024)
                if mb > 250:
                    print(f"File size {mb:.2f} MB exceeds limit of 250 MB.")
                    return None
                path = await loop.run_in_executor(None, video_dl)
                return path, True

        # Default: audio download via yt‑dl
        path = await loop.run_in_executor(None, audio_dl)
        return path, True
