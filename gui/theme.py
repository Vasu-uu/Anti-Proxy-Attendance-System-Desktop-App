"""
APCAS Design Tokens — mirrors the React/Tailwind theme.
"""

# ── Core palette ──────────────────────────────────────────────────────────────
BG         = "#0a0a0a"      # body / outer background
CARD       = "#111111"      # card surface
CARD_ALT   = "#161616"      # alternate card (slightly lighter)
BORDER     = "#262626"      # subtle border
BORDER_ALT = "#1f1f1f"      # even subtler border

# ── Brand accent (teal) ───────────────────────────────────────────────────────
PRIMARY        = "#14b8a6"
PRIMARY_DARK   = "#0d9488"
PRIMARY_GLOW   = "#14b8a6"   # used as selection / highlight bg
PRIMARY_BADGE  = "#134e4a"     # dark badge background

# ── Semantic colours ──────────────────────────────────────────────────────────
EMERALD     = "#10b981"
EMERALD_BG  = "#052e16"
RED         = "#ef4444"
RED_BG      = "#2d0a0a"
YELLOW      = "#f59e0b"
YELLOW_BG   = "#291b00"
BLUE        = "#3b82f6"
BLUE_BG     = "#0c1c3b"
PURPLE      = "#a855f7"

# ── Text ──────────────────────────────────────────────────────────────────────
TEXT        = "#f5f5f5"    # primary text
TEXT_MUTED  = "#737373"    # secondary / label
TEXT_DIM    = "#404040"    # placeholder / disabled

# ── Sidebar ───────────────────────────────────────────────────────────────────
SIDEBAR_W       = 220        # pixels
SIDEBAR_BG      = "#0f0f0f"
NAV_ACTIVE_BG   = "#14b8a6"
NAV_ACTIVE_FG   = PRIMARY
NAV_HOVER_BG    = "#ffffff"
NAV_FG          = TEXT_MUTED

# ── Typography ────────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"

def font(size: int = 13, weight: str = "normal") -> tuple:
    return (FONT_FAMILY, size, weight)

TITLE   = font(24, "bold")
HEADING = font(16, "bold")
BODY    = font(13)
SMALL   = font(11)
TINY    = font(10)
LABEL   = font(11)

# ── Widget corner radii ────────────────────────────────────────────────────────
RADIUS_SM  = 8
RADIUS_MD  = 12
RADIUS_LG  = 16
RADIUS_XL  = 20

# ── Spacing ───────────────────────────────────────────────────────────────────
PAD_SM = 8
PAD_MD = 16
PAD_LG = 24
PAD_XL = 32
