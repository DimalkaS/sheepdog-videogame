"""
Renderer - all drawing logic for the world and agents.

Agents are drawn procedurally with pygame shapes rather than with
sprite assets.  This keeps the project self-contained (no downloads
required) and the shapes are clear enough for a grading demo.

Each agent type has a distinctive silhouette:
    Sheep : round white body, dark face
    Dog   : brown elongated body, pointed ears
    Wolf  : dark grey body, glowing eyes
    Owner : red tunic, hat
"""

import math
import pygame
from ..core import settings as cfg
from ..world import world as world_mod


# ---------------------------------------------------------------------------
# Tile drawing
# ---------------------------------------------------------------------------
def draw_world(surface, world):
    """Draw the tile map onto the surface."""
    # background grass first (cheap base layer)
    surface.fill(cfg.GRASS_GREEN)

    for row in range(cfg.WORLD_ROWS):
        for col in range(cfg.WORLD_COLS):
            tile = world.tiles[row][col]
            x = col * cfg.TILE_SIZE
            y = row * cfg.TILE_SIZE
            rect = pygame.Rect(x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)

            if tile == world_mod.GRASS:
                continue  # already grass-colored
            elif tile == world_mod.GRASS_DARK:
                pygame.draw.rect(surface, cfg.GRASS_DARK, rect)
            elif tile == world_mod.DIRT:
                pygame.draw.rect(surface, cfg.DIRT, rect)
            elif tile == world_mod.WATER:
                pygame.draw.rect(surface, cfg.WATER, rect)
                # lighter highlight
                pygame.draw.rect(surface, (100, 160, 210),
                                 rect.inflate(-6, -6), 1)
            elif tile == world_mod.PRECIPICE:
                pygame.draw.rect(surface, cfg.PRECIPICE, rect)
                # jagged edge indicator
                pygame.draw.rect(surface, cfg.BLACK, rect, 2)
            elif tile == world_mod.TREE:
                pygame.draw.rect(surface, cfg.GRASS_DARK, rect)
                # trunk
                pygame.draw.rect(
                    surface, (90, 60, 40),
                    pygame.Rect(x + cfg.TILE_SIZE // 2 - 3,
                                y + cfg.TILE_SIZE - 10, 6, 8),
                )
                # canopy
                pygame.draw.circle(
                    surface, cfg.TREE,
                    (x + cfg.TILE_SIZE // 2, y + cfg.TILE_SIZE // 2 - 2),
                    cfg.TILE_SIZE // 2 - 3,
                )
            elif tile == world_mod.ROCK:
                pygame.draw.rect(surface, cfg.GRASS_DARK, rect)
                pygame.draw.circle(
                    surface, cfg.ROCK,
                    (x + cfg.TILE_SIZE // 2, y + cfg.TILE_SIZE // 2),
                    cfg.TILE_SIZE // 2 - 4,
                )
                pygame.draw.circle(
                    surface, (150, 150, 155),
                    (x + cfg.TILE_SIZE // 2 - 3, y + cfg.TILE_SIZE // 2 - 3),
                    3,
                )
            elif tile == world_mod.FENCE:
                pygame.draw.rect(surface, cfg.GRASS_GREEN, rect)
                # two horizontal planks
                pygame.draw.rect(
                    surface, cfg.FENCE,
                    pygame.Rect(x, y + 6, cfg.TILE_SIZE, 4),
                )
                pygame.draw.rect(
                    surface, cfg.FENCE,
                    pygame.Rect(x, y + cfg.TILE_SIZE - 12, cfg.TILE_SIZE, 4),
                )
                # posts
                for px in (x + 4, x + cfg.TILE_SIZE - 8):
                    pygame.draw.rect(
                        surface, (110, 80, 50),
                        pygame.Rect(px, y + 2, 4, cfg.TILE_SIZE - 4),
                    )
            elif tile == world_mod.PEN:
                pygame.draw.rect(surface, (155, 180, 120), rect)
                # hay color


# ---------------------------------------------------------------------------
# Agent drawing
# ---------------------------------------------------------------------------
def draw_agents(surface, world):
    # order: sheep -> wolves -> dogs -> owner (top-most)
    for s in world.sheep:
        _draw_sheep(surface, s)
    for w in world.wolves:
        _draw_wolf(surface, w)
    for d in world.dogs:
        _draw_dog(surface, d)
    _draw_owner(surface, world.owner)


def _draw_sheep(surface, sheep):
    if not sheep.alive:
        # draw a small grey X to mark a kill site
        x, y = int(sheep.pos.x), int(sheep.pos.y)
        pygame.draw.line(surface, cfg.DARK_GRAY, (x - 4, y - 4), (x + 4, y + 4), 2)
        pygame.draw.line(surface, cfg.DARK_GRAY, (x - 4, y + 4), (x + 4, y - 4), 2)
        return

    x, y = int(sheep.pos.x), int(sheep.pos.y)
    # body
    pygame.draw.circle(surface, cfg.SHEEP_COLOR, (x, y), sheep.radius)
    pygame.draw.circle(surface, (200, 200, 190), (x, y), sheep.radius, 1)

    # face direction dot
    fx = x + int(math.cos(math.radians(sheep.facing_deg)) * (sheep.radius - 1))
    fy = y + int(math.sin(math.radians(sheep.facing_deg)) * (sheep.radius - 1))
    pygame.draw.circle(surface, cfg.SHEEP_FACE, (fx, fy), 3)

    # pent indicator
    if sheep.fsm.state == "PENNED":
        pygame.draw.circle(surface, cfg.GREEN, (x, y - 14), 3)

    _draw_emotion_tag(surface, sheep)
    _draw_speech(surface, sheep)


def _draw_dog(surface, dog):
    if dog is None:
        return
    x, y = int(dog.pos.x), int(dog.pos.y)

    if not dog.alive:
        pygame.draw.circle(surface, cfg.DARK_GRAY, (x, y), dog.radius + 2, 2)
        return

    # body color depends on role - herder is brown, defender is darker
    # so the player can tell the two dogs apart at a glance
    if getattr(dog, "role", "herder") == "defender":
        body_color = (60, 50, 60)        # dark grey-brown
        muzzle_color = (95, 80, 80)
    else:
        body_color = cfg.DOG_COLOR        # default brown
        muzzle_color = (110, 85, 55)

    # elongated body along facing direction
    rad = math.radians(dog.facing_deg)
    fx, fy = math.cos(rad), math.sin(rad)
    # ellipse approximated as two circles
    head_x = x + int(fx * dog.radius * 0.6)
    head_y = y + int(fy * dog.radius * 0.6)
    tail_x = x - int(fx * dog.radius * 0.5)
    tail_y = y - int(fy * dog.radius * 0.5)

    pygame.draw.circle(surface, body_color, (tail_x, tail_y), dog.radius)
    pygame.draw.circle(surface, body_color, (head_x, head_y), dog.radius - 1)
    # muzzle
    mz_x = head_x + int(fx * 6)
    mz_y = head_y + int(fy * 6)
    pygame.draw.circle(surface, muzzle_color, (mz_x, mz_y), 3)
    # eyes
    pygame.draw.circle(surface, cfg.WHITE, (mz_x, mz_y), 2, 1)
    # state-indicating collar color
    collar_color = _state_color_dog(dog.fsm.state)
    pygame.draw.circle(surface, collar_color, (x, y), dog.radius + 3, 2)

    # stamina bar
    _draw_stamina_bar(surface, dog)
    _draw_emotion_tag(surface, dog)
    _draw_speech(surface, dog)


def _draw_wolf(surface, wolf):
    x, y = int(wolf.pos.x), int(wolf.pos.y)

    if not wolf.alive:
        return

    rad = math.radians(wolf.facing_deg)
    fx, fy = math.cos(rad), math.sin(rad)
    head_x = x + int(fx * wolf.radius * 0.7)
    head_y = y + int(fy * wolf.radius * 0.7)
    tail_x = x - int(fx * wolf.radius * 0.4)
    tail_y = y - int(fy * wolf.radius * 0.4)

    pygame.draw.circle(surface, cfg.WOLF_COLOR, (tail_x, tail_y), wolf.radius)
    pygame.draw.circle(surface, cfg.WOLF_COLOR, (head_x, head_y), wolf.radius - 1)
    # glowing eyes
    eye_offset_x = int(-fy * 3)
    eye_offset_y = int(fx * 3)
    eye_color = cfg.YELLOW if wolf.fsm.state in ("CHARGE", "STALK") else cfg.RED
    pygame.draw.circle(
        surface, eye_color,
        (head_x + int(fx * 3) + eye_offset_x, head_y + int(fy * 3) + eye_offset_y),
        2,
    )
    pygame.draw.circle(
        surface, eye_color,
        (head_x + int(fx * 3) - eye_offset_x, head_y + int(fy * 3) - eye_offset_y),
        2,
    )
    # ears (two triangles)
    ear1 = (head_x - int(fy * 5), head_y + int(fx * 5))
    ear2 = (head_x + int(fy * 5), head_y - int(fx * 5))
    pygame.draw.circle(surface, (40, 40, 50), ear1, 2)
    pygame.draw.circle(surface, (40, 40, 50), ear2, 2)

    # state indicator outline
    outline_color = _state_color_wolf(wolf.fsm.state)
    pygame.draw.circle(surface, outline_color, (x, y), wolf.radius + 3, 2)

    _draw_emotion_tag(surface, wolf)
    _draw_speech(surface, wolf)


def _draw_owner(surface, owner):
    if owner is None:
        return
    x, y = int(owner.pos.x), int(owner.pos.y)

    # Herd-mode aura: pulsing green ring showing the push radius
    if getattr(owner, "herd_mode", False):
        import math as _math
        pulse = abs(_math.sin(pygame.time.get_ticks() * 0.004)) * 0.35 + 0.55
        aura_r = int(cfg.OWNER_HERD_RADIUS)
        aura_surf = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
        aura_alpha = int(55 * pulse)
        pygame.draw.circle(
            aura_surf, (80, 220, 100, aura_alpha),
            (aura_r + 2, aura_r + 2), aura_r,
        )
        pygame.draw.circle(
            aura_surf, (80, 220, 100, int(aura_alpha * 1.8)),
            (aura_r + 2, aura_r + 2), aura_r, 2,
        )
        surface.blit(aura_surf, (x - aura_r - 2, y - aura_r - 2))

    # body
    pygame.draw.circle(surface, cfg.OWNER_COLOR, (x, y), owner.radius)
    # head
    pygame.draw.circle(surface, (230, 200, 170), (x, y - owner.radius - 1), 5)
    # hat
    pygame.draw.rect(
        surface, (80, 60, 40),
        pygame.Rect(x - 8, y - owner.radius - 7, 16, 3),
    )
    pygame.draw.rect(
        surface, (80, 60, 40),
        pygame.Rect(x - 5, y - owner.radius - 11, 10, 5),
    )

    # small green badge on body when herd mode is on
    if getattr(owner, "herd_mode", False):
        pygame.draw.circle(surface, (60, 220, 80), (x + owner.radius - 2, y - 3), 4)
        pygame.draw.circle(surface, cfg.WHITE, (x + owner.radius - 2, y - 3), 4, 1)

    _draw_speech(surface, owner)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _state_color_dog(state: str):
    return {
        "IDLE": cfg.GREEN,
        "PATROLLING": (150, 220, 150),
        "HERDING": cfg.YELLOW,
        "CHASING_WOLF": cfg.RED,
        "RETURNING": cfg.BLUE,
        "RESTING": cfg.GRAY,
        "EXHAUSTED": cfg.DARK_GRAY,
    }.get(state, cfg.WHITE)


def _state_color_wolf(state: str):
    return {
        "PATROL": cfg.GRAY,
        "STALK": cfg.ORANGE,
        "CHARGE": cfg.RED,
        "FLEE": cfg.BLUE,
        "RESTING": cfg.DARK_GRAY,
    }.get(state, cfg.WHITE)


def _draw_stamina_bar(surface, dog):
    from ..core import settings as cfg
    x, y = int(dog.pos.x), int(dog.pos.y)
    bar_w = 22
    bar_h = 3
    bx = x - bar_w // 2
    by = y - dog.radius - 9
    pct = dog.stamina / cfg.DOG_MAX_STAMINA
    pygame.draw.rect(surface, cfg.DARK_GRAY, (bx, by, bar_w, bar_h))
    color = cfg.GREEN if pct > 0.4 else cfg.YELLOW if pct > 0.15 else cfg.RED
    pygame.draw.rect(surface, color, (bx, by, int(bar_w * pct), bar_h))


def _draw_emotion_tag(surface, agent):
    """A small colored dot above the agent indicating dominant emotion."""
    if agent.emotion.fear > 40:
        color = cfg.BLUE
    elif agent.emotion.anger > 40:
        color = cfg.RED
    elif agent.emotion.happiness > 70:
        color = cfg.GREEN
    else:
        return
    x = int(agent.pos.x)
    y = int(agent.pos.y - agent.radius - 14)
    pygame.draw.circle(surface, color, (x, y), 3)


def _draw_speech(surface, agent):
    if agent.speech is None:
        return
    # import here to avoid circular imports
    from . import ui_theme as ui
    text = ui.render_text(agent.speech, 11, ui.TEXT_PRIMARY, "bold")
    tw, th = text.get_size()
    pad_x = 8
    pad_y = 4
    w = tw + pad_x * 2
    h = th + pad_y * 2
    x = int(agent.pos.x - w // 2)
    y = int(agent.pos.y - agent.radius - h - 18)

    # bubble body with shadow
    panel = pygame.Surface((w + 4, h + 6), pygame.SRCALPHA)
    pygame.draw.rect(
        panel, (0, 0, 0, 100),
        pygame.Rect(2, 3, w, h), border_radius=8,
    )
    pygame.draw.rect(
        panel, (*ui.BG_ELEVATED, 240),
        pygame.Rect(0, 0, w, h), border_radius=8,
    )
    pygame.draw.rect(
        panel, ui.BORDER_STRONG,
        pygame.Rect(0, 0, w, h), 1, border_radius=8,
    )
    panel.blit(text, (pad_x, pad_y))

    # little triangle tail pointing down at the agent
    tail_x_center = w // 2
    tail_points = [
        (tail_x_center - 4, h - 1),
        (tail_x_center + 4, h - 1),
        (tail_x_center, h + 5),
    ]
    pygame.draw.polygon(panel, ui.BG_ELEVATED, tail_points)

    surface.blit(panel, (x, y))