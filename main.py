import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import os
import json
import re
from mutagen.easyid3 import EasyID3
import threading
import shutil


class YtDownloaderApp:
    CONFIG_FILE = "yt_downloader_config.json"

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("520x540")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.config = self._load_config()
        self._setup_variables()
        self._setup_gui()

    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                return json.load(f)
        return {
            "save_path": os.path.expanduser("~/Downloads/YT-Downloads"),
            "dl_movie": True, "dl_music": False, "dl_srt": False, "dl_txt": False,
            "subtitle_lang": "detect", "download_playlist": True,
            "trim_start": "", "trim_end": ""
        }

    def _save_config(self):
        current_config = {
            "save_path": self.save_path_var.get(),
            "dl_movie": self.movie_var.get(), "dl_music": self.music_var.get(),
            "dl_srt": self.srt_subs_var.get(), "dl_txt": self.txt_subs_var.get(),
            "subtitle_lang": self.lang_var.get(), "download_playlist": self.playlist_var.get(),
            "trim_start": self.trim_start_var.get(), "trim_end": self.trim_end_var.get()
        }
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(current_config, f, indent=4)

    def _setup_variables(self):
        self.save_path_var = tk.StringVar(value=self.config.get("save_path"))
        self.movie_var = tk.BooleanVar(value=self.config.get("dl_movie", True))
        self.music_var = tk.BooleanVar(value=self.config.get("dl_music", False))
        self.srt_subs_var = tk.BooleanVar(value=self.config.get("dl_srt", False))
        self.txt_subs_var = tk.BooleanVar(value=self.config.get("dl_txt", False))
        self.lang_var = tk.StringVar(value=self.config.get("subtitle_lang", "detect"))
        self.playlist_var = tk.BooleanVar(value=self.config.get("download_playlist", True))

        # New: trim range vars
        self.trim_start_var = tk.StringVar(value=self.config.get("trim_start", ""))
        self.trim_end_var = tk.StringVar(value=self.config.get("trim_end", ""))

        # Traces
        self.srt_subs_var.trace("w", self._toggle_subtitle_options)
        self.txt_subs_var.trace("w", self._toggle_subtitle_options)
        self.movie_var.trace("w", self._toggle_trim_options)
        self.playlist_var.trace("w", self._toggle_trim_options)

    def _setup_gui(self):
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="YouTube Video or Playlist URL:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.url_entry = tk.Entry(main_frame, width=60)
        self.url_entry.pack(fill="x", pady=(5, 15))

        # Download options
        tk.Label(main_frame, text="Download Options:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        opts_frame = tk.Frame(main_frame)
        opts_frame.pack(fill="x", pady=(0, 10))
        tk.Checkbutton(opts_frame, text="Video (MP4)", variable=self.movie_var).grid(row=0, column=0, sticky="w")
        tk.Checkbutton(opts_frame, text="Audio (MP3)", variable=self.music_var).grid(row=0, column=1, sticky="w", padx=(15,0))
        tk.Checkbutton(opts_frame, text="Subtitles (SRT)", variable=self.srt_subs_var).grid(row=1, column=0, sticky="w", pady=(5,0))
        tk.Checkbutton(opts_frame, text="Subtitles (TXT)", variable=self.txt_subs_var).grid(row=1, column=1, sticky="w", padx=(15,0), pady=(5,0))

        # Playlist section (more eye-catching / separate)
        playlist_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=10, pady=8, highlightthickness=1)
        playlist_frame.pack(fill="x", pady=(5, 12))
        tk.Label(playlist_frame, text="▶ Playlist Mode", font=("Helvetica", 10, "bold"), fg="#b30000").pack(anchor="w")
        tk.Checkbutton(playlist_frame,
                       text="Download entire playlist (if URL contains one)",
                       variable=self.playlist_var, font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(4,0))
        tk.Label(playlist_frame,
                 text="Tip: Turn this off to download only the single video at the URL.",
                 fg="#555555").pack(anchor="w", pady=(2,0))

        # Save path
        tk.Label(main_frame, text="Save To:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(4, 0))
        save_path_frame = tk.Frame(main_frame)
        save_path_frame.pack(fill="x", pady=(5, 10))
        tk.Entry(save_path_frame, textvariable=self.save_path_var).pack(side="left", fill="x", expand=True, ipady=2)
        tk.Button(save_path_frame, text="Browse...", command=self._browse_for_directory).pack(side="right", padx=(5, 0))

        # Subtitle lang (auto show/hide)
        self.lang_label = tk.Label(main_frame, text="Subtitle Language:", font=("Helvetica", 10, "bold"))
        languages = ["detect", "all", "en", "es", "fr", "de", "ko", "ja", "ru", "it", "pt", "zh-Hans", "zh-Hant"]
        self.lang_dropdown = tk.OptionMenu(main_frame, self.lang_var, *languages)
        self._toggle_subtitle_options()

        # Trim range (only for single-video MP4; disabled when playlist is on)
        self.trim_block = tk.Frame(main_frame)
        self.trim_title = tk.Label(self.trim_block, text="Trim Video (optional):", font=("Helvetica", 10, "bold"))
        self.trim_title.grid(row=0, column=0, sticky="w", pady=(0,5))
        tk.Label(self.trim_block, text="Start (MM:SS or HH:MM:SS):").grid(row=1, column=0, sticky="w")
        self.trim_start_entry = tk.Entry(self.trim_block, textvariable=self.trim_start_var, width=15)
        self.trim_start_entry.grid(row=1, column=1, sticky="w", padx=(6,0))
        tk.Label(self.trim_block, text="End (MM:SS or HH:MM:SS):").grid(row=1, column=2, sticky="w", padx=(20,0))
        self.trim_end_entry = tk.Entry(self.trim_block, textvariable=self.trim_end_var, width=15)
        self.trim_end_entry.grid(row=1, column=3, sticky="w", padx=(6,0))
        self.trim_note = tk.Label(self.trim_block, text="Used for MP4 only. Disabled when playlist mode is on.",
                                  fg="#555555")
        self.trim_note.grid(row=2, column=0, columnspan=4, sticky="w", pady=(4,0))
        self._toggle_trim_options()  # initial state

        # Download button + progress
        self.download_button = tk.Button(main_frame, text="Download", font=("Helvetica", 12, "bold"),
                                         command=self.start_download_thread)
        self.download_button.pack(pady=(12, 0), fill="x", ipady=5)

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(15, 5))
        self.status_label = tk.Label(main_frame, text="", font=("Helvetica", 9))
        self.status_label.pack(anchor="w", fill="x")

    def _browse_for_directory(self):
        path = filedialog.askdirectory(initialdir=self.save_path_var.get() or os.path.expanduser("~"))
        if path: self.save_path_var.set(path)

    def _toggle_subtitle_options(self, *args):
        if self.srt_subs_var.get() or self.txt_subs_var.get():
            self.lang_label.pack(anchor="w", pady=(5, 0))
            self.lang_dropdown.pack(anchor="w", fill="x")
        else:
            self.lang_label.pack_forget()
            self.lang_dropdown.pack_forget()

    def _toggle_trim_options(self, *args):
        # Show trim UI only if Video selected
        show_trim = self.movie_var.get()
        if show_trim:
            self.trim_block.pack(fill="x", pady=(8, 6))
        else:
            self.trim_block.pack_forget()

        # Disable trim entries when playlist mode is enabled
        state = "disabled" if self.playlist_var.get() else "normal"
        for w in (self.trim_start_entry, self.trim_end_entry):
            w.config(state=state)

    def _on_closing(self):
        self._save_config()
        self.root.destroy()

    def _update_ui(self, status_text="", color="black", progress=None, button_state="normal"):
        def task():
            self.status_label.config(text=status_text, fg=color)
            if progress is not None: self.progress_bar['value'] = progress
            self.download_button.config(state=button_state)
        self.root.after(0, task)

    def start_download_thread(self):
        threading.Thread(target=self.run_download_orchestrator, daemon=True).start()

    def _execute_subprocess(self, command, description):
        self._update_ui(f"{description}...", progress=0)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   universal_newlines=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            print(line.strip())
            match = re.search(r"\[download\]\s+([0-9\.]+)%", line)
            if match:
                percentage = float(match.group(1))
                self._update_ui(f"{description}... {percentage:.1f}%", progress=percentage)
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command,
                                                "A download task failed. See console for details.")

    def run_download_orchestrator(self):
        self._update_ui(progress=0, button_state="disabled")
        url = self.url_entry.get()
        base_dir = self.save_path_var.get()

        if not all([url, base_dir]) or not any(
                [self.movie_var.get(), self.music_var.get(), self.srt_subs_var.get(), self.txt_subs_var.get()]):
            messagebox.showwarning("Input Missing",
                                   "Please provide a URL, save path, and select at least one download type.")
            self._update_ui(button_state="normal")
            return

        # Validate trim times if present (and only matters for video)
        try:
            trim_flags = []
            if self.movie_var.get() and not self.playlist_var.get():
                trim_flags = self._build_trim_flags()  # may be []
        except ValueError as ve:
            self._update_ui(button_state="normal")
            messagebox.showerror("Invalid time", str(ve))
            return

        try:
            is_playlist = "list=" in url and self.playlist_var.get()
            final_save_dir = base_dir
            if is_playlist:
                self._update_ui("Fetching playlist details...")
                info_cmd = ["yt-dlp", "-j", "--playlist-items", "1", url]
                result = subprocess.run(info_cmd, capture_output=True, text=True, check=True, encoding='utf-8')
                # yt-dlp may output multiple JSON lines; use the first valid object
                first_line = result.stdout.strip().splitlines()[0]
                metadata = json.loads(first_line)
                artist = metadata.get("uploader", "Unknown Artist")
                album = metadata.get("playlist_title", "Playlist")
                subfolder = f"{artist} - {album}".replace("/", "-").replace("\\", "-").strip()
                final_save_dir = os.path.join(base_dir, subfolder)
            os.makedirs(final_save_dir, exist_ok=True)

            output_template = os.path.join(final_save_dir,
                                           "%(playlist_index)s - %(title)s.%(ext)s" if is_playlist else "%(title)s.%(ext)s")

            base_command = ["yt-dlp", "--progress", "--no-overwrites", "--compat-options", "no-live-chat"]

            if "list=" in url and not self.playlist_var.get(): base_command.append("--no-playlist")

            subs_were_downloaded = False
            if self.movie_var.get():
                cmd = base_command + [
                    "--embed-metadata", "--embed-thumbnail",
                    "-f", "bv*+ba/bv/b",
                    "--merge-output-format", "mp4"
                ]
                if trim_flags:
                    cmd += trim_flags  # ["--download-sections", section, "--force-keyframes-at-cuts"]
                if self.srt_subs_var.get() or self.txt_subs_var.get():
                    cmd.extend(self._get_subtitle_flags())
                    subs_were_downloaded = True
                cmd.extend(["-o", output_template, url])
                self._execute_subprocess(cmd, "Downloading Video")

            if self.music_var.get():
                cmd = base_command + ["--embed-metadata", "--embed-thumbnail", "-x", "--audio-format", "mp3"]
                if not subs_were_downloaded and (self.srt_subs_var.get() or self.txt_subs_var.get()):
                    cmd.extend(self._get_subtitle_flags())
                    subs_were_downloaded = True
                cmd.extend(["-o", output_template, url])
                self._execute_subprocess(cmd, "Downloading Audio")

            if not subs_were_downloaded and (self.srt_subs_var.get() or self.txt_subs_var.get()):
                cmd = base_command + ["--skip-download"] + self._get_subtitle_flags()
                cmd.extend(["-o", output_template, url])
                self._execute_subprocess(cmd, "Downloading Subtitles")

            self._update_ui("Post-processing...", progress=100)
            self._post_process_files(final_save_dir, is_playlist)

            self._update_ui("Download complete! ✅", "green", progress=100)
            self.root.bell()

        except Exception as e:
            self._update_ui(f"Error: {e} ❌", "red")
        finally:
            self._update_ui(button_state="normal")

    def _normalize_time(self, tstr):
        """
        Accepts HH:MM:SS, MM:SS, or plain digits interpreted as HHMMSS.
        Examples:
          "1"      -> 00:00:01
          "12"     -> 00:00:12
          "315"    -> 00:03:15
          "93215"  -> 09:32:15
          "124124" -> 12:41:24
        """
        tstr = (tstr or "").strip()
        if not tstr:
            return None

        # Case 1: digits only, treat as HHMMSS (pad left to 6 digits)
        if tstr.isdigit():
            val = tstr.zfill(6)  # pad with leading zeros to length 6
            h = int(val[:-4]) if len(val) > 4 else 0
            m = int(val[-4:-2])
            s = int(val[-2:])
            if not (0 <= m < 60 and 0 <= s < 60):
                raise ValueError("Minutes and seconds must be within 0–59.")
            return f"{h:02d}:{m:02d}:{s:02d}"

        # Case 2: H:M:S or M:S
        if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}", tstr):
            h, m, s = [int(x) for x in tstr.split(":")]
        elif re.fullmatch(r"\d{1,2}:\d{2}", tstr):
            m, s = [int(x) for x in tstr.split(":")]
            h = 0
        else:
            raise ValueError("Time must be HH:MM:SS, MM:SS, or HHMMSS digits.")

        if not (0 <= m < 60 and 0 <= s < 60):
            raise ValueError("Minutes and seconds must be within 0–59.")
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _build_trim_flags(self):
        """
        Builds yt-dlp trim flags using --download-sections.
        Returns [] if no trimming requested.
        """
        start = self._normalize_time(self.trim_start_var.get())
        end = self._normalize_time(self.trim_end_var.get())

        if not start and not end:
            return []
        # open-ended ranges allowed: *START- or *-END
        if start and end:
            # sanity: start < end (compare by seconds)
            def to_secs(hms):
                h, m, s = [int(x) for x in hms.split(":")]
                return h*3600 + m*60 + s
            if to_secs(start) >= to_secs(end):
                raise ValueError("Start time must be earlier than end time.")
            section = f"*{start}-{end}"
        elif start:
            section = f"*{start}-"
        else:  # end only
            section = f"*-{end}"

        # --force-keyframes-at-cuts improves cut accuracy
        return ["--download-sections", section, "--force-keyframes-at-cuts"]

    def _get_subtitle_flags(self):
        flags = ["--write-subs", "--write-auto-subs", "--convert-subs", "srt"]
        lang = self.lang_var.get()
        if lang == "all":
            flags.append("--all-subs")
        elif lang != "detect":
            flags.extend(["--sub-langs", lang])
        return flags

    def _post_process_files(self, directory, is_playlist):
        if self.music_var.get() and is_playlist: self._tag_music_files(directory)
        if self.txt_subs_var.get(): self._convert_srt_to_txt(directory)
        self._cleanup_files(directory)

    def _tag_music_files(self, directory):
        print("Tagging music files...")
        for filename in sorted(f for f in os.listdir(directory) if f.endswith(".mp3")):
            match = re.match(r"(\d+)\s*-\s*", filename)
            if match:
                try:
                    audio = EasyID3(os.path.join(directory, filename))
                    audio["tracknumber"] = match.group(1).lstrip("0") or "0"
                    audio.save()
                except Exception as e:
                    print(f"Failed to tag {filename}: {e}")

    def _convert_srt_to_txt(self, directory):
        print("Converting SRT to TXT...")
        for filename in os.listdir(directory):
            if filename.endswith(".srt"):
                srt_path = os.path.join(directory, filename)
                txt_path = os.path.splitext(srt_path)[0] + ".txt"
                try:
                    with open(srt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    raw_text_lines = re.findall(
                        r'^(?!\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+$)(?!\d+$).+',
                        content, re.MULTILINE
                    )
                    clean_transcript_lines = []
                    last_line = ""
                    for line in raw_text_lines:
                        cleaned_line = re.sub(r'<.*?>', '', line).strip()
                        if cleaned_line and cleaned_line != last_line:
                            clean_transcript_lines.append(cleaned_line)
                            last_line = cleaned_line
                    final_text = "\n".join(clean_transcript_lines)
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(final_text)
                    print(f"Successfully converted {filename} to TXT.")
                except Exception as e:
                    print(f"Error converting {filename}: {e}")

    def _cleanup_files(self, directory):
        print("Cleaning up files...")
        srt_wanted = self.srt_subs_var.get()
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            ext = os.path.splitext(filename)[1].lower()
            if not srt_wanted and ext == ".srt":
                try:
                    os.remove(file_path)
                    print(f"Removed temporary SRT file: {filename}")
                except OSError as e:
                    print(f"Error removing SRT file {file_path}: {e}")
            if ext in ['.webp', '.jpg', '.jpeg', '.png']:
                try:
                    os.remove(file_path)
                    print(f"Removed thumbnail: {filename}")
                except OSError as e:
                    print(f"Error removing thumbnail file {file_path}: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YtDownloaderApp(root)
    root.mainloop()
