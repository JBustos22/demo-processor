# Copied and reduced directly from jfedor's quake 3 proxy https://github.com/jfedor2/quake3-proxy-aimbot
import collections

GENTITYNUM_BITS = 10
FLOAT_INT_BITS = 13
FLOAT_INT_BIAS = 1 << (FLOAT_INT_BITS - 1)
MAX_GENTITIES = 1 << GENTITYNUM_BITS
MAX_PACKETLEN = 1400
FRAGMENT_SIZE = MAX_PACKETLEN - 100
FRAGMENT_BIT = 1 << 31
MAX_RELIABLE_COMMANDS = 64
PACKET_BACKUP = 32
PACKET_MASK = PACKET_BACKUP - 1
MSG_SEQUENCE_LEN = 4
MSG_LENGTH_LEN = 4
BLOCK_HEADER_BYTES = MSG_SEQUENCE_LEN + MSG_LENGTH_LEN
MSG_TYPES = {
    0: 'bad',
    1: 'nop',
    2: 'gamestate',
    3: 'cofigstring',
    4: 'baseline',
    5: 'servercommand',
    6: 'download',
    7: 'snapshot',
    8: 'eof'
}

PRESS_NUMS = {
    "_": 512,
    "*": 256,
    "C": 64,
    "J": 32,
    "R": 16,
    "L": 8,
    "B": 2,
    "F": 1,
    " ": 0
}

FieldDefinition = collections.namedtuple("FieldDefinition", ["name", "bits"])

PLAYERSTATE_FIELDS = [
    FieldDefinition("commandTime", 32),
    FieldDefinition("origin[0]", 0),
    FieldDefinition("origin[1]", 0),
    FieldDefinition("bobCycle", 8),
    FieldDefinition("velocity[0]", 0),
    FieldDefinition("velocity[1]", 0),
    FieldDefinition("viewangles[1]", 0),
    FieldDefinition("viewangles[0]", 0),
    FieldDefinition("weaponTime", -16),
    FieldDefinition("origin[2]", 0),
    FieldDefinition("velocity[2]", 0),
    FieldDefinition("legsTimer", 8),
    FieldDefinition("pm_time", -16),
    FieldDefinition("eventSequence", 16),
    FieldDefinition("torsoAnim", 8),
    FieldDefinition("movementDir", 4),
    FieldDefinition("events[0]", 8),
    FieldDefinition("legsAnim", 8),
    FieldDefinition("events[1]", 8),
    FieldDefinition("pm_flags", 16),
    FieldDefinition("groundEntityNum", GENTITYNUM_BITS),
    FieldDefinition("weaponstate", 4),
    FieldDefinition("eFlags", 16),
    FieldDefinition("externalEvent", 10),
    FieldDefinition("gravity", 16),
    FieldDefinition("speed", 16),
    FieldDefinition("delta_angles[1]", 16),
    FieldDefinition("externalEventParm", 8),
    FieldDefinition("viewheight", -8),
    FieldDefinition("damageEvent", 8),
    FieldDefinition("damageYaw", 8),
    FieldDefinition("damagePitch", 8),
    FieldDefinition("damageCount", 8),
    FieldDefinition("generic1", 8),
    FieldDefinition("pm_type", 8),
    FieldDefinition("delta_angles[0]", 16),
    FieldDefinition("delta_angles[2]", 16),
    FieldDefinition("torsoTimer", 12),
    FieldDefinition("eventParms[0]", 8),
    FieldDefinition("eventParms[1]", 8),
    FieldDefinition("clientNum", 8),
    FieldDefinition("weapon", 5),
    FieldDefinition("viewangles[2]", 0),
    FieldDefinition("grapplePoint[0]", 0),
    FieldDefinition("grapplePoint[1]", 0),
    FieldDefinition("grapplePoint[2]", 0),
    FieldDefinition("jumppad_ent", 10),
    FieldDefinition("loopSound", 16),
]

ENTITY_FIELDS = [
    FieldDefinition("pos.trTime", 32),
    FieldDefinition("pos.trBase[0]", 0),
    FieldDefinition("pos.trBase[1]", 0),
    FieldDefinition("pos.trDelta[0]", 0),
    FieldDefinition("pos.trDelta[1]", 0),
    FieldDefinition("pos.trBase[2]", 0),
    FieldDefinition("apos.trBase[1]", 0),
    FieldDefinition("pos.trDelta[2]", 0),
    FieldDefinition("apos.trBase[0]", 0),
    FieldDefinition("event", 10),
    FieldDefinition("angles2[1]", 0),
    FieldDefinition("eType", 8),
    FieldDefinition("torsoAnim", 8),
    FieldDefinition("eventParm", 8),
    FieldDefinition("legsAnim", 8),
    FieldDefinition("groundEntityNum", GENTITYNUM_BITS),
    FieldDefinition("pos.trType", 8),
    FieldDefinition("eFlags", 19),
    FieldDefinition("otherEntityNum", GENTITYNUM_BITS),
    FieldDefinition("weapon", 8),
    FieldDefinition("clientNum", 8),
    FieldDefinition("angles[1]", 0),
    FieldDefinition("pos.trDuration", 32),
    FieldDefinition("apos.trType", 8),
    FieldDefinition("origin[0]", 0),
    FieldDefinition("origin[1]", 0),
    FieldDefinition("origin[2]", 0),
    FieldDefinition("solid", 24),
    FieldDefinition("powerups", 16),
    FieldDefinition("modelindex", 8),
    FieldDefinition("otherEntityNum2", GENTITYNUM_BITS),
    FieldDefinition("loopSound", 8),
    FieldDefinition("generic1", 8),
    FieldDefinition("origin2[2]", 0),
    FieldDefinition("origin2[0]", 0),
    FieldDefinition("origin2[1]", 0),
    FieldDefinition("modelindex2", 8),
    FieldDefinition("angles[0]", 0),
    FieldDefinition("time", 32),
    FieldDefinition("apos.trTime", 32),
    FieldDefinition("apos.trDuration", 32),
    FieldDefinition("apos.trBase[2]", 0),
    FieldDefinition("apos.trDelta[0]", 0),
    FieldDefinition("apos.trDelta[1]", 0),
    FieldDefinition("apos.trDelta[2]", 0),
    FieldDefinition("time2", 32),
    FieldDefinition("angles[2]", 0),
    FieldDefinition("angles2[0]", 0),
    FieldDefinition("angles2[2]", 0),
    FieldDefinition("constantLight", 32),
    FieldDefinition("frame", 16),
]
