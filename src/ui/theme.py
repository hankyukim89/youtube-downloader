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
    "heading_large": ("SF Pro Display", 24, "bold"),
    "heading_medium": ("SF Pro Display", 18, "bold"),
    "heading_small": ("SF Pro Display", 14, "bold"),
    "body": ("SF Pro Text", 13),
    "body_medium": ("SF Pro Text", 13, "normal"),
    "body_small": ("SF Pro Text", 11),
    "button": ("SF Pro Text", 13, "bold"),
    "mono": ("SF Mono", 12),
}

# Fallback fonts for systems without SF Pro
FONTS_FALLBACK = {
    "heading_large": ("Helvetica Neue", 24, "bold"),
    "heading_medium": ("Helvetica Neue", 18, "bold"),
    "heading_small": ("Helvetica Neue", 14, "bold"),
    "body": ("Helvetica Neue", 13),
    "body_medium": ("Helvetica Neue", 13, "normal"),
    "body_small": ("Helvetica Neue", 11),
    "button": ("Helvetica Neue", 13, "bold"),
    "mono": ("Menlo", 12),
}

# Spacing
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48,
}

# Border radius
RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 14,
    "xl": 20,
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
