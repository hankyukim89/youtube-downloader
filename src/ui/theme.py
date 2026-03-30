"""
Theme and styling constants for the modern UI
"""

# Color Palette - YouTube Red & White Theme
COLORS = {
    # Background colors - Clean white/light gray
    "bg_primary": "#ffffff",          # Pure white
    "bg_secondary": "#f9f9f9",        # Light gray card background
    "bg_tertiary": "#f1f1f1",         # Input fields, buttons
    "bg_hover": "#e5e5e5",            # Hover states
    
    # Accent colors - YouTube Red
    "accent_primary": "#ff0000",      # YouTube Red
    "accent_secondary": "#cc0000",    # Darker red for hover
    "accent_gradient_start": "#ff0000",
    "accent_gradient_end": "#cc0000", # Red gradient
    
    # Status colors
    "success": "#2ba640",             # Green
    "success_bg": "#e8f5e9",
    "warning": "#ff9800",             # Orange
    "warning_bg": "#fff3e0",
    "error": "#ff0000",               # Red
    "error_bg": "#ffebee",
    
    # Text colors
    "text_primary": "#0f0f0f",        # Almost black
    "text_secondary": "#606060",      # Gray
    "text_muted": "#909090",          # Light gray
    
    # Border colors
    "border": "#e0e0e0",
    "border_focus": "#ff0000",
    
    # Special
    "progress_bg": "#e0e0e0",
    "progress_fill": "#ff0000",
}

# Typography
FONTS = {
    "heading_large": ("SF Pro Display", 20, "bold"),
    "heading_medium": ("SF Pro Display", 16, "bold"),
    "heading_small": ("SF Pro Display", 13, "bold"),
    "body": ("SF Pro Text", 12),
    "body_medium": ("SF Pro Text", 12, "normal"),
    "body_small": ("SF Pro Text", 10),
    "button": ("SF Pro Text", 12, "bold"),
    "mono": ("SF Mono", 11),
}

# Fallback fonts for systems without SF Pro
FONTS_FALLBACK = {
    "heading_large": ("Helvetica Neue", 20, "bold"),
    "heading_medium": ("Helvetica Neue", 16, "bold"),
    "heading_small": ("Helvetica Neue", 13, "bold"),
    "body": ("Helvetica Neue", 12),
    "body_medium": ("Helvetica Neue", 12, "normal"),
    "body_small": ("Helvetica Neue", 10),
    "button": ("Helvetica Neue", 12, "bold"),
    "mono": ("Menlo", 11),
}

# Spacing
SPACING = {
    "xs": 2,
    "sm": 4,
    "md": 6,
    "lg": 8,
    "xl": 12,
    "xxl": 16,
}

# Border radius
RADIUS = {
    "sm": 4,
    "md": 6,
    "lg": 10,
    "xl": 16,
    "full": 9999,
}

# Shadows (for future use with custom widgets)
SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
}

# Animation durations (ms)
ANIMATION = {
    "fast": 150,
    "normal": 300,
    "slow": 500,
}
