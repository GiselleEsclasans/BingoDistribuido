import pygame
from UI_manager import View
import urllib.request
import urllib.error
import json

class UI_Login(View):
    def __init__(self, manager):
        super().__init__(manager)

        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        
        try:
            self.title_font = pygame.font.SysFont('Extenda', 48, bold=True)
            self.label_font = pygame.font.SysFont('Extenda', 24)
            self.input_font = pygame.font.SysFont('Extenda', 22)
            self.button_font = pygame.font.SysFont('Extenda', 30, bold=True)
            self.error_font = pygame.font.SysFont('Extenda', 20, bold=True)
        except:
            self.title_font = pygame.font.SysFont(None, 48, bold=True)
            self.label_font = pygame.font.SysFont(None, 24)
            self.input_font = pygame.font.SysFont(None, 22)
            self.button_font = pygame.font.SysFont(None, 30, bold=True)
            self.error_font = pygame.font.SysFont(None, 20, bold=True)

        self.username = ""
        self.password = ""
        self.active_input = "username" 
        self.login_error = None
        
        self.input_width = 300
        self.input_height = 40
        self.center_x = self.manager.screen.get_width() // 2
        
        self.user_rect = pygame.Rect(self.center_x - self.input_width // 2, 150, self.input_width, self.input_height)
        self.pass_rect = pygame.Rect(self.center_x - self.input_width // 2, 250, self.input_width, self.input_height)
        
        self.login_rect = pygame.Rect(self.center_x - 100, 330, 200, 50)

    def attempt_login(self):
        """Intenta hacer login contra la API de FastAPI"""
        self.login_error = None
        
        if not self.username or not self.password:
            self.login_error = "Usuario y contraseña no pueden estar vacíos"
            return
            
        try:
            data = json.dumps({
                "username": self.username,
                "password": self.password
            }).encode('utf-8')
            
            req = urllib.request.Request(
                "http://localhost:8000/login", 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get("status") == "success":
                    self.manager.nickname = result.get("username")
                    self.manager.set_view("bienvenida")
                else:
                    self.login_error = result.get("message", "Error desconocido")

        except urllib.error.HTTPError as e:
            try:
                error_json = json.loads(e.read().decode('utf-8'))
                self.login_error = error_json.get("detail", "Error del servidor")
            except:
                self.login_error = "Error del servidor"
        except urllib.error.URLError as e:
            self.login_error = "Error de conexión: ¿La API está encendida?"
        except Exception as e:
            self.login_error = "Error inesperado."

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.user_rect.collidepoint(event.pos):
                self.active_input = "username"
            elif self.pass_rect.collidepoint(event.pos):
                self.active_input = "password"
            elif self.login_rect.collidepoint(event.pos):
                self.attempt_login() 
            else:
                self.active_input = None

        if event.type == pygame.KEYDOWN:
            self.login_error = None
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.active_input == "username":
                    self.active_input = "password"
                elif self.active_input == "password":
                    self.attempt_login()
            elif event.key == pygame.K_TAB:
                self.active_input = "password" if self.active_input == "username" else "username"
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == "username":
                    self.username = self.username[:-1]
                elif self.active_input == "password":
                    self.password = self.password[:-1]
            else:
                if self.active_input == "username" and len(self.username) < 20:
                    self.username += event.unicode
                elif self.active_input == "password" and len(self.password) < 20:
                    self.password += event.unicode

    def render(self, surface):
        surface.fill(self.WHITE)

        title_surf = self.title_font.render("INICIAR SESIÓN", True, self.RED)
        title_rect = title_surf.get_rect(center=(self.center_x, 70))
        surface.blit(title_surf, title_rect)

        user_label = self.label_font.render("Usuario:", True, self.BLACK)
        surface.blit(user_label, (self.user_rect.x, self.user_rect.y - 30))

        pass_label = self.label_font.render("Contraseña:", True, self.BLACK)
        surface.blit(pass_label, (self.pass_rect.x, self.pass_rect.y - 30))

        color_user = self.YELLOW if self.active_input == "username" else self.WHITE
        pygame.draw.rect(surface, color_user, self.user_rect, border_radius=5)
        pygame.draw.rect(surface, self.RED, self.user_rect, 2, border_radius=5)
        user_text = self.input_font.render(self.username, True, self.BLACK)
        surface.blit(user_text, (self.user_rect.x + 10, self.user_rect.y + 10))

        color_pass = self.YELLOW if self.active_input == "password" else self.WHITE
        pygame.draw.rect(surface, color_pass, self.pass_rect, border_radius=5)
        pygame.draw.rect(surface, self.RED, self.pass_rect, 2, border_radius=5)
        pass_text = self.input_font.render("*" * len(self.password), True, self.BLACK)
        surface.blit(pass_text, (self.pass_rect.x + 10, self.pass_rect.y + 10))
        
        pygame.draw.rect(surface, self.RED, self.login_rect, border_radius=10)
        login_text = self.button_font.render("Entrar", True, self.WHITE)
        login_text_rect = login_text.get_rect(center=self.login_rect.center)
        surface.blit(login_text, login_text_rect)
        
        if self.login_error:
            error_surf = self.error_font.render(self.login_error, True, self.RED)
            error_rect = error_surf.get_rect(center=(self.center_x, 400))
            surface.blit(error_surf, error_rect)