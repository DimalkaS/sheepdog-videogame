"""
HUD - status card (top-right), controls strip (bottom), plus the
title and ending full-screen scenes.

All visuals pull from ui_theme for a cohesive look.
"""

import math
import pygame

from ..core import settings as cfg
from . import ui_theme as ui


# =============================================================================
# In-game HUD
# =============================================================================
def draw_hud(surface, world, fps: float, debug_on: bool, rubric_on: bool):
    """Top-right stats card + bottom-center controls strip."""
    _draw_stats_card(surface, world)
    _draw_controls_strip(surface, debug_on, rubric_on)
    _draw_dog_card(surface, world.dogs)
    _draw_environment_card(surface, world)
    if cfg.SHOW_FPS:
        _draw_fps(surface, fps)


# ---------------------------------------------------------------------------
# Stats card (top-right)
# ---------------------------------------------------------------------------
def _draw_stats_card(surface, world):
    penned = sum(1 for s in world.sheep if s.alive
                 and world.is_in_pen(s.pos))
    alive  = sum(1 for s in world.sheep if s.alive)
    lost   = len(world.sheep) - alive
    total  = len(world.sheep)

    # card dims
    w = 230
    h = 112
    x = cfg.SCREEN_WIDTH - w - 16
    y = 16
    rect = pygame.Rect(x, y, w, h)
    ui.draw_glass_card(surface, rect, radius=10)

    # header - "FLOCK STATUS"
    ui.draw_section_title(
        surface, "FLOCK", (rect.x + 16, rect.y + 12),
        size=9, color=ui.TEXT_MUTED,
    )

    # big penned count
    penned_text = ui.render_text(f"{penned}", 32, ui.SUCCESS, "bold")
    surface.blit(penned_text, (rect.x + 16, rect.y + 28))

    slash = ui.render_text(f"/ {total}", 16, ui.TEXT_MUTED)
    surface.blit(
        slash,
        (rect.x + 16 + penned_text.get_width() + 4,
         rect.y + 44),
    )

    label = ui.render_text("SAVED", 10, ui.TEXT_MUTED, "bold")
    surface.blit(label, (rect.x + 16, rect.y + 68))

    # progress bar
    bar_rect = pygame.Rect(rect.x + 16, rect.y + 86, w - 32, 6)
    ui.draw_progress_bar(
        surface, bar_rect,
        value=penned, max_value=total,
        fg=ui.SUCCESS, bg=ui.BG_DEEP,
    )

    # right side: alive / lost mini-stats
    mini_x = rect.x + w - 78
    ui.draw_section_title(
        surface, "ALIVE", (mini_x, rect.y + 12),
        size=9, color=ui.TEXT_MUTED,
    )
    alive_text = ui.render_text(f"{alive}", 22, ui.TEXT_PRIMARY, "bold")
    surface.blit(alive_text, (mini_x, rect.y + 26))

    ui.draw_section_title(
        surface, "LOST", (mini_x, rect.y + 52),
        size=9, color=ui.TEXT_MUTED,
    )
    lost_color = ui.DANGER if lost > 0 else ui.TEXT_MUTED
    lost_text = ui.render_text(f"{lost}", 18, lost_color, "bold")
    surface.blit(lost_text, (mini_x, rect.y + 66))


# ---------------------------------------------------------------------------
# Dog status card (top-right, below stats)
# ---------------------------------------------------------------------------
def _draw_dog_card(surface, dogs):
    if not dogs:
        return

    # height adapts to number of dogs (one row per dog)
    w = 230
    row_h = 38
    pad_top = 28
    pad_bottom = 10
    h = pad_top + row_h * len(dogs) + pad_bottom
    x = cfg.SCREEN_WIDTH - w - 16
    y = 16 + 112 + 10
    rect = pygame.Rect(x, y, w, h)
    ui.draw_glass_card(surface, rect, radius=10)

    # Header
    ui.draw_section_title(
        surface, f"DOGS ({len(dogs)})", (rect.x + 16, rect.y + 10),
        size=9, color=ui.TEXT_MUTED,
    )

    # one row per dog: name, state pill, stamina bar
    row_y = rect.y + pad_top
    for d in dogs:
        # name
        name_surf = ui.render_text(
            d.name.upper(), 10, ui.TEXT_SECONDARY, "bold",
        )
        surface.blit(name_surf, (rect.x + 16, row_y))

        # state pill
        state_color = _dog_state_color(d.fsm.state)
        ui.draw_pill(
            surface, d.fsm.state,
            (rect.x + 60, row_y - 2),
            size=9,
            bg=(*state_color, 40),
            fg=state_color,
            border=state_color,
            padding=(8, 3),
            weight="bold",
        )

        # stamina bar
        bar_rect = pygame.Rect(rect.x + 16, row_y + 18, w - 32, 4)
        color = ui.SUCCESS if d.stamina > 40 else (
            ui.WARNING if d.stamina > 15 else ui.DANGER
        )
        ui.draw_progress_bar(
            surface, bar_rect, d.stamina, cfg.DOG_MAX_STAMINA,
            fg=color, bg=ui.BG_DEEP,
        )

        row_y += row_h


# ---------------------------------------------------------------------------
# Environment card (top-right, below dog)
# ---------------------------------------------------------------------------
def _draw_environment_card(surface, world):
    w = 230
    h = 68
    x = cfg.SCREEN_WIDTH - w - 16
    # position below the dogs card (which expands per dog count)
    dogs_card_h = 28 + 38 * max(1, len(world.dogs)) + 10
    y = 16 + 112 + 10 + dogs_card_h + 10
    rect = pygame.Rect(x, y, w, h)
    ui.draw_glass_card(surface, rect, radius=10)

    ui.draw_section_title(
        surface, "ENVIRONMENT", (rect.x + 16, rect.y + 10),
        size=9, color=ui.TEXT_MUTED,
    )

    # weather pill
    weather = world.weather.state
    weather_color = _weather_color(weather)
    ui.draw_pill(
        surface, weather,
        (rect.x + 16, rect.y + 26),
        size=10,
        bg=(*weather_color, 40),
        fg=weather_color,
        padding=(8, 3),
        weight="bold",
    )

    # time pill next to weather
    time_label = world.day_night.label()
    time_color = _time_color(time_label)
    # position after weather pill
    weather_surf = ui.render_text(weather, 10, weather_color, "bold")
    wp_width = weather_surf.get_width() + 16
    ui.draw_pill(
        surface, time_label,
        (rect.x + 16 + wp_width + 6, rect.y + 26),
        size=10,
        bg=(*time_color, 40),
        fg=time_color,
        padding=(8, 3),
        weight="bold",
    )

    # elapsed time
    t = int(world.elapsed_time)
    total = int(cfg.SIMULATION_TIME_LIMIT)
    mm, ss = t // 60, t % 60
    tmm, tss = total // 60, total % 60
    time_text = ui.render_text(
        f"{mm:02d}:{ss:02d}  /  {tmm:02d}:{tss:02d}",
        11, ui.TEXT_SECONDARY, "bold",
    )
    surface.blit(
        time_text,
        (rect.x + 16, rect.y + rect.h - time_text.get_height() - 8),
    )


# ---------------------------------------------------------------------------
# Controls strip (bottom-center, minimal)
# ---------------------------------------------------------------------------
def _draw_controls_strip(surface, debug_on: bool, rubric_on: bool):
    controls = [
        ("LMB",     "Move you"),
        ("RMB",     "Command dog"),
        ("SPACE",   "Whistle"),
        ("F1",      "Debug"),
        ("F2",      "Rubric"),
        ("R",       "Reset"),
    ]

    # measure total width
    cap_spacing = 6
    group_spacing = 18
    cap_size = 11
    label_size = 11

    total_w = 0
    heights = []
    for key, label in controls:
        cap_surf = ui.render_text(key, cap_size, ui.TEXT_PRIMARY, "bold")
        lbl_surf = ui.render_text(label, label_size, ui.TEXT_SECONDARY)
        cap_w = max(cap_surf.get_width() + 14, 26)
        cap_h = cap_surf.get_height() + 8
        total_w += cap_w + cap_spacing + lbl_surf.get_width() + group_spacing
        heights.append(cap_h)
    total_w -= group_spacing  # remove trailing spacing
    strip_h = max(heights) + 16

    # card
    pad_x = 16
    card_w = total_w + pad_x * 2
    card_x = (cfg.SCREEN_WIDTH - card_w) // 2
    card_y = cfg.SCREEN_HEIGHT - strip_h - 12
    rect = pygame.Rect(card_x, card_y, card_w, strip_h)
    ui.draw_glass_card(surface, rect, radius=strip_h // 2)

    # draw each control pair
    x = rect.x + pad_x
    cy = rect.y + rect.h // 2
    for key, label in controls:
        cap_surf = ui.render_text(key, cap_size, ui.TEXT_PRIMARY, "bold")
        cap_w = max(cap_surf.get_width() + 14, 26)
        cap_h = cap_surf.get_height() + 8
        cap_rect = ui.draw_keycap(
            surface, key, (x, cy - cap_h // 2), size=cap_size,
        )
        lbl_surf = ui.render_text(label, label_size, ui.TEXT_SECONDARY)
        surface.blit(
            lbl_surf,
            (x + cap_w + cap_spacing,
             cy - lbl_surf.get_height() // 2),
        )
        x += cap_w + cap_spacing + lbl_surf.get_width() + group_spacing


# ---------------------------------------------------------------------------
# FPS counter (bottom-right corner, tiny)
# ---------------------------------------------------------------------------
def _draw_fps(surface, fps: float):
    text = ui.render_text(f"{int(fps)} fps", 10, ui.TEXT_MUTED)
    surface.blit(
        text,
        (cfg.SCREEN_WIDTH - text.get_width() - 16, 16),
    )


# =============================================================================
# Color helpers
# =============================================================================
def _dog_state_color(state: str):
    return {
        "IDLE":         ui.TEXT_SECONDARY,
        "PATROLLING":   ui.INFO,
        "HERDING":      ui.ACCENT,
        "CHASING_WOLF": ui.DANGER,
        "RETURNING":    ui.WARNING,
        "RESTING":      ui.TEXT_MUTED,
        "EXHAUSTED":    ui.DANGER,
    }.get(state, ui.TEXT_SECONDARY)


def _weather_color(weather: str):
    return {
        "CLEAR":  ui.WARNING,
        "CLOUDY": ui.TEXT_SECONDARY,
        "RAIN":   ui.INFO,
        "STORM":  ui.DANGER,
        "FOG":    ui.TEXT_MUTED,
    }.get(weather, ui.TEXT_SECONDARY)


def _time_color(time_label: str):
    return {
        "DAY":   ui.WARNING,
        "DAWN":  (255, 165, 120),
        "DUSK":  (200, 120, 180),
        "NIGHT": (130, 140, 200),
    }.get(time_label, ui.TEXT_SECONDARY)


# =============================================================================
# Title screen
# =============================================================================
def draw_title_screen(surface):
    """Modern title / splash screen."""
    # gradient background
    ui.draw_vertical_gradient(
        surface, surface.get_rect(),
        ui.BG_DEEP, (ui.BG_CANVAS[0] + 5, ui.BG_CANVAS[1] + 8, ui.BG_CANVAS[2] + 14),
    )

    # Large centered title block
    cx = cfg.SCREEN_WIDTH // 2
    cy = cfg.SCREEN_HEIGHT // 2

    # eyebrow (centered, letter-spaced)
    _draw_centered_eyebrow(surface, "AI  AGENT  SIMULATION", cy - 120,
                           size=12, color=ui.ACCENT)

    title_surf = ui.render_text("Sheep Dog", 78, ui.TEXT_PRIMARY, "bold")
    surface.blit(
        title_surf,
        (cx - title_surf.get_width() // 2, cy - 90),
    )

    sub_surf = ui.render_text(
        "Intelligent agents.  Dynamic weather.  No two runs alike.",
        16, ui.TEXT_SECONDARY,
    )
    surface.blit(
        sub_surf,
        (cx - sub_surf.get_width() // 2, cy + 4),
    )

    # CTA pill
    cta_text = "Press  ENTER  to begin"
    cta_surf = ui.render_text(cta_text, 14, ui.ACCENT, "bold")
    cta_pad = (20, 12)
    cta_w = cta_surf.get_width() + cta_pad[0] * 2
    cta_h = cta_surf.get_height() + cta_pad[1] * 2
    cta_rect = pygame.Rect(
        cx - cta_w // 2, cy + 56, cta_w, cta_h,
    )
    # subtle accent glow
    glow = pygame.Surface((cta_w + 20, cta_h + 20), pygame.SRCALPHA)
    pygame.draw.rect(
        glow, (*ui.ACCENT, 30),
        glow.get_rect(), border_radius=cta_h // 2 + 4,
    )
    surface.blit(glow, (cta_rect.x - 10, cta_rect.y - 10))

    pygame.draw.rect(surface, ui.BG_CARD, cta_rect, border_radius=cta_h // 2)
    pygame.draw.rect(
        surface, ui.ACCENT, cta_rect, 1, border_radius=cta_h // 2,
    )
    surface.blit(
        cta_surf,
        (cta_rect.x + cta_pad[0], cta_rect.y + cta_pad[1]),
    )

    # footer
    footer = ui.render_text(
        "Built with pygame  -  Press ESC to quit",
        11, ui.TEXT_MUTED,
    )
    surface.blit(
        footer,
        (cx - footer.get_width() // 2, cfg.SCREEN_HEIGHT - 32),
    )


def _draw_centered_eyebrow(surface, text, y, size, color):
    """Render letter-spaced uppercase text horizontally centered at y."""
    spacing = 2
    chars = []
    total_w = 0
    for ch in text:
        ch_surf = ui.render_text(ch, size, color, "bold")
        chars.append(ch_surf)
        total_w += ch_surf.get_width() + spacing
    total_w -= spacing

    x = cfg.SCREEN_WIDTH // 2 - total_w // 2
    for ch_surf in chars:
        surface.blit(ch_surf, (x, y))
        x += ch_surf.get_width() + spacing


# =============================================================================
# Ending screen
# =============================================================================
ENDING_DATA = {
    "ALL_SAVED": {
        "title": "Perfect Run",
        "subtitle": "All sheep returned safely to the pen.",
        "color":   "SUCCESS",
        "icon":    "OK",
    },
    "PARTIAL_WIN": {
        "title": "Success",
        "subtitle": "Most of the flock made it home.",
        "color":   "SUCCESS",
        "icon":    "OK",
    },
    "PARTIAL_LOSS": {
        "title": "Too Few Saved",
        "subtitle": "The flock thinned out before you could finish.",
        "color":   "WARNING",
        "icon":    "!",
    },
    "WOLVES_WIN": {
        "title": "The Wolves Won",
        "subtitle": "Every sheep was lost.",
        "color":   "DANGER",
        "icon":    "X",
    },
    "DOG_EXHAUSTED": {
        "title": "Dog Collapsed",
        "subtitle": "Rex ran himself to exhaustion.",
        "color":   "WARNING",
        "icon":    "!",
    },
}


def draw_ending_screen(surface, world):
    """Modern ending / results screen."""
    # dim background
    ui.draw_vertical_gradient(
        surface, surface.get_rect(),
        ui.BG_DEEP, ui.BG_CANVAS,
    )

    data = ENDING_DATA.get(world.ending, ENDING_DATA["PARTIAL_LOSS"])
    color = {
        "SUCCESS": ui.SUCCESS,
        "WARNING": ui.WARNING,
        "DANGER":  ui.DANGER,
    }[data["color"]]

    cx = cfg.SCREEN_WIDTH // 2

    # Status icon
    icon_size = 64
    icon_cy = 150
    pygame.draw.circle(
        surface, (*color, 30) if False else ui.BG_CARD,
        (cx, icon_cy), icon_size // 2,
    )
    pygame.draw.circle(
        surface, color, (cx, icon_cy), icon_size // 2, 2,
    )
    icon_surf = ui.render_text(data["icon"], 32, color, "bold")
    surface.blit(
        icon_surf,
        (cx - icon_surf.get_width() // 2,
         icon_cy - icon_surf.get_height() // 2),
    )

    # Title
    title_surf = ui.render_text(data["title"], 44, ui.TEXT_PRIMARY, "bold")
    surface.blit(title_surf, (cx - title_surf.get_width() // 2, 210))

    # Subtitle
    sub_surf = ui.render_text(data["subtitle"], 16, ui.TEXT_SECONDARY)
    surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, 270))

    # Stats grid (4 cards in a row)
    alive  = sum(1 for s in world.sheep if s.alive)
    penned = sum(1 for s in world.sheep if s.alive
                 and world.is_in_pen(s.pos))
    lost   = len(world.sheep) - alive
    wolves_alive = sum(1 for w in world.wolves if w.alive)

    stats = [
        ("PENNED", str(penned),           ui.SUCCESS),
        ("LOST",   str(lost),              ui.DANGER),
        ("WOLVES", f"{wolves_alive}",      ui.TEXT_SECONDARY),
        ("TIME",   f"{int(world.elapsed_time)}s",   ui.TEXT_SECONDARY),
    ]

    card_w = 128
    card_h = 96
    gap = 16
    total_w = card_w * len(stats) + gap * (len(stats) - 1)
    start_x = cx - total_w // 2
    y = 330
    for i, (label, value, c) in enumerate(stats):
        x = start_x + i * (card_w + gap)
        rect = pygame.Rect(x, y, card_w, card_h)
        ui.draw_card(surface, rect, radius=10)

        # label on top (muted, small)
        label_surf = ui.render_text(label, 10, ui.TEXT_MUTED, "bold")
        surface.blit(
            label_surf,
            (rect.x + (rect.w - label_surf.get_width()) // 2,
             rect.y + 14),
        )

        # big number below label
        val_surf = ui.render_text(value, 32, c, "bold")
        surface.blit(
            val_surf,
            (rect.x + (rect.w - val_surf.get_width()) // 2,
             rect.y + 38),
        )

    # Weather history as pills
    wh_y = y + card_h + 36
    ui.draw_section_title(
        surface, "WEATHER HISTORY",
        (cx - 80, wh_y), size=10, color=ui.TEXT_MUTED,
    )

    hist = world.weather.history[-6:]
    pill_x = cx - (len(hist) * 58) // 2
    for w in hist:
        wc = _weather_color(w)
        rect = ui.draw_pill(
            surface, w, (pill_x, wh_y + 18),
            size=10,
            bg=(*wc, 30),
            fg=wc,
            padding=(8, 3),
            weight="bold",
        )
        pill_x += rect.w + 6

    # CTAs
    cta_y = cfg.SCREEN_HEIGHT - 80
    cta_text = "Press  R  to play again   -   ESC  to quit"
    cta_surf = ui.render_text(cta_text, 13, ui.TEXT_MUTED)
    surface.blit(
        cta_surf,
        (cx - cta_surf.get_width() // 2, cta_y),
    )
