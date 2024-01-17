from core.demos import DemoParser
import numpy as np
FRAME_TIME = 8


def get_jumps_speed(demo):
    print("### Jump speed ###")
    for snapshot in demo.get_jump_snapshots(timed=True):
        print(f"Jump at {snapshot.get_time()} with speed {snapshot.get_speed()}")
    print("\n################\n")


def get_switch_times(demo):
    print("\n### Switch times ###\n")
    switch_times = []
    right_strafing, left_strafing = False, False
    switch_end_time, switch_start_time = None, None
    last_cgaz_servertime = 0
    prev_wdx, prev_wdy = 0, 0
    for snapshot in demo.get_timed_snapshots():
        if snapshot.in_cgaz_zone():
            curr_wdx, curr_wdy = snapshot.get_wishdir_xy()
            if prev_wdx * curr_wdx < 0 or prev_wdy * curr_wdy < 0:
                # switch has occurred and completed, accelerating the other way now.
                switch_time = snapshot.servertime - last_cgaz_servertime
                switch_times += [switch_time]
                print(f"Switch detected. Time {switch_time}ms or {int(switch_time / FRAME_TIME)} frames")
            else:
                last_cgaz_servertime = snapshot.servertime
            prev_wdx, prev_wdy = curr_wdx, curr_wdy

    avg_switch_time = np.mean(switch_times)
    min_switch_time = np.min(switch_times)
    max_switch_time = np.max(switch_times)

    print(f"\naverage: {round(avg_switch_time, 2)}ms or {round(avg_switch_time/FRAME_TIME, 2)} frames")
    print(f"minimum switch time: {min_switch_time}ms or {int(min_switch_time/FRAME_TIME)} frames")
    print(f"maximum switch time: {max_switch_time}ms or {int(max_switch_time/FRAME_TIME)} frames")
    print(f"total switches: {len(switch_times)}")
    print("\n################\n")
    return


def get_jump_times(demo):
    print("\n### Jump times ###\n")
    jump_times = []
    for jump_snapshot in demo.get_jump_snapshots(timed=True):
        # go backwards and check for Js
        prev_test_snapshot = demo.get_prev_snapshot(jump_snapshot)
        while 'J' in prev_test_snapshot.get_presses() and not prev_test_snapshot.is_jump():
            prev_test_snapshot = demo.get_prev_snapshot(prev_test_snapshot)
            if prev_test_snapshot is None:
                break

        # go forwards and check for Js
        next_test_snapshot = demo.get_next_snapshot(jump_snapshot)
        while 'J' in next_test_snapshot.get_presses() and not next_test_snapshot.is_jump():
            next_test_snapshot = demo.get_next_snapshot(next_test_snapshot)
            if next_test_snapshot is None:
                break

        if prev_test_snapshot is None or next_test_snapshot is None:
            print(f"Unable to find jump timing at t={jump_snapshot.get_time()} due to incomplete information\n")
            continue

        earliest_snapshot = demo.get_next_snapshot(prev_test_snapshot)
        latest_snapshot = demo.get_prev_snapshot(next_test_snapshot)

        jump_time = latest_snapshot.servertime - earliest_snapshot.servertime
        if jump_time < FRAME_TIME:
            jump_time = FRAME_TIME
        print(f"Jump at {jump_snapshot.get_time()} jump time: {jump_time} ms or {int(jump_time/FRAME_TIME)} frames")
        jump_times += [jump_time]
    avg_jump_time = np.mean(jump_times)
    min_jump_time = np.min(jump_times)
    max_jump_time = np.max(jump_times)

    print(f"\naverage: {round(avg_jump_time, 2)}ms or {round(avg_jump_time/FRAME_TIME, 2)} frames")
    print(f"minimum jump time: {min_jump_time}ms or {int(min_jump_time/FRAME_TIME)} frames")
    print(f"maximum jump time: {max_jump_time}ms or {int(max_jump_time/FRAME_TIME)} frames")
    print(f"total jumps: {len(jump_times)}")
    print("\n################\n")
    return


def get_avg_jump_accel(demo):
    prev_snapshot = None
    for snapshot in demo.get_jump_snapshots(timed=True):
        if prev_snapshot is not None:
            dv = snapshot.get_speed() - prev_snapshot.get_speed()
            dt = (snapshot.servertime - prev_snapshot.servertime) / FRAME_TIME
            print(f"Jump at {snapshot.get_time()} with average accel {round(dv/dt,2)} ups/frame")
        prev_snapshot = snapshot

filepath = "./files/palmslane[mdf.vq3]00.06.512(bunnybunbob.Germany).dm_68"
demoparser = DemoParser(filepath)
demo = demoparser.parse()
get_switch_times(demo)
get_jumps_speed(demo)
get_jump_times(demo)

