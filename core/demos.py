from net import defs, q3classes
from net.buffers import Buffer
import collections
import numpy as np


DemoMessage = collections.namedtuple("DemoMessage",["sequence", "length", "type", "message"])


class Demo():
    def __init__(self, filepath, gamestate, snapshots, servercommands):
        self.filepath = filepath
        self.snapshots = snapshots
        self.servercommands = servercommands
        self.gamestate = gamestate
        self.data = None
        self.length = None
        self.player = None
        self.map_name = None
        self.physics = None

        first_sequence = next(iter(self.snapshots))
        self.snaps = int(1000/(self.snapshots[first_sequence+1].servertime - self.snapshots[first_sequence].servertime))
        print(f"Demo snaps {self.snaps} detected")

    def get_snapshots(self):
        if not bool(self.snapshots):
            self.snapshots = self.parse_snapshots()
        return self.snapshots

    def get_jump_snapshots(self, timed=False):
        jump_snapshots = []
        for snapshot in self.snapshots.values():
            if snapshot.is_jump():
                if timed and not snapshot.get_time():
                    continue
                jump_snapshots += [snapshot]
        return jump_snapshots

    def get_timed_snapshots(self):
        timed_snapshots = []
        for snapshot in self.snapshots.values():
                if not snapshot.get_time():
                    continue
                timed_snapshots += [snapshot]
        return timed_snapshots

    def get_prev_snapshot(self, snapshot, delta=1):
        try:
            return self.snapshots[snapshot.sequence-delta]
        except KeyError:
            return None

    def get_next_snapshot(self, snapshot, delta=1):
        try:
            return self.snapshots[snapshot.sequence+delta]
        except KeyError:
            return None

    def get_checkpoints(self):
        return
    def get_physics(self):
        return

    def get_players(self):
        return

    def get_gamestate(self):
        return

    def get_server_commands(self):
        return

    def get_chat(self):
        return

    def get_console(self):
        return

    def get_scores(self):
        return

    def parse_gamestate(self):
        return

    def parse_snapshots(self):
        return


class DemoParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.baselines = {}
        self.snapshots = {}
        self.curr_index = 0
        self.last_snapshot = None

    def parse_snapshot(self, sequence, buffer):
        server_time = buffer.read_bits(32, "server_time")
        delta_num = buffer.read_bits(8, "delta_num")
        snapshot = q3classes.Snapshot(sequence=sequence, server_time=server_time, delta_num=delta_num)
        snapshot_to_delta_from = (None if delta_num == 0 else
                                  self.snapshots[(sequence - delta_num) & defs.PACKET_MASK])

        if snapshot_to_delta_from and snapshot_to_delta_from.sequence != sequence - delta_num:
            snapshot_to_delta_from = None

        snapshot.snap_flags = buffer.read_bits(8, "snap_flags")
        areamask_length = buffer.read_bits(8, "areamask_length")
        snapshot.areamask = buffer.read_bits(areamask_length * 8, "areamask")
        snapshot.playerstate = self.parse_playerstate(buffer, snapshot_to_delta_from)
        snapshot.entities = self.parse_entities(buffer, snapshot_to_delta_from)
        self.snapshots[sequence & defs.PACKET_MASK] = snapshot
        snapshot.previous_snapshot = self.last_snapshot
        if self.last_snapshot is not None:
            self.last_snapshot.next_snapshot = snapshot
        self.last_snapshot = snapshot
        return snapshot

    def parse_playerstate(self, buffer, snapshot_to_delta_from):
        if snapshot_to_delta_from is not None:
            playerstate = snapshot_to_delta_from.playerstate.copy()
        else:
            playerstate = {}
        field_count = buffer.read_bits(8, "field_count")
        for i in range(field_count):
            if buffer.read_bit("field_changed"):
                field = defs.PLAYERSTATE_FIELDS[i]
                if field.bits == 0:  # float
                    if buffer.read_bit("int_or_float") == 0:
                        playerstate[field.name] = buffer.read_int_float(field.name)
                    else:
                        playerstate[field.name] = buffer.read_float(field.name)
                else:
                    playerstate[field.name] = buffer.read_bits(field.bits, field.name)
        if buffer.read_bit("arrays_changed"):
            if buffer.read_bit("stats_changed"):
                stats = playerstate.get('stats', {}).copy()
                bits = buffer.read_bits(16, "stats_bits")
                time = 0
                for i in range(16):
                    if bits & (1 << i):
                        if i == 8:
                            time = buffer.read_bits(16, "stats_bit_{}".format(i))
                        else:
                            stats[str(i)] = buffer.read_bits(16, "stats_bit_{}".format(i))
                playerstate['stats'] = stats
                playerstate['time'] = time
                # pm_flags = format(playerstate['pm_flags'], '013b')
                # print(f'stats at time {time}: presses: {PRESSES}, speed:{speed} pm_flags: {pm_flags}')
            if buffer.read_bit("persistent_changed"):
                bits = buffer.read_bits(16, "persistent_bits")
                persistent_bits = {}
                index = 9
                changed = False
                for i in range(16):
                    if bits & (1 << i):
                        if i == index:
                            changed = True
                        persistent_bits[str(i)] = buffer.read_bits(16, "persistent_bit_{}".format(i))
                playerstate['persistent_bits'] = persistent_bits
            if buffer.read_bit("ammo_changed"):
                ammo = {}
                bits = buffer.read_bits(16, "ammo_bits")
                for i in range(16):
                    if bits & (1 << i):
                        ammo[str(i)] = buffer.read_bits(16, "ammo_bit_{}".format(i))
                playerstate['ammo'] = ammo
            if buffer.read_bit("powerups_changed"):
                powerups = {}
                bits = buffer.read_bits(16, "powerups_bits")
                for i in range(16):
                    if bits & (1 << i):
                        powerups[str(i)] = buffer.read_bits(32, "powerups_bit_{}".format(i))
                playerstate['powerups'] = powerups
        return playerstate

    def parse_entities(self, buffer, snapshot_to_delta_from):
        if snapshot_to_delta_from is not None:
            entities = snapshot_to_delta_from.entities.copy()
        else:
            entities = {}
        while True:
            entity_number = buffer.read_bits(defs.GENTITYNUM_BITS, "entity_number")
            if entity_number == defs.MAX_GENTITIES - 1:
                break
            elif buffer.read_bit("update_or_delete") == 1:
                if entity_number in entities:
                    del entities[entity_number]
            else:
                if entity_number in entities:
                    old = entities[entity_number]
                else:
                    if entity_number in self.baselines:
                        old = self.baselines[entity_number]
                    else:
                        old = {}
                entities[entity_number] = self.read_delta_entity(buffer, old)
        return entities

    def parse_gamestate(self, buffer):
        server_command_sequence = buffer.read_bits(32)
        gamestate = {
            "client_number": "",
            "configs": {},
            "baseline": []
        }
        while True:
            gamestate_op = buffer.read_bits(8)
            if gamestate_op == 8:  # svc_EOF
                break
            elif gamestate_op == 3:  # svc_configstring
                config_index = buffer.read_bits(16, "configstring_index")
                config_string = buffer.read_string("configstring")
                # self.parse_configstring(config_string)
                gamestate['configs'][config_index] = config_string
            elif gamestate_op == 4:  # svc_baseline
                entity_number = buffer.read_bits(defs.GENTITYNUM_BITS, "entity_number")
                if buffer.read_bit("update_or_delete") == 0:
                    gamestate['baseline'] += [{'entity_number': entity_number, 'state':  self.read_delta_entity(buffer, {})}]
            else:
                raise Exception("unknown command in gamestate: {}".format(gamestate_op))
        gamestate["client_number"] = buffer.read_bits(32, "client_number")
        self.checksum_feed = buffer.read_bits(32, "checksum_feed")
        return gamestate

    def read_delta_entity(self, buffer, old):
        entity = old.copy()
        if buffer.read_bit("entity_changed") == 1:
            field_count = buffer.read_bits(8, "field_count")
            for i in range(field_count):
                if buffer.read_bit("field_changed") == 1:
                    field = defs.ENTITY_FIELDS[i]
                    if field.bits == 0:  # float
                        if buffer.read_bit("float_is_not_zero") == 1:
                            if buffer.read_bit("int_or_float") == 0:
                                entity[field.name] = buffer.read_int_float(field.name)
                            else:
                                entity[field.name] = buffer.read_float(field.name)
                        else:
                            entity[field.name] = 0
                    else:
                        if buffer.read_bit("int_is_not_zero") == 1:
                            entity[field.name] = buffer.read_bits(field.bits, field.name)
                        else:
                            entity[field.name] = 0

        return entity

    def parse_server_command(self, buffer):
        commands = []
        command_sequence = buffer.read_bits(32, "command_sequence")
        commands += [buffer.read_string("command")]
        return commands

    def parse_compressed_msg(self, sequence, msg_type, buffer):
        if msg_type == 'gamestate':
            return self.parse_gamestate(buffer)
        elif msg_type == 'snapshot':
            return self.parse_snapshot(sequence, buffer)
        elif msg_type == 'servercommand':
            return self.parse_server_command(buffer)
        else:
            # core should only contain gamestates, snapshots, and server commands at the block level
            raise('Unexpected message type')

    def get_messages(self):
        while True:
            sequence = int.from_bytes(self.file.read(defs.MSG_SEQUENCE_LEN), 'little')
            msg_length = int.from_bytes(self.file.read(defs.MSG_LENGTH_LEN), 'little')
            if sequence in [0, 4294967295] and msg_length in [0, 4294967295]:
                return None
            buffer = Buffer(self.file.read(msg_length))
            buffer.read_bits(32)
            msg_op_num = buffer.read_bits(8)
            msg_type = defs.MSG_TYPES[msg_op_num]
            yield DemoMessage(sequence, msg_length, msg_type, self.parse_compressed_msg(sequence, msg_type, buffer))

    def parse(self):
        self.file = open(self.filepath, 'rb')
        gamestate, snapshots, servercommands = None, {}, []
        for demo_message in self.get_messages():
            if demo_message is None:
                break
            if demo_message.type == 'gamestate':
                gamestate = demo_message.message
            elif demo_message.type == 'snapshot':
                snapshots[demo_message.sequence] = demo_message.message
            else:
                servercommands += [demo_message.message]
        self.file.close()
        return Demo(self.filepath, gamestate, snapshots, servercommands)
