import pygame
from UI_manager import View


class UI_Instrucciones(View):
    def __init__(self, manager):
        super().__init__(manager)
   
        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        
        try:
            self.title_font = pygame.font.SysFont('Extenda', 48)
            self.content_font = pygame.font.SysFont('Extenda', 24)
            self.button_font = pygame.font.SysFont('Extenda', 26)
        except Exception:
            self.title_font = pygame.font.SysFont(None, 48)
            self.content_font = pygame.font.SysFont(None, 24)
            self.button_font = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            back_rect = pygame.Rect(20, 20, 100, 48)
            if back_rect.collidepoint(mx, my):
                self.manager.set_view('bienvenida')

    def render(self, surface):
        surface.fill(self.RED)

        #BOTÓN REGRESAR ------------------------------------------
        back_rect = pygame.Rect(20, 20, 100, 48)
        try:
            pygame.draw.rect(surface, self.WHITE, back_rect, border_radius=12)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, back_rect)
        back_text = self.button_font.render('Volver', True, self.YELLOW)
        back_x = back_rect.x + (back_rect.w - back_text.get_width()) // 2
        back_y = back_rect.y + (back_rect.h - back_text.get_height()) // 2
        surface.blit(back_text, (back_x, back_y))

        lines = [
            '1. Cada jugador recibe un cartón de bingo',
            '2. El sistema genera números de forma aleatoria',
            '3. Marca los números que coincidan en tu cartón',
            '4. El primer jugador en completar un patrón gana',
            '5. Patrones depende del modo que eligas, puede ser línea o cartón lleno',
            '',
            '¡Diviértete!'
        ]
        
        padding = 20
        max_line_width = 0
        text_surfs = []
        for idx, line in enumerate(lines):
            color = self.RED if idx == len(lines) - 1 else self.YELLOW
            ts = self.content_font.render(line, True, color)
            text_surfs.append(ts)
            max_line_width = max(max_line_width, ts.get_width())
        title_surf = self.title_font.render('Instrucciones del Bingo', True, self.RED)
        box_inner_width = max(max_line_width, title_surf.get_width())
        extra_right = 40
        inner_width = box_inner_width
        box_width = inner_width + padding * 2 + extra_right

        title_h = title_surf.get_height()
        line_height = text_surfs[0].get_height() if text_surfs else 24
        box_height = padding * 2 + title_h + 12 + (line_height * len(text_surfs)) + (len(text_surfs)-1) * 8

        box_x = (800 - box_width) // 2
        box_y = 140

        try:
            shadow = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            surface.blit(shadow, (box_x + 8, box_y + 8))
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), (box_x + 6, box_y + 6, box_width, box_height))

        try:
            pygame.draw.rect(surface, self.WHITE, pygame.Rect(box_x, box_y, box_width, box_height), border_radius=12)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, (box_x, box_y, box_width, box_height))

        title_x = box_x + (box_width - title_surf.get_width()) // 2
        title_y = box_y + padding
        surface.blit(title_surf, (title_x, title_y))

        ty = title_y + title_h + 12
        content_left = box_x + padding + 8
        for i, ts in enumerate(text_surfs):
            if i < len(text_surfs) - 1:
                surface.blit(ts, (content_left, ty))
            else:
                surface.blit(ts, (box_x + (box_width - ts.get_width()) // 2, ty))
            ty += ts.get_height() + 8
