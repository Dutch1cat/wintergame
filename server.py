import socket
import json
import time
import threading
from collections import defaultdict

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.settimeout(0.1)
        
        # Player data: {addr: {'id', 'x', 'y', 'angle', 'vx', 'vy', 'crashes', 'last_update'}}
        self.players = {}
        self.next_id = 0
        self.running = True
        
        # Track selection
        self.current_track = "track1.json"
        
        print(f"Server started on {host}:{port}")
        print(f"Current track: {self.current_track}")
    
    def handle_message(self, data, addr):
        try:
            msg = json.loads(data.decode('utf-8'))
            msg_type = msg.get('type')
            
            if msg_type == 'join':
                # New player joining
                if addr not in self.players:
                    player_id = self.next_id
                    self.next_id += 1
                    self.players[addr] = {
                        'id': player_id,
                        'x': msg.get('x', 100),
                        'y': msg.get('y', 100),
                        'angle': msg.get('angle', 0),
                        'vx': 0,
                        'vy': 0,
                        'crashes': 0,
                        'last_update': time.time()
                    }
                    print(f"Player {player_id} joined from {addr}")
                    
                    # Send welcome message with player ID and track
                    response = {
                        'type': 'welcome',
                        'id': player_id,
                        'track': self.current_track
                    }
                    self.sock.sendto(json.dumps(response).encode('utf-8'), addr)
            
            elif msg_type == 'update':
                # Player position update
                if addr in self.players:
                    self.players[addr].update({
                        'x': msg.get('x'),
                        'y': msg.get('y'),
                        'angle': msg.get('angle'),
                        'vx': msg.get('vx', 0),
                        'vy': msg.get('vy', 0),
                        'crashes': msg.get('crashes', 0),
                        'last_update': time.time()
                    })
            
            elif msg_type == 'leave':
                # Player leaving
                if addr in self.players:
                    player_id = self.players[addr]['id']
                    del self.players[addr]
                    print(f"Player {player_id} left")
        
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def broadcast_game_state(self):
        # Remove stale players (no update in 5 seconds)
        current_time = time.time()
        stale_addrs = [addr for addr, p in self.players.items() 
                       if current_time - p['last_update'] > 5.0]
        for addr in stale_addrs:
            print(f"Removing stale player {self.players[addr]['id']}")
            del self.players[addr]
        
        if not self.players:
            return
        
        # Prepare game state
        game_state = {
            'type': 'state',
            'players': [
                {
                    'id': p['id'],
                    'x': p['x'],
                    'y': p['y'],
                    'angle': p['angle'],
                    'vx': p['vx'],
                    'vy': p['vy'],
                    'crashes': p['crashes']
                }
                for p in self.players.values()
            ]
        }
        
        # Send to all players
        state_data = json.dumps(game_state).encode('utf-8')
        for addr in self.players.keys():
            try:
                self.sock.sendto(state_data, addr)
            except Exception as e:
                print(f"Error sending to {addr}: {e}")
    
    def run(self):
        last_broadcast = time.time()
        broadcast_rate = 1/30  # 30 updates per second
        
        while self.running:
            # Receive messages
            try:
                data, addr = self.sock.recvfrom(4096)
                self.handle_message(data, addr)
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Receive error: {e}")
            
            # Broadcast game state at fixed rate
            current_time = time.time()
            if current_time - last_broadcast >= broadcast_rate:
                self.broadcast_game_state()
                last_broadcast = current_time
            
            time.sleep(0.001)  # Small sleep to prevent CPU spinning
    
    def stop(self):
        self.running = False
        self.sock.close()
        print("Server stopped")

if __name__ == "__main__":
    server = GameServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()