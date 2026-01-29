"""
Configuration management for YouTube Downloader
"""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class DownloadConfig:
    """Stores all user preferences and settings"""
    save_path: str = field(default_factory=lambda: str(Path.home() / "Downloads" / "YT-Downloads"))
    dl_video: bool = True
    dl_audio: bool = False
    dl_srt: bool = False
    dl_txt: bool = False
    subtitle_lang: str = "detect"
    audio_format: str = "mp3"  # mp3 or wav
    download_playlist: bool = True
    trim_start: str = ""
    trim_end: str = ""
    theme: str = "dark"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DownloadConfig':
        # Handle legacy config keys
        if "dl_movie" in data:
            data["dl_video"] = data.pop("dl_movie")
        if "dl_music" in data:
            data["dl_audio"] = data.pop("dl_music")
        
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class ConfigManager:
    """Handles loading and saving configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Store config in app directory
            self.config_path = Path(__file__).parent.parent / "yt_downloader_config.json"
        self._config: Optional[DownloadConfig] = None
    
    @property
    def config(self) -> DownloadConfig:
        if self._config is None:
            self._config = self.load()
        return self._config
    
    def load(self) -> DownloadConfig:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                return DownloadConfig.from_dict(data)
            except (json.JSONDecodeError, IOError):
                pass
        return DownloadConfig()
    
    def save(self, config: Optional[DownloadConfig] = None) -> None:
        """Save configuration to file"""
        if config is not None:
            self._config = config
        if self._config is not None:
            with open(self.config_path, "w") as f:
                json.dump(self._config.to_dict(), f, indent=4)
    
    def update(self, **kwargs) -> None:
        """Update specific config values"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save()
