import pygame
from UI_manager import View

class UI_Bienvenida(View):
    def __init__(self, manager):
        super().__init__(manager)

        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)

        try:
            self.title_font = pygame.font.SysFont('Extenda', 48)
            self.title_bold_font = pygame.font.SysFont('Extenda', 48, bold=True)
            self.subtitle_font = pygame.font.SysFont('Extenda', 24)
            self.button_font = pygame.font.SysFont('Extenda', 30)
            self.button_bold_font = pygame.font.SysFont('Extenda', 30, bold=True)
            self.error_font = pygame.font.SysFont('Extenda', 22, bold=True)
        except Exception:
            self.title_font = pygame.font.SysFont(None, 48)
            self.title_bold_font = pygame.font.SysFont(None, 48, bold=True)
            self.subtitle_font = pygame.font.SysFont(None, 24)
            self.button_font = pygame.font.SysFont(None, 30)
            self.button_bold_font = pygame.font.SysFont(None, 30, bold=True)
            self.error_font = pygame.font.SysFont(None, 24, bold=True)

        self.buttons = [
            ('📖', 'Instrucciones', 'instrucciones'),
            ('⚙️', 'Configuraciones', 'config'), 
            ('🎬', 'Video', 'video'),
            ('🎮', 'Juego', 'juego'),
        ]

        self.emoji_font = None
        for fname in ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji']:
            try:
                f = pygame.font.SysFont(fname, 36)
                test = f.render('🎮', True, self.RED)
                if test.get_width() > 0:
                    self.emoji_font = f
                    break
            except Exception:
                continue

        self.use_graphic_fallback = self.emoji_font is None
        
        self.error_message = None

    def darken_color(self, color, amount=0.2):
        """Return a darker version of color (tuple) by amount (0..1)."""
        return tuple(max(0, int(c * (1 - amount))) for c in color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            w = 300
            h = 70  
            spacing = 16
            total_h = len(self.buttons) * h + (len(self.buttons)-1) * spacing
            start_x = (800 - w) // 2
            start_y = (460 - total_h) // 2 + 40
            
            self.error_message = None 
            
            for i, (emoji, label, target) in enumerate(self.buttons):
                rect = pygame.Rect(start_x, start_y + i*(h+spacing), w, h)
                
                if rect.collidepoint(mx, my):
                    
                    if rect.collidepoint(mx, my):
                        if target == 'juego':
                            try:
                                game_view = self.manager.get_view('juego')
                                
                                settings = getattr(self.manager, 'game_settings', {
                                    'numero_jugadores': 4,
                                    'modo': 'regular'
                                })
                                jugadores_sel = settings['numero_jugadores']
                                modo_sel = settings['modo']
                                
                                nickname = getattr(self.manager, 'nickname', 'Jugador')

                                exito = game_view.inicializar_juego(
                                    nickname=nickname,
                                    jugadores=jugadores_sel,
                                    modo_juego=modo_sel
                                )
                                
                                if exito:
                                    self.manager.set_view(target)
                                else:
                                    self.error_message = "Error: No se pudo conectar al servidor."
                                    print(f"[BIENVENIDA] Falla al conectar: {nickname}, {jugadores_sel}, {modo_sel}")
                            
                            except Exception as e:
                                self.error_message = f"Error: {e}"
                                print(f"[BIENVENIDA] Excepción: {e}")
                        
                        else:
                            self.manager.set_view(target)
                        return

    def render(self, surface):
        surface.fill(self.WHITE)

        title_text = '¡Bingo Distribuido!'
        t_surf_red = self.title_bold_font.render(title_text, True, self.RED)
        t_surf_yellow = self.title_bold_font.render(title_text, True, self.YELLOW)
        tx = (surface.get_width() - t_surf_yellow.get_width()) // 2
        ty = 60
        outline_radius = 4 
        for ox in range(-outline_radius, outline_radius+1):
            for oy in range(-outline_radius, outline_radius+1):
                if ox == 0 and oy == 0:
                    continue
                surface.blit(t_surf_red, (tx+ox, ty+oy))
        surface.blit(t_surf_yellow, (tx, ty))

        subtitle = 'Selecciona una opción'
        sub_surf = self.subtitle_font.render(subtitle, True, self.YELLOW)
        sx = (surface.get_width() - sub_surf.get_width()) // 2
        surface.blit(sub_surf, (sx, 120))

        w = 300
        h = 70
        spacing = 16
        radius = 12
        total_h = len(self.buttons) * h + (len(self.buttons)-1) * spacing
        start_x = (surface.get_width() - w) // 2
        start_y = (surface.get_height() - total_h) // 2 + 40
        mx, my = pygame.mouse.get_pos()
        
        for i, (emoji, label, _) in enumerate(self.buttons):
            rect = pygame.Rect(start_x, start_y + i*(h+spacing), w, h)
            hover = rect.collidepoint(mx, my)
            base_color = self.RED if (i % 2) == 0 else self.YELLOW
            btn_color = tuple(min(255, c + 30) for c in base_color) if hover else base_color

            for s in range(6, 0, -1):
                alpha = int(80 * (s / 6))
                shadow_surf = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
                shadow_color = (0, 0, 0, alpha)
                pygame.draw.rect(shadow_surf, shadow_color, pygame.Rect(4, 4, rect.w, rect.h), border_radius=radius)
                surface.blit(shadow_surf, (rect.x + s, rect.y + s))

            pygame.draw.rect(surface, btn_color, rect, border_radius=radius)

            emoji_space = 80 
            if not self.use_graphic_fallback:
                emoji_surf = self.emoji_font.render(emoji, True, self.RED)
                emoji_x = rect.x + 20
                emoji_y = rect.y + (rect.h - emoji_surf.get_height()) // 2
                surface.blit(emoji_surf, (emoji_x, emoji_y))
            else:
                icon_center = (rect.x + 30, rect.y + rect.h // 2)
                pygame.draw.circle(surface, self.RED, icon_center, 16)
                pygame.draw.circle(surface, (0,0,0), icon_center, 16, 2)

            outline_color = self.darken_color(base_color, amount=0.25)
            txt_font = self.button_bold_font
            txt_main = txt_font.render(label, True, self.WHITE)
            txt_outline = txt_font.render(label, True, outline_color)
            txt_x = rect.x + emoji_space
            txt_y = rect.y + (rect.h - txt_main.get_height()) // 2
            outline_radius = 2
            for ox in range(-outline_radius, outline_radius+1):
                for oy in range(-outline_radius, outline_radius+1):
                    if ox == 0 and oy == 0:
                        continue
                    surface.blit(txt_outline, (txt_x+ox, txt_y+oy))
            surface.blit(txt_main, (txt_x, txt_y))

        if self.error_message:
            error_surf = self.error_font.render(self.error_message, True, self.RED)
            err_x = (surface.get_width() - error_surf.get_width()) // 2
            err_y = 520

            err_bg_rect = error_surf.get_rect(center=(err_x + error_surf.get_width() // 2, err_y + error_surf.get_height() // 2))
            err_bg_rect.inflate_ip(20, 10) 
            
            bg_surf = pygame.Surface(err_bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((255, 255, 255, 180)) 
            
            surface.blit(bg_surf, err_bg_rect.topleft)
            surface.blit(error_surf, error_surf.get_rect(center=err_bg_rect.center))