import socket
import json
import threading
import time

class GameClient:
    def __init__(self, server_host='127.0.0.1', server_port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.server_addr = (server_host, server_port)
        
        self.player_id = None
        self.other_players = {}  # {id: {'x', 'y', 'angle', 'vx', 'vy', 'crashes'}}
        self.connected = False
        self.track_name = None
        
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
    
    def connect(self, spawn_x, spawn_y, spawn_angle):
        """Send join request to server"""
        join_msg = {
            'type': 'join',
            'x': spawn_x,
            'y': spawn_y,
            'angle': spawn_angle
        }
        self.sock.sendto(json.dumps(join_msg).encode('utf-8'), self.server_addr)
        
        # Wait for welcome message (with timeout)
        start_time = time.time()
        while not self.connected and time.time() - start_time < 3.0:
            time.sleep(0.1)
        
        return self.connected
    
    def send_update(self, x, y, angle, vx, vy, crashes):
        """Send player position update to server"""
        if not self.connected:
            return
        
        update_msg = {
            'type': 'update',
            'x': x,
            'y': y,
            'angle': angle,
            'vx': vx,
            'vy': vy,
            'crashes': crashes
        }
        try:
            self.sock.sendto(json.dumps(update_msg).encode('utf-8'), self.server_addr)
        except Exception as e:
            print(f"Send error: {e}")
    
    def disconnect(self):
        """Notify server of disconnect"""
        leave_msg = {'type': 'leave'}
        try:
            self.sock.sendto(json.dumps(leave_msg).encode('utf-8'), self.server_addr)
        except:
            pass
        self.running = False
        self.sock.close()
    
    def _receive_loop(self):
        """Background thread to receive server messages"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = json.loads(data.decode('utf-8'))
                msg_type = msg.get('type')
                
                if msg_type == 'welcome':
                    # Server acknowledged connection
                    self.player_id = msg.get('id')
                    self.track_name = msg.get('track', 'track1.json')
                    self.connected = True
                    print(f"Connected to server! Player ID: {self.player_id}")
                    print(f"Track: {self.track_name}")
                
                elif msg_type == 'state':
                    # Update other players' positions
                    players = msg.get('players', [])
                    self.other_players.clear()
                    for p in players:
                        if p['id'] != self.player_id:
                            self.other_players[p['id']] = {
                                'x': p['x'],
                                'y': p['y'],
                                'angle': p['angle'],
                                'vx': p.get('vx', 0),
                                'vy': p.get('vy', 0),
                                'crashes': p.get('crashes', 0)
                            }
            
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
    
    def get_other_players(self):
        """Get dictionary of other players' states"""
        return self.other_players.copy()
    
    def is_connected(self):
        return self.connected