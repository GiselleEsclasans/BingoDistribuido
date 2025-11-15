import pygame
from UI_manager import View


class UI_Video(View):
    def __init__(self, manager):
        super().__init__(manager)
       
        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        
        try:
            if not pygame.font.get_init():
                pygame.font.init()
        except Exception:
            pass

        try:
            self.title_font = pygame.font.SysFont('Extenda', 48)
            self.content_font = pygame.font.SysFont('Extenda', 24)
            self.button_font = pygame.font.SysFont('Extenda', 26)
        except Exception:
            try:
                self.title_font = pygame.font.SysFont(None, 48)
                self.content_font = pygame.font.SysFont(None, 24)
                self.button_font = pygame.font.SysFont(None, 26)
            except Exception:
                class DummyFont:
                    def __init__(self, size=24):
                        self.size = size
                    def render(self, text, aa, color):
                        try:
                            return pygame.Surface((1,1))
                        except Exception:
                            return None
                self.title_font = DummyFont(48)
                self.content_font = DummyFont(24)
                self.button_font = DummyFont(26)

        self.emoji_font = None
        try:
            emoji_candidates = ['Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', 'Apple Color Emoji']
            for name in emoji_candidates:
                try:
                    f = pygame.font.SysFont(name, 24)
                    self.emoji_font = f
                    break
                except Exception:
                    continue
        except Exception:
            self.emoji_font = None

        self.movie = None
        self.video_playing = False
        self.movie_size = (500, 250)
        self.load_video()

    def _render_text(self, text, primary_font, color):
        """Renderizar texto eligiendo una fuente con soporte emoji si es necesario.

        Si el texto contiene caracteres fuera del ASCII básico, intentamos usar
        `self.emoji_font` (si existe). Si falla, volvemos a la fuente primaria.
        """
        try:
            has_nonascii = any(ord(ch) > 127 for ch in text)
            if has_nonascii and getattr(self, 'emoji_font', None):
                try:
                    surf = self.emoji_font.render(text, True, color)
                    if surf and getattr(surf, 'get_width', lambda: 0)() > 0:
                        return surf
                except Exception:
                    pass
            try:
                return primary_font.render(text, True, color)
            except Exception:
                return pygame.Surface((1, 1))
        except Exception:
            return pygame.Surface((1, 1))

        

    def load_video(self):
        """Cargar el video desde el archivo"""
        import os

        try:
            Movie = getattr(pygame, 'movie', None)
            video_path = 'Bingo.mpg'
            abs_path = os.path.abspath(video_path)
            if not os.path.exists(abs_path):
                self.movie = None
                self.clip = None
                return

            if Movie and hasattr(Movie, 'Movie'):
                try:
                    self.movie = Movie.Movie(abs_path)
                    try:
                        self.movie.set_display(pygame.Rect(150, 150, self.movie_size[0], self.movie_size[1]))
                    except Exception:
                        pass
                    
                except Exception as e:
                 
                    self.movie = None
            else:
                
                try:
                    try:
                        from moviepy import VideoFileClip
                    except Exception:
                        from moviepy.editor import VideoFileClip

                    try:
                        self.clip = VideoFileClip(abs_path)
                        self.movie = 'moviepy'
                        self.clip_time = 0.0
                     
                    except Exception as e:
                       
                        self.clip = None
                        self.movie = None
                except Exception as e:
            
                    self.clip = None
                    self.movie = None
        except pygame.error as e:
    
            self.movie = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
          
            back_rect = pygame.Rect(20, 20, 120, 40)
            if back_rect.collidepoint(mx, my):
                self.stop_video()
                self.manager.set_view('bienvenida')
            
            video_rect = pygame.Rect(150, 150, 500, 250)
            if video_rect.collidepoint(mx, my) and self.movie:
                if self.video_playing:
                    self.pause_video()
                else:
                    self.play_video()

    def play_video(self):
        """Reproducir el video"""
        if self.movie and not self.video_playing:
            if self.movie != 'moviepy':
                try:
                    play_fn = getattr(self.movie, 'play', None)
                    if callable(play_fn):
                        play_fn()
                        self.video_playing = True
                      
                    else:
                        print('Reproducción no soportada por el backend de video.')
                except Exception as e:
                    print(f'Error al reproducir el video: {e}')
            else:
                self.video_playing = True

    def stop_video(self):
        """Detener el video"""
        if self.movie and self.video_playing:
            if self.movie != 'moviepy':
                try:
                    stop_fn = getattr(self.movie, 'stop', None)
                    if callable(stop_fn):
                        stop_fn()
                    self.video_playing = False
                   
                except Exception as e:
                    print(f'Error al detener el video: {e}')
            else:
                self.video_playing = False
                try:
                    self.clip_time = 0.0
                except Exception:
                    pass
             
    def pause_video(self):
        """Pausar el video"""
        if self.movie and self.video_playing:
            if self.movie != 'moviepy':
                try:
                    pause_fn = getattr(self.movie, 'pause', None)
                    if callable(pause_fn):
                        pause_fn()
                    self.video_playing = False
                   
                except Exception as e:
                    print(f'Error al pausar el video: {e}')
            else:
                self.video_playing = False
         

    def render(self, surface):
        surface.fill(self.RED)

        back_rect = pygame.Rect(20, 20, 100, 48)
        try:
            pygame.draw.rect(surface, self.WHITE, back_rect, border_radius=12)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, back_rect)
        back_text = self.button_font.render('Volver', True, self.YELLOW)
        back_x = back_rect.x + (back_rect.w - back_text.get_width()) // 2
        back_y = back_rect.y + (back_rect.h - back_text.get_height()) // 2
        surface.blit(back_text, (back_x, back_y))

        title = self.title_font.render('Video Promocional', True, self.RED)
        padding = 24
        box_inner_width = max(self.movie_size[0], title.get_width())
        box_width = box_inner_width + padding * 2
        box_height = padding * 2 + title.get_height() + 12 + self.movie_size[1]
        box_x = (800 - box_width) // 2
        box_y = 80

        try:
            shadow = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            surface.blit(shadow, (box_x + 8, box_y + 8))
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), (box_x + 6, box_y + 6, box_width, box_height))

        try:
            pygame.draw.rect(surface, self.WHITE, pygame.Rect(box_x, box_y, box_width, box_height), border_radius=14)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, (box_x, box_y, box_width, box_height))

        title_x = box_x + (box_width - title.get_width()) // 2
        title_y = box_y + padding
        surface.blit(title, (title_x, title_y))

        video_x = box_x + (box_width - self.movie_size[0]) // 2
        video_y = title_y + title.get_height() + 12
        video_rect = pygame.Rect(video_x, video_y, self.movie_size[0], self.movie_size[1])
        video_corner_radius = 18
        try:
            pygame.draw.rect(surface, (0, 0, 0), video_rect, border_radius=video_corner_radius)
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), video_rect)

        if self.movie == 'moviepy' and getattr(self, 'clip', None):
            try:
                frame = self.clip.get_frame(self.clip_time)
                try:
                    import numpy as _np
                except Exception:
                    return
                if _np.issubdtype(frame.dtype, _np.floating):
                    frame = (frame * 255).astype('uint8')
                if frame.shape[2] == 4:
                    frame = frame[..., :3]
                elif frame.shape[2] != 3:
                    if frame.shape[2] > 3:
                        frame = frame[..., :3]
                    else:
                        frame = _np.repeat(frame[..., :1], 3, axis=2)
                frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB')
                if (frame_surface.get_width(), frame_surface.get_height()) != self.movie_size:
                    frame_surface = pygame.transform.smoothscale(frame_surface, self.movie_size)
                surface.blit(frame_surface, (video_rect.x, video_rect.y))
                if not self.video_playing:
                    dark_overlay = pygame.Surface(self.movie_size, pygame.SRCALPHA)
                    dark_overlay.fill((0, 0, 0, 128))
                    surface.blit(dark_overlay, (video_rect.x, video_rect.y))
            except Exception as e:
                print(f'Error al renderizar frame con moviepy: {e}')

        if not self.movie:
            error_text = self._render_text('❌ Error al cargar el video', self.content_font, self.RED if False else self.WHITE)
            surface.blit(error_text, (video_rect.x + (video_rect.w - error_text.get_width()) // 2,
                                   video_rect.y + (video_rect.h - error_text.get_height()) // 2))
        elif not self.video_playing:
            play_text = self._render_text('🎬 Haz clic para reproducir', self.content_font, self.WHITE)
            surface.blit(play_text, (video_rect.x + (video_rect.w - play_text.get_width()) // 2,
                                   video_rect.y + (video_rect.h - play_text.get_height()) // 2))

    def update(self, dt):
        """Actualizar el estado del video

        dt: seconds elapsed since last update (no usado actualmente)
        """
        if self.movie and self.video_playing:
            try:
                if self.movie == 'moviepy' and getattr(self, 'clip', None):
                    try:
                        self.clip_time += dt
                        if self.clip_time >= self.clip.duration:
                            self.clip_time = 0.0
                            self.video_playing = False
                    except Exception as e:
                        print(f'Error al avanzar tiempo del clip: {e}')
                else:
                    busy_fn = getattr(self.movie, 'get_busy', None)
                    if callable(busy_fn):
                        if not busy_fn():
                            self.video_playing = False
                            rewind_fn = getattr(self.movie, 'rewind', None)
                            if callable(rewind_fn):
                                rewind_fn()
            except Exception as e:
                print(f'Error al verificar estado del video: {e}')
