"""
Modern YouTube Downloader Application
A beautiful, modern GUI for downloading YouTube videos and audio
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ConfigManager, DownloadConfig
from src.downloader import YouTubeDownloader, DownloadProgress
from src.ui.theme import COLORS, FONTS, FONTS_FALLBACK, SPACING, RADIUS


class ModernYouTubeDownloader(ctk.CTk):
    """Modern YouTube Downloader Application"""
    
    def __init__(self):
        super().__init__()
        
        # Configure appearance - YouTube Light Theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Window setup
        self.title("YouTube Downloader")
        self.geometry("480x520")
        self.minsize(480, 520)
        
        # Custom colors
        self.configure(fg_color=COLORS["bg_primary"])
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Initialize variables
        self._setup_variables()
        
        # Build UI
        self._build_ui()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Center window
        self._center_window()
    
    def _center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2 - 50
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def _setup_variables(self):
        """Initialize all tkinter variables"""
        self.url_var = ctk.StringVar(value="")
        self.save_path_var = ctk.StringVar(value=self.config.save_path)
        self.video_var = ctk.BooleanVar(value=self.config.dl_video)
        self.audio_var = ctk.BooleanVar(value=self.config.dl_audio)
        self.srt_var = ctk.BooleanVar(value=self.config.dl_srt)
        self.txt_var = ctk.BooleanVar(value=self.config.dl_txt)
        self.lang_var = ctk.StringVar(value=self.config.subtitle_lang)
        self.audio_format_var = ctk.StringVar(value=self.config.audio_format)
        self.playlist_var = ctk.BooleanVar(value=self.config.download_playlist)
        self.trim_start_var = ctk.StringVar(value=self.config.trim_start)
        self.trim_end_var = ctk.StringVar(value=self.config.trim_end)
        
        # Traces for dynamic UI updates
        self.srt_var.trace_add("write", self._toggle_subtitle_options)
        self.txt_var.trace_add("write", self._toggle_subtitle_options)
        self.video_var.trace_add("write", self._toggle_trim_options)
        self.playlist_var.trace_add("write", self._toggle_trim_options)
        self.audio_var.trace_add("write", self._toggle_audio_format_options)
    
    def _build_ui(self):
        """Build the main UI"""
        # Main container (no longer scrollable, forces compactness)
        self.scroll_frame = ctk.CTkFrame(
            self, 
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Main container with padding (now inside scroll_frame)
        self.main_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=SPACING["sm"])
        
        # Header
        self._build_header()
        
        # URL Input Section
        self._build_url_section()
        
        # Download Options Section
        self._build_options_section()
        
        # Audio Format Section (hidden by default)
        self._build_audio_format_section()
        
        # Playlist Section
        self._build_playlist_section()
        
        # Save Path Section
        self._build_save_section()
        
        # Subtitle Language (hidden by default)
        self._build_subtitle_section()
        
        # Trim Section (conditional)
        self._build_trim_section()
        
        # Download Button & Progress
        self._build_action_section()
        
        # Initialize conditional UI states (must be after all UI is built)
        self._toggle_trim_options()
        self._toggle_subtitle_options()
        self._toggle_audio_format_options()
    
    def _build_header(self):
        """Build the header with title and icon"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, SPACING["md"]))
        
        # Icon (YouTube-style play button)
        icon_canvas = ctk.CTkCanvas(
            header_frame, 
            width=30, height=30, 
            bg=COLORS["bg_primary"],
            highlightthickness=0
        )
        icon_canvas.pack(side="left", padx=(0, SPACING["sm"]))
        
        # Draw play button icon
        icon_canvas.create_oval(2, 2, 28, 28, fill=COLORS["accent_primary"], outline="")
        icon_canvas.create_polygon(12, 8, 12, 22, 22, 15, fill="white")
        
        # Title and subtitle
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="YouTube Downloader",
            font=ctk.CTkFont(family="Helvetica Neue", size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Clean, modern downloader",
            font=ctk.CTkFont(family="Helvetica Neue", size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(anchor="w")
    
    def _build_url_section(self):
        """Build URL input section"""
        section_frame = self._create_section("Paste URL", "YouTube video or playlist link")
        
        # URL Entry with paste button
        url_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        url_container.pack(fill="x")
        
        self.url_entry = ctk.CTkEntry(
            url_container,
            textvariable=self.url_var,
            placeholder_text="https://youtube.com/watch?v=...",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            corner_radius=RADIUS["md"]
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["sm"]))
        
        paste_btn = ctk.CTkButton(
            url_container,
            text="📋",
            width=32,
            height=32,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            command=self._paste_from_clipboard
        )
        paste_btn.pack(side="right")
    
    def _build_options_section(self):
        """Build download options section"""
        self.options_frame = self._create_section("Download Options", "Select what to download")
        
        options_grid = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        options_grid.pack(fill="x")
        
        # Video option
        self.video_check = self._create_option_card(
            options_grid, "🎬", "Video", "High quality MP4", 
            self.video_var, 0, 0
        )
        
        # Audio option
        self.audio_check = self._create_option_card(
            options_grid, "🎵", "Audio", "MP3 format", 
            self.audio_var, 0, 1
        )
        
        # SRT option
        self.srt_check = self._create_option_card(
            options_grid, "📝", "Subtitles", "SRT format", 
            self.srt_var, 1, 0
        )
        
        # TXT option
        self.txt_check = self._create_option_card(
            options_grid, "📄", "Transcript", "Plain text", 
            self.txt_var, 1, 1
        )
        
        options_grid.grid_columnconfigure(0, weight=1)
        options_grid.grid_columnconfigure(1, weight=1)
    
    def _create_option_card(self, parent, icon, title, subtitle, variable, row, col):
        """Create an option card with icon, title, subtitle, and checkbox"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["md"],
            border_width=2,
            border_color=COLORS["border"]
        )
        card.grid(row=row, column=col, padx=SPACING["xs"], pady=SPACING["xs"], sticky="ew")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        # Icon and text
        left_frame = ctk.CTkFrame(inner, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        icon_label = ctk.CTkLabel(
            left_frame,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left", padx=(0, SPACING["sm"]))
        
        text_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        text_frame.pack(side="left")
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        sub_label = ctk.CTkLabel(
            text_frame,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        sub_label.pack(anchor="w")
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            inner,
            text="",
            variable=variable,
            width=20,
            height=20,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=6,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            border_color=COLORS["border"]
        )
        checkbox.pack(side="right")
        
        # Make entire card clickable
        def toggle_checkbox(event=None):
            variable.set(not variable.get())
        
        for widget in [card, inner, left_frame, icon_label, text_frame, title_label, sub_label]:
            widget.bind("<Button-1>", toggle_checkbox)
        
        return checkbox
    
    def _build_playlist_section(self):
        """Build playlist mode section"""
        self.playlist_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["md"],
            border_width=2,
            border_color=COLORS["accent_primary"]
        )
        self.playlist_frame.pack(fill="x", pady=(SPACING["md"], 0))
        
        inner = ctk.CTkFrame(self.playlist_frame, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        # Icon and label
        icon_label = ctk.CTkLabel(
            inner,
            text="📂",
            font=ctk.CTkFont(size=20)
        )
        icon_label.pack(side="left", padx=(0, SPACING["sm"]))
        
        text_frame = ctk.CTkFrame(inner, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            text_frame,
            text="Playlist Mode",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_primary"]
        )
        title_label.pack(anchor="w")
        
        hint_label = ctk.CTkLabel(
            text_frame,
            text="Download all videos in the playlist",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        hint_label.pack(anchor="w")
        
        # Switch
        self.playlist_switch = ctk.CTkSwitch(
            inner,
            text="",
            variable=self.playlist_var,
            width=40,
            height=20,
            fg_color=COLORS["bg_tertiary"],
            progress_color=COLORS["accent_primary"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["text_secondary"]
        )
        self.playlist_switch.pack(side="right")
    
    def _build_save_section(self):
        """Build save path section"""
        section_frame = self._create_section("Save Location", "Where to save downloaded files")
        
        path_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        path_container.pack(fill="x")
        
        self.save_entry = ctk.CTkEntry(
            path_container,
            textvariable=self.save_path_var,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            corner_radius=RADIUS["md"]
        )
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["sm"]))
        
        browse_btn = ctk.CTkButton(
            path_container,
            text="Browse",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            command=self._browse_directory
        )
        browse_btn.pack(side="right")
    
    def _build_audio_format_section(self):
        """Placeholder - only MP3 supported, no dropdown needed"""
        self.audio_format_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        # Empty frame, never shown
    
    def _build_subtitle_section(self):
        """Build subtitle language selection (hidden by default)"""
        self.subtitle_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["md"]
        )
        # Hidden by default
        
        inner = ctk.CTkFrame(self.subtitle_frame, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        label = ctk.CTkLabel(
            inner,
            text="🌐  Subtitle Language",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        label.pack(side="left")
        
        languages = ["detect", "all", "en", "es", "fr", "de", "ko", "ja", "ru", "it", "pt", "zh-Hans", "zh-Hant"]
        
        self.lang_dropdown = ctk.CTkOptionMenu(
            inner,
            variable=self.lang_var,
            values=languages,
            width=120,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_tertiary"],
            button_color=COLORS["bg_hover"],
            button_hover_color=COLORS["accent_primary"],
            dropdown_fg_color=COLORS["bg_secondary"],
            dropdown_hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["sm"]
        )
        self.lang_dropdown.pack(side="right")
    
    def _build_trim_section(self):
        """Build video trim section"""
        self.trim_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["md"]
        )
        # Hidden by default, shown when video is selected
        
        inner = ctk.CTkFrame(self.trim_frame, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        header = ctk.CTkLabel(
            inner,
            text="✂️  Trim Video (Optional)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header.pack(anchor="w", pady=(0, SPACING["sm"]))
        
        time_container = ctk.CTkFrame(inner, fg_color="transparent")
        time_container.pack(fill="x")
        
        # Start time
        start_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING["sm"]))
        
        start_label = ctk.CTkLabel(
            start_frame,
            text="Start Time",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        start_label.pack(anchor="w")
        
        self.trim_start_entry = ctk.CTkEntry(
            start_frame,
            textvariable=self.trim_start_var,
            placeholder_text="00:00:00",
            height=32,
            font=ctk.CTkFont(size=12, family="Menlo"),
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            corner_radius=RADIUS["sm"]
        )
        self.trim_start_entry.pack(fill="x")
        
        # End time
        end_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        end_frame.pack(side="right", fill="x", expand=True, padx=(SPACING["sm"], 0))
        
        end_label = ctk.CTkLabel(
            end_frame,
            text="End Time",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        end_label.pack(anchor="w")
        
        self.trim_end_entry = ctk.CTkEntry(
            end_frame,
            textvariable=self.trim_end_var,
            placeholder_text="00:00:00",
            height=32,
            font=ctk.CTkFont(size=12, family="Menlo"),
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            corner_radius=RADIUS["sm"]
        )
        self.trim_end_entry.pack(fill="x")
        
        # Note
        note_label = ctk.CTkLabel(
            inner,
            text="Format: HH:MM:SS or MM:SS • Disabled for playlists",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        note_label.pack(anchor="w", pady=(SPACING["sm"], 0))
    
    def _build_action_section(self):
        """Build download button and progress section"""
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x", pady=(SPACING["md"], SPACING["lg"]))
        
        # Download button with gradient effect
        self.download_btn = ctk.CTkButton(
            action_frame,
            text="⬇️  Download",
            height=42,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_secondary"],
            corner_radius=RADIUS["lg"],
            command=self._start_download
        )
        self.download_btn.pack(fill="x")
        
        # Progress section
        self.progress_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(SPACING["md"], 0))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=8,
            corner_radius=4,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent_primary"]
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(anchor="w", pady=(SPACING["xs"], 0))
    
    def _create_section(self, title: str, subtitle: str = ""):
        """Create a section with title and optional subtitle"""
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(fill="x", pady=(SPACING["sm"], 0))
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        if subtitle:
            sub_label = ctk.CTkLabel(
                frame,
                text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_muted"]
            )
            sub_label.pack(anchor="w", pady=(0, SPACING["xs"]))
        
        return frame
    
    def _paste_from_clipboard(self):
        """Paste URL from clipboard"""
        try:
            clipboard = self.clipboard_get()
            if clipboard.startswith("http"):
                self.url_var.set(clipboard)
        except:
            pass
    
    def _browse_directory(self):
        """Open directory browser"""
        path = filedialog.askdirectory(
            initialdir=self.save_path_var.get() or str(Path.home())
        )
        if path:
            self.save_path_var.set(path)
    
    def _toggle_subtitle_options(self, *args):
        """Show/hide subtitle language dropdown"""
        if self.srt_var.get() or self.txt_var.get():
            self.subtitle_frame.pack(fill="x", pady=(SPACING["md"], 0), after=self.playlist_frame)
        else:
            self.subtitle_frame.pack_forget()
    
    def _toggle_trim_options(self, *args):
        """Show/hide and enable/disable trim options"""
        if self.video_var.get():
            self.trim_frame.pack(fill="x", pady=(SPACING["md"], 0), before=self.progress_frame.master)
            
            # Disable when playlist mode is on
            state = "disabled" if self.playlist_var.get() else "normal"
            self.trim_start_entry.configure(state=state)
            self.trim_end_entry.configure(state=state)
        else:
            self.trim_frame.pack_forget()
    
    def _toggle_audio_format_options(self, *args):
        """Show/hide audio format dropdown"""
        if self.audio_var.get():
            self.audio_format_frame.pack(fill="x", pady=(SPACING["md"], 0), after=self.options_frame)
        else:
            self.audio_format_frame.pack_forget()
    
    def _update_progress(self, progress: DownloadProgress):
        """Update UI with progress information"""
        def update():
            self.progress_bar.set(progress.percentage / 100)
            
            if progress.is_error:
                self.status_label.configure(
                    text=f"❌ {progress.error_message}",
                    text_color=COLORS["error"]
                )
                self.download_btn.configure(state="normal")
            elif progress.is_complete:
                self.status_label.configure(
                    text="✅ Download complete!",
                    text_color=COLORS["success"]
                )
                self.download_btn.configure(state="normal")
                self.bell()
            else:
                self.status_label.configure(
                    text=progress.status,
                    text_color=COLORS["text_secondary"]
                )
        
        self.after(0, update)
    
    def _start_download(self):
        """Start the download process"""
        url = self.url_var.get().strip()
        save_path = self.save_path_var.get().strip()
        
        # Validation
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
            return
        
        if not save_path:
            messagebox.showwarning("Missing Path", "Please select a save location.")
            return
        
        if not any([self.video_var.get(), self.audio_var.get(), 
                    self.srt_var.get(), self.txt_var.get()]):
            messagebox.showwarning("No Selection", "Please select at least one download option.")
            return
        
        # Disable button and start download
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...", text_color=COLORS["text_secondary"])
        
        # Create downloader with progress callback
        downloader = YouTubeDownloader(progress_callback=self._update_progress)
        
        def run_download():
            try:
                downloader.download(
                    url=url,
                    save_path=save_path,
                    dl_video=self.video_var.get(),
                    dl_audio=self.audio_var.get(),
                    dl_srt=self.srt_var.get(),
                    dl_txt=self.txt_var.get(),
                    subtitle_lang=self.lang_var.get(),
                    download_playlist=self.playlist_var.get(),
                    trim_start=self.trim_start_var.get(),
                    trim_end=self.trim_end_var.get()
                )
            except ValueError as e:
                self._update_progress(DownloadProgress(is_error=True, error_message=str(e)))
            except Exception as e:
                self._update_progress(DownloadProgress(is_error=True, error_message=str(e)))
        
        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()
    
    def _on_closing(self):
        """Save config and close"""
        self.config_manager.update(
            save_path=self.save_path_var.get(),
            dl_video=self.video_var.get(),
            dl_audio=self.audio_var.get(),
            dl_srt=self.srt_var.get(),
            dl_txt=self.txt_var.get(),
            subtitle_lang=self.lang_var.get(),
            audio_format=self.audio_format_var.get(),
            download_playlist=self.playlist_var.get(),
            trim_start=self.trim_start_var.get(),
            trim_end=self.trim_end_var.get()
        )
        self.destroy()


def main():
    app = ModernYouTubeDownloader()
    app.mainloop()


if __name__ == "__main__":
    main()
