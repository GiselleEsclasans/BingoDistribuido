# Server/chat_server.py
import socket
import threading
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.clientes = []
        self.nicknames = {}
        
    def broadcast(self, mensaje, cliente_emisor=None):
        """Envía mensaje a todos los clientes conectados"""
        for cliente in self.clientes:
            if cliente != cliente_emisor:
                try:
                    cliente.send(mensaje.encode('utf-8'))
                except:
                    self.remover_cliente(cliente)
    
    def manejar_cliente(self, cliente):
        """Maneja la comunicación con un cliente específico"""
        while True:
            try:
                mensaje = cliente.recv(1024).decode('utf-8')
                if mensaje:
                    # Formato: "nickname: mensaje"
                    self.broadcast(mensaje, cliente)
                else:
                    break
            except:
                break
        self.remover_cliente(cliente)
    
    def remover_cliente(self, cliente):
        if cliente in self.clientes:
            nickname = self.nicknames.get(cliente, "Unknown")
            self.clientes.remove(cliente)
            if cliente in self.nicknames:
                del self.nicknames[cliente]
            cliente.close()
            self.broadcast(f"--- {nickname} abandonó el chat ---")
    
    def iniciar(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"🔄 Servidor de Chat escuchando en {self.host}:{self.port}")
        
        while True:
            cliente, direccion = self.server.accept()
            print(f"✅ Nueva conexión desde {direccion}")
            
            # Solicitar nickname
            cliente.send("NICK".encode('utf-8'))
            nickname = cliente.recv(1024).decode('utf-8')
            
            self.nicknames[cliente] = nickname
            self.clientes.append(cliente)
            
            # Notificar a todos
            mensaje_bienvenida = f"🎉 {nickname} se ha unido al chat!"
            self.broadcast(mensaje_bienvenida)
            print(f"👤 {nickname} conectado. Clientes: {len(self.clientes)}")
            
            # Iniciar hilo para el cliente
            hilo = threading.Thread(target=self.manejar_cliente, args=(cliente,))
            hilo.daemon = True
            hilo.start()

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.iniciar()