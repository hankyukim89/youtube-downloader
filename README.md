# YouTube Downloader

A modern, beautiful desktop application for downloading YouTube videos, audio, and subtitles.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)

## ✨ Features

- **🎬 Video Download** - High quality MP4 with embedded metadata and thumbnails
- **🎵 Audio Extraction** - MP3 format with full metadata
- **📝 Subtitles** - SRT format with auto-generated subtitle support
- **📄 Transcripts** - Plain text conversion of subtitles
- **📂 Playlist Support** - Download entire playlists with organized folders
- **✂️ Video Trimming** - Clip specific portions of videos
- **🌐 Multi-language Subtitles** - Support for 13+ languages

## 🚀 Quick Start

### Launch the App

**Double-click** `YouTube Downloader.command` to start the application.

Or run from terminal:
```bash
python3 run.py
```

### Requirements

- Python 3.8+
- yt-dlp
- ffmpeg

Install dependencies:
```bash
pip3 install customtkinter pillow mutagen
brew install yt-dlp ffmpeg
```

## 📁 Project Structure

```
youtube-downloader/
├── YouTube Downloader.command  # Desktop launcher
├── run.py                      # Entry point
├── src/
│   ├── config.py              # Configuration management
│   ├── downloader.py          # Core download logic
│   └── ui/
│       ├── app.py             # Main application UI
│       └── theme.py           # Color scheme and styling
└── main.py                    # Legacy single-file version
```

## 🎨 Design

The application features a modern dark theme with:
- Deep blue-black background
- Vibrant purple accent colors
- Card-based options with hover effects
- Smooth progress indicators
- Clean, readable typography

## 📝 License

MIT License - Feel free to modify and distribute.
