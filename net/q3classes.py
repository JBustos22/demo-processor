import numpy as np
from net import defs
class GameState():
    def __init__(self,):
        return

class Snapshot():
    def __init__(self, server_time=None, delta_num=None, sequence=None, player_state=None, entity_state=None):
        self.servertime = server_time
        self.delta_num = delta_num
        self.sequence = sequence
        self.playerstate = player_state
        self.entitystate = entity_state
        self.previous_snapshot = None
        self.next_snapshot = None

    def get_ps_val(self, key):
        return self.playerstate.get(key, None)

    def get_es_val(self, key):
        return self.entitystate.get(key, None)

    def get_stat(self, num):
        return self.playerstate.get('stats', {}).get(num, None)

    def is_dj_time(self):
        return

    def is_jump(self):
        try:
            return self.get_ps_val('pm_time') > self.previous_snapshot.get_ps_val('pm_time')
        except (AttributeError, TypeError):
            return False

    def get_view_angles(self, rad=False):
        scalar = np.pi/180 if rad else 1
        pitch = self.playerstate.get('viewangles[0]', 0)
        yaw = self.playerstate.get('viewangles[1]', 0)
        roll = self.playerstate.get('viewangles[2]', 0)
        return list(map(lambda angle: angle * scalar, [pitch, yaw, roll]))

    def get_wishdir_xy(self):
        pitch, yaw, roll = self.get_view_angles(rad=True)
        forward = [np.cos(pitch) * np.cos(yaw),
                   np.cos(pitch) * np.sin(yaw)]
        right = [-np.sin(roll)*np.sin(pitch)*np.cos(yaw) + np.cos(roll)*np.sin(yaw),
                 -np.sin(roll)*np.sin(pitch)*np.sin(yaw) - np.cos(roll)*np.cos(yaw)]

        presses = self.get_presses()
        if 'F' in presses:
            fwd_press = 127.0
        elif 'B' in presses:
            fwd_press = -127.0
        else:
            fwd_press = 0.0

        if 'R' in presses:
            side_press = 127.0
        elif 'L' in presses:
            side_press = -127.0
        else:
            side_press = 0.0


        wish_vel = np.array([0.0, 0.0])
        for i in range(0, 2):
            wish_vel[i] = forward[i] * fwd_press + right[i] * side_press

        if np.linalg.norm(wish_vel):
            wish_dir = wish_vel / np.linalg.norm(wish_vel)
        else:
            wish_dir = np.array([0, 0])

        return wish_dir

    def get_vel(self):
        vx = self.playerstate.get('velocity[0]', 0)
        vy = self.playerstate.get('velocity[1]', 0)
        return [vx, vy]

    def in_cgaz_zone(self):
        wish_dir = self.get_wishdir_xy()
        if not np.linalg.norm(wish_dir):
            return False

        vel = np.array(self.get_vel())
        dot_prod = np.dot(vel, wish_dir)
        return 0 < 320 - dot_prod <= 320


    def get_speed(self):
        v_x = self.playerstate.get('velocity[0]', 0)
        v_y = self.playerstate.get('velocity[1]', 0)
        speed = round(np.sqrt(v_x**2 + v_y**2))
        return speed

    def get_time(self):
        try:
            timer = self.playerstate['time']
        except KeyError:
            timer = 0
        return timer

    def get_presses(self):
        press = self.playerstate.get('stats', {}).get('13', 0)
        presses = ""
        for symbol, press_num in defs.PRESS_NUMS.items():
            if press >= press_num:
                presses += symbol
                press -= press_num
            if press == 0:
                break
        return presses

    def has_pm_flag(self, flag):
        return

    def get_pmflags(self):
        return
    def get_health(self):
        return
    def get_weapon(self):
        return
    def get_pos(self):
        return
    def is_checkpoint(self):
        return

class ServerCommand():
    def __init__(self, command):
        self.command_type = None