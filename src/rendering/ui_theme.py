"""
UI Theme - design tokens and reusable drawing primitives.

Everything visual in the HUD, tutorial, and debug overlays pulls from
here so the app looks cohesive. Change a token here and the whole
interface updates.

Palette philosophy:
    - Dark, layered surfaces (BG_DEEP -> BG_CARD -> BG_ELEVATED)
    - One signature accent (teal) used for highlights + CTAs
    - Semantic colors (success/warning/danger/info) muted, not harsh
    - Text has three legibility tiers (primary/secondary/muted)
"""

import pygame


# =============================================================================
# COLOR TOKENS
# =============================================================================

# Backgrounds (layered depth)
BG_DEEP      = (12, 16, 23)       # behind everything
BG_CANVAS    = (20, 26, 36)       # main canvas
BG_CARD      = (28, 37, 51)       # card surface
BG_ELEVATED  = (40, 52, 70)       # elevated element
BG_OVERLAY   = (6, 9, 14, 230)    # modal overlay (RGBA)
BG_GLASS     = (22, 30, 42, 240)  # translucent card (RGBA) - opaque enough to block world behind

# Borders
BORDER_SUBTLE = (46, 60, 80)
BORDER_STRONG = (72, 90, 114)

# Text (three legibility tiers)
TEXT_PRIMARY    = (235, 242, 252)
TEXT_SECONDARY  = (160, 176, 198)
TEXT_MUTED      = (105, 120, 144)

# Accent - single signature color, used sparingly
ACCENT          = (100, 227, 210)      # soft teal
ACCENT_BRIGHT   = (140, 255, 232)
ACCENT_DIM      = (55, 150, 140)

# Semantic (muted, no harsh primaries)
SUCCESS         = (134, 239, 172)
SUCCESS_DIM     = (60, 140, 95)
WARNING         = (251, 191, 36)
WARNING_DIM     = (160, 120, 30)
DANGER          = (248, 113, 113)
DANGER_DIM      = (170, 60, 60)
INFO            = (147, 197, 253)
INFO_DIM        = (80, 130, 200)


# =============================================================================
# TYPOGRAPHY
# =============================================================================
# Cascade of modern fonts - pygame tries each in order, falls back to default.
_FONT_CASCADE = (
    "sfprodisplay,sf pro display,"
    "inter,interregular,"
    "segoeuivariable,segoe ui variable,segoeui,segoe ui,"
    "roboto,helveticaneue,helvetica,arial,sans-serif"
)

_font_cache = {}


def font(size: int, weight: str = "regular") -> pygame.font.Font:
    """Cached system font lookup. weight: 'regular' | 'bold'."""
    key = (size, weight)
    if key not in _font_cache:
        bold = (weight == "bold")
        try:
            f = pygame.font.SysFont(_FONT_CASCADE, size, bold=bold)
        except Exception:
            f = pygame.font.Font(None, size)
        _font_cache[key] = f
    return _font_cache[key]


def render_text(text: str, size: int, color, weight: str = "regular"):
    """Shortcut: render antialiased text."""
    return font(size, weight).render(text, True, color)


# =============================================================================
# PRIMITIVE COMPONENTS
# =============================================================================

def draw_card(surface, rect, bg=BG_CARD, border=BORDER_SUBTLE,
              radius: int = 10, shadow: bool = True):
    """Rounded card with an optional subtle drop shadow."""
    if shadow:
        sh = pygame.Surface((rect.w + 10, rect.h + 14), pygame.SRCALPHA)
        pygame.draw.rect(
            sh, (0, 0, 0, 70),
            pygame.Rect(5, 6, rect.w, rect.h),
            border_radius=radius,
        )
        surface.blit(sh, (rect.x - 5, rect.y - 3))

    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 1, border_radius=radius)


def draw_glass_card(surface, rect, tint=BG_GLASS,
                    border=BORDER_SUBTLE, radius: int = 10):
    """Translucent card - for overlays on top of game content."""
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, tint, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border, panel.get_rect(), 1, border_radius=radius)
    surface.blit(panel, (rect.x, rect.y))


def draw_pill(surface, text: str, pos, size: int = 13,
              bg=BG_ELEVATED, fg=TEXT_PRIMARY, border=None,
              padding=(12, 6), weight: str = "regular",
              center: bool = False) -> pygame.Rect:
    """Rounded pill label. Returns the rect it drew into."""
    text_surf = render_text(text, size, fg, weight)
    w = text_surf.get_width() + padding[0] * 2
    h = text_surf.get_height() + padding[1] * 2
    x, y = pos
    if center:
        x -= w // 2
        y -= h // 2
    rect = pygame.Rect(int(x), int(y), w, h)

    if len(bg) == 4:
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=h // 2)
        if border:
            pygame.draw.rect(
                panel, border, panel.get_rect(), 1, border_radius=h // 2,
            )
        surface.blit(panel, (rect.x, rect.y))
    else:
        pygame.draw.rect(surface, bg, rect, border_radius=h // 2)
        if border:
            pygame.draw.rect(
                surface, border, rect, 1, border_radius=h // 2,
            )

    surface.blit(text_surf, (rect.x + padding[0], rect.y + padding[1]))
    return rect


def draw_keycap(surface, key_text: str, pos, size: int = 12) -> pygame.Rect:
    """Keyboard-style key cap with highlight and shadow."""
    text_surf = render_text(key_text, size, TEXT_PRIMARY, "bold")
    w = max(text_surf.get_width() + 14, 26)
    h = text_surf.get_height() + 8
    x, y = pos
    rect = pygame.Rect(x, y, w, h)

    # drop shadow
    shadow = pygame.Surface((w, h + 2), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow, (0, 0, 0, 120),
        pygame.Rect(0, 2, w, h), border_radius=5,
    )
    surface.blit(shadow, (x, y))

    # cap body
    pygame.draw.rect(surface, BG_ELEVATED, rect, border_radius=5)
    pygame.draw.rect(surface, BORDER_STRONG, rect, 1, border_radius=5)

    # top highlight (thin line)
    highlight = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.line(highlight, (255, 255, 255, 30),
                     (6, 1), (w - 7, 1), 1)
    surface.blit(highlight, (x, y))

    surface.blit(
        text_surf,
        (x + (w - text_surf.get_width()) // 2,
         y + (h - text_surf.get_height()) // 2),
    )
    return rect


def draw_progress_bar(surface, rect, value: float, max_value: float = 100.0,
                      fg=ACCENT, bg=BG_DEEP, radius: int = None):
    """Rounded progress bar."""
    if radius is None:
        radius = rect.h // 2
    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    if value > 0 and max_value > 0:
        pct = max(0.0, min(1.0, value / max_value))
        fill_w = max(rect.h, int(rect.w * pct)) if pct > 0.02 else 0
        if fill_w > 0:
            filled = pygame.Rect(rect.x, rect.y, fill_w, rect.h)
            pygame.draw.rect(surface, fg, filled, border_radius=radius)


def draw_dot(surface, pos, color, size: int = 4, glow: bool = False):
    """Status dot. Optional soft glow."""
    x, y = int(pos[0]), int(pos[1])
    if glow:
        glow_surf = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf, (*color, 50),
            (size * 3, size * 3), size * 3,
        )
        surface.blit(glow_surf, (x - size * 3, y - size * 3))
    pygame.draw.circle(surface, color, (x, y), size)


def draw_swatch(surface, pos, color, size: int = 10,
                outline=BORDER_SUBTLE):
    """Colored circle/square used in legends to represent a sprite type."""
    pygame.draw.circle(surface, color, (int(pos[0]), int(pos[1])), size)
    pygame.draw.circle(
        surface, outline, (int(pos[0]), int(pos[1])), size, 1,
    )


def draw_section_title(surface, text: str, pos,
                       size: int = 10, color=TEXT_MUTED):
    """Uppercase letter-spaced section header (Apple / Linear style)."""
    # render each char separately with a small gap for letter-spacing
    x, y = pos
    spacing = 1
    total_w = 0
    for i, ch in enumerate(text.upper()):
        ch_surf = render_text(ch, size, color, "bold")
        surface.blit(ch_surf, (x + total_w, y))
        total_w += ch_surf.get_width() + spacing
    return total_w


# =============================================================================
# GRADIENTS
# =============================================================================

def draw_vertical_gradient(surface, rect, top_color, bottom_color):
    """Simple vertical gradient fill (pygame has no native gradient)."""
    h = rect.h
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(
            surface, (r, g, b),
            (rect.x, rect.y + i), (rect.x + rect.w, rect.y + i),
        )


def draw_radial_glow(surface, pos, color, radius: int, steps: int = 12):
    """Soft radial glow by stacking translucent circles of decreasing alpha."""
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(steps, 0, -1):
        alpha = int(80 * (i / steps) ** 2)
        pygame.draw.circle(
            glow, (*color, alpha),
            (radius, radius),
            int(radius * (i / steps)),
        )
    surface.blit(glow, (pos[0] - radius, pos[1] - radius))
