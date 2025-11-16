import pygame

class View:
    def __init__(self, manager):
        self.manager = manager
    def handle_event(self, event):
        pass
    def update(self, dt):
        pass
    def render(self, surface):
        pass

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.views = {}
        self.current = None

    def register(self, name, view_cls):
        self.views[name] = view_cls(self)

    def set_view(self, name):
        if name in self.views:
            self.current = self.views[name]

    def get_view(self, name):
        """Obtiene una instancia de vista por su nombre."""
        return self.views.get(name)

    def handle_event(self, event):
        if self.current:
            self.current.handle_event(event)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def render(self):
        if self.current:
            self.current.render(self.screen)