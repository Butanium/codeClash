import sys
import math
from math import cos, sin, pi, acos
import numpy as np


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
def rotate(center: np.array, point: np.array, a):
    rot_matrix = np.array([[cos(a), -sin(a)], [sin(a), cos(a)]])
    return rot_matrix.dot(point - center) + center


def dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5


def debug(message):
    print(message, file=sys.stderr, flush=True)


def angle_btw(orientation: np.array, pos1: np.array, pos2: np.array):
    return int(acos(sum(orientation * (pos2 - pos1)) / (
            sum(orientation ** 2) ** .5 * sum((pos2 - pos1) ** 2) ** .5)) * 180 / pi)


def speed(agl, mode=2, smooth=.05):
    if mode == 1:
        return 100 - int(agl // 1.8)
    elif mode == 2:
        return int((.5 - 1 / (1 + math.exp(-(agl - 90)) * smooth)) * 100 + 50)
    elif mode == 3:
        if agl > 90:
            return speed(agl, 2, .07)
        else:
            return speed(agl, 1)


lap = 1
checkpoint_index = 0
checkpoint_count = 0
checkpoints = []
locked_target = False
previous_check_aim = 0
# game loop
boost = 1
previous_check = 0
init = False
en_pos = np.array([0, 0])
pod_pos = np.array([0, 0])
prev_en_pos = np.array([0, 0])
prev_pod_pos = np.array([0, 0])
pod_speed = np.array([0, 0])
enemy_speed = np.array([0, 0])
delta_t = .75
angle_diff = 0
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = \
        [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]
    prev_pod_pos = pod_pos
    prev_en_pos = en_pos
    next_check_pos = np.array([next_checkpoint_x, next_checkpoint_y])
    pod_pos = np.array([x, y])
    en_pos = np.array([opponent_x, opponent_y])

    if init:
        pod_speed = ((pod_pos - prev_pod_pos) / delta_t).astype(int)
        enemy_speed = ((en_pos - prev_en_pos) / delta_t).astype(int)
        angle_diff = angle_btw(pod_speed, pod_pos, next_check_pos)
        debug("speed : " + str(pod_speed))
        debug("rotation_difference : " + str(angle_btw(pod_speed, pod_pos, next_check_pos)))
        debug("input rotation" + str(next_checkpoint_angle))

    chp = np.array([next_checkpoint_x, next_checkpoint_y])
    if not np.array_equal(previous_check, chp):
        previous_check = chp
        checkpoint_index += 1

        if checkpoint_index == 1 and lap > 1:
            lap += 1
        if not any((chp == x).all() for x in checkpoints):
            checkpoints.append(chp.copy())
            checkpoint_count += 1
        elif lap == 1:
            lap += 1
        if lap > 1:
            checkpoint_index %= (checkpoint_count)

    debug("checkpoint index : " + str(checkpoint_index))
    debug("lap : " + str(lap))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    angle = abs(next_checkpoint_angle)
    s = speed(angle)

    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    """toggle direction"""
    sensitivity = .01
    if init and angle < 20:
        debug("angle diff : " + str(angle_diff))
        rot1 = rotate(pod_pos, chp, angle_diff*sensitivity).astype(int)
        rot2 = rotate(pod_pos, chp, -1*angle_diff*sensitivity).astype(int)
        # debug(str(chp)+"/"+str(len(rot1)))
        if angle_btw(pod_speed, pod_pos, rot1) > angle_btw(pod_speed, pod_pos, rot2):
            to_reach_x, to_reach_y = rot1
        else:
            to_reach_x, to_reach_y = rot2
    else:
        to_reach_x = next_checkpoint_x
        to_reach_y = next_checkpoint_y


    op_check_dist = dist(opponent_x, opponent_y, next_checkpoint_x, next_checkpoint_y)
    if 0 < op_check_dist - next_checkpoint_dist < 2000 and s == 100 \
            and not (lap == 3 and (checkpoint_count - checkpoint_index < 3 or checkpoint_index == 0)):
        debug("WE ARE SLOWUNG DOWN")
        s = 50
    if op_check_dist < min(next_checkpoint_dist, 2000):
        if not locked_target and dist(opponent_x, opponent_y, x, y) < 1000 and next_checkpoint_x != previous_check_aim:
            locked_target = True
            debug("TARGET LOCKED")
    if locked_target:
        to_reach_x = opponent_x
        to_reach_y = opponent_y
        s = 100
        debug(dist(opponent_x, opponent_y, x, y))
    if dist(opponent_x, opponent_y, x, y) < 1000 and locked_target:
        locked_target = False
        previous_check_aim = next_checkpoint_x
        debug("_______________TARGET UNLOCKED__________________")
    if angle_diff < 8 and boost and lap == 3 and checkpoint_index == 0:
        s = "BOOST"
        boost = 0
        debug("BOOOOOOST")
    init = True
    print(str(to_reach_x) + " " + str(to_reach_y) + " " + str(s))

