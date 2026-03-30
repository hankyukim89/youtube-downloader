"""
Core download logic for YouTube Downloader
"""
import yt_dlp
import json
import os
import re
from pathlib import Path
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass
from enum import Enum
from mutagen.easyid3 import EasyID3

@dataclass
class DownloadProgress:
    """Represents download progress state"""
    percentage: float = 0.0
    status: str = ""
    is_complete: bool = False
    is_error: bool = False
    error_message: str = ""

class TimeParser:
    """Utility class for parsing time strings"""
    @staticmethod
    def normalize(time_str: str) -> Optional[str]:
        time_str = (time_str or "").strip()
        if not time_str: return None
        if time_str.isdigit():
            val = time_str.zfill(6)
            h, m, s = int(val[:-4]) if len(val) > 4 else 0, int(val[-4:-2]), int(val[-2:])
            return f"{h:02d}:{m:02d}:{s:02d}"
        if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}", time_str):
            return time_str
        elif re.fullmatch(r"\d{1,2}:\d{2}", time_str):
            m, s = [int(x) for x in time_str.split(":")]
            return f"00:{m:02d}:{s:02d}"
        raise ValueError("Invalid time format")

    @staticmethod
    def to_seconds(hms: str) -> int:
        h, m, s = [int(x) for x in hms.split(":")]
        return h * 3600 + m * 60 + s

class YouTubeDownloader:
    """Handles all YouTube download operations using yt_dlp library"""
    
    def __init__(self, progress_callback: Optional[Callable[[DownloadProgress], None]] = None):
        self.progress_callback = progress_callback or (lambda x: None)
        self.log_file = Path("yt_dlp_debug.log")
        # Ensure log file is fresh
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"YouTube Downloader Log Started. yt-dlp version: {yt_dlp.version.__version__}\n")

    class Logger:
        def __init__(self, log_file):
            self.log_file = log_file
        def debug(self, msg):
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"DEBUG: {msg}\n")
        def info(self, msg):
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"INFO: {msg}\n")
        def warning(self, msg):
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"WARNING: {msg}\n")
        def error(self, msg):
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"ERROR: {msg}\n")

    
    def _report_progress(self, percentage: float = 0, status: str = "", 
                         is_complete: bool = False, is_error: bool = False,
                         error_message: str = "") -> None:
        progress = DownloadProgress(percentage, status, is_complete, is_error, error_message)
        self.progress_callback(progress)
    
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Strip ANSI escape sequences yt-dlp outputs
                raw_str = d.get('_percent_str', '0%')
                clean_str = re.sub(r'\x1b[^m]*m', '', raw_str).replace('%', '')
                self._report_progress(percentage=float(clean_str), status=f"Downloading... {raw_str}")
            except:
                pass
        elif d['status'] == 'finished':
            self._report_progress(percentage=100, status="Processing...")

    def _get_playlist_info(self, url: str) -> Tuple[str, str]:
        opts = {
            'extract_flat': True,
            'playlist_items': '1',
            'extractor_args': {'youtube': {'player_client': ['web', 'mweb', 'android']}},
            'quiet': True,
            'ignoreerrors': True
        }
        
        # Try to find a browser for cookies, but don't fail if all missing
        for browser in ['chrome', 'safari', 'firefox']:
            try:
                test_opts = opts.copy()
                test_opts['cookiesfrombrowser'] = (browser,)
                with yt_dlp.YoutubeDL(test_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info: 
                         opts['cookiesfrombrowser'] = (browser,)
                         break
            except Exception:
                continue

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # It's a playlist
                    # Access first entry for uploader if top level is missing it
                    first_entry = info['entries'][0] if info['entries'] else {}
                    artist = info.get("uploader") or first_entry.get("uploader") or "Unknown Artist"
                    album = info.get("title") or "Playlist"
                    return artist, album
                else:
                    # Single video passed as checklist?
                    return info.get("uploader", "Unknown Artist"), info.get("title", "Title")
            except Exception:
                return "Unknown Artist", "Playlist"

    def _get_subtitle_opts(self, language: str) -> dict:
        opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'srt'
        }
        if language == "all":
            opts['allsubtitles'] = True
        elif language != "detect":
            opts['subtitleslangs'] = [language]
        return opts

    def _tag_music_files(self, directory: Path) -> None:
        print("Tagging music files...")
        for filename in sorted(f for f in os.listdir(directory) if f.endswith(".mp3")):
            match = re.match(r"(\d+)\s*-\s*", filename)
            if match:
                try:
                    audio = EasyID3(directory / filename)
                    audio["tracknumber"] = match.group(1).lstrip("0") or "0"
                    audio.save()
                except Exception as e:
                    print(f"Failed to tag {filename}: {e}")

    def _convert_srt_to_txt(self, directory: Path) -> None:
        print("Converting SRT to TXT...")
        for filename in os.listdir(directory):
            if filename.endswith(".srt"):
                try:
                    srt_path = directory / filename
                    txt_path = srt_path.with_suffix(".txt")
                    with open(srt_path, 'r', encoding='utf-8') as f: content = f.read()
                    raw_lines = re.findall(r'^(?!\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+$)(?!\d+$).+', content, re.MULTILINE)
                    clean_lines = []
                    last_line = ""
                    for line in raw_lines:
                        cleaned = re.sub(r'<.*?>', '', line).strip()
                        if cleaned and cleaned != last_line:
                            clean_lines.append(cleaned)
                            last_line = cleaned
                    with open(txt_path, "w", encoding="utf-8") as f: f.write("\n".join(clean_lines))
                except Exception as e:
                    print(f"Error converting {filename}: {e}")

    def _cleanup_files(self, directory: Path, keep_srt: bool) -> None:
        for filename in os.listdir(directory):
            file_path = directory / filename
            ext = file_path.suffix.lower()
            if not keep_srt and ext == ".srt":
                try: os.remove(file_path) 
                except: pass
            if ext in ['.webp', '.jpg', '.jpeg', '.png']:
                try: os.remove(file_path)
                except: pass

    def download(self, url: str, save_path: str, dl_video: bool = True, dl_audio: bool = False,
                 dl_srt: bool = False, dl_txt: bool = False, subtitle_lang: str = "detect",
                 download_playlist: bool = True, trim_start: str = "", trim_end: str = "",
                 video_res: str = "1080p", audio_format: str = "mp3") -> None:
        
        if not url or not save_path: raise ValueError("URL and save path required.")
        if not any([dl_video, dl_audio, dl_srt, dl_txt]): raise ValueError("Select at least one download type.")

        try:
            base_dir = Path(save_path)
            is_playlist = "list=" in url and download_playlist
            final_save_dir = base_dir
            
            if is_playlist:
                artist, album = self._get_playlist_info(url)
                subfolder = f"{artist} - {album}".replace("/", "-").replace("\\", "-").strip()
                final_save_dir = base_dir / subfolder
            
            final_save_dir.mkdir(parents=True, exist_ok=True)
            
            trim_opts = {}
            if not is_playlist and (trim_start.strip() or trim_end.strip()):
                norm_start = TimeParser.normalize(trim_start)
                start_sec = TimeParser.to_seconds(norm_start) if norm_start else 0
                norm_end = TimeParser.normalize(trim_end)
                end_sec = TimeParser.to_seconds(norm_end) if norm_end else float('inf')
                
                if start_sec >= end_sec and end_sec != float('inf'):
                    raise ValueError("Start time must be earlier than end time.")
                    
                def download_range_func(info_dict, ydl):
                    return [{'start_time': start_sec, 'end_time': end_sec}]
                    
                trim_opts["download_ranges"] = download_range_func
                trim_opts["force_keyframes_at_cuts"] = True
            
            browser_to_use = None

            # Common Options based on USER'S WORKING SCRIPT
            base_opts = {
                "paths": {"home": str(final_save_dir)},
                "outtmpl": "%(playlist_index)s - %(title)s.%(ext)s" if is_playlist else "%(title)s.%(ext)s",
                "quiet": False, # Setting to False to see more in log
                "color": "no_color",
                "logger": self.Logger(self.log_file),
                "progress_hooks": [self._progress_hook],
                "ignoreerrors": False,
                "nocheckcertificate": True,
                "noplaylist": not download_playlist,
                "no_warnings": False,
                "verbose": True
            }
            if browser_to_use:
                base_opts["cookiesfrombrowser"] = (browser_to_use,)


            subs_opts = {}
            if dl_srt or dl_txt:
                subs_opts = self._get_subtitle_opts(subtitle_lang)

            if dl_video:
                self._report_progress(status="Starting Video Download...")
                video_opts = base_opts.copy()
                
                format_str = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b"
                if video_res and video_res != "Best":
                    if video_res == "4K":
                        height = "2160"
                    else:
                        height = video_res.replace("p", "")
                    format_str = f"bv*[ext=mp4][height<={height}]+ba[ext=m4a]/b[ext=mp4][height<={height}] / bv*[height<={height}]+ba/b"

                video_opts.update({
                    "format": format_str,
                    "merge_output_format": "mp4",
                    "writethumbnail": True,
                    "addmetadata": True,
                })
                video_opts.update(subs_opts)
                if trim_opts:
                    video_opts.update(trim_opts)
                
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    ydl.download([url])

            # 2. Download Audio
            if dl_audio:
                self._report_progress(status="Starting Audio Download...")
                audio_opts = base_opts.copy()
                
                audio_codec = audio_format.lower() if audio_format else "mp3"
                pp_opts = {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_codec,
                }
                if audio_codec == "mp3":
                    pp_opts["preferredquality"] = "192"

                audio_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [
                        pp_opts, {
                        'key': 'EmbedThumbnail',
                    }, {
                        'key': 'FFmpegMetadata',
                    }],
                    "writethumbnail": True,
                })
                audio_opts.update(subs_opts)
                if trim_opts:
                    audio_opts.update(trim_opts)
                
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    ydl.download([url])
            # 3. Download Subtitles Only
            if not dl_video and not dl_audio and (dl_srt or dl_txt):
                self._report_progress(status="Downloading Subtitles/Transcript...")
                sub_opts_only = base_opts.copy()
                sub_opts_only.update({
                    "skip_download": True,
                })
                sub_opts_only.update(subs_opts)
                with yt_dlp.YoutubeDL(sub_opts_only) as ydl:
                    ydl.download([url])

            # 4. Post-processing
            if dl_audio and is_playlist:
                self._tag_music_files(final_save_dir)
            if dl_txt:
                self._convert_srt_to_txt(final_save_dir)
            
            self._cleanup_files(final_save_dir, dl_srt)
            self._report_progress(percentage=100, status="Download complete! ✅", is_complete=True)

        except Exception as e:
            self._report_progress(is_error=True, error_message=str(e))
