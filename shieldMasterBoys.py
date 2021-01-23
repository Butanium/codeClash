import sys
import math
from math import cos, sin, pi, acos, tan
from typing import List

import numpy as np


class PodInfo:
    def __init__(self, infos):
        x, y, vx, vy, a, next_ch_id = infos
        self.pos = np.array([x, y])
        self.speed = np.array([vx, vy])
        self.angle = a
        # debug("ANGLE : " + str(a))
        self.next_checkpoint_id = next_ch_id
        self.next_check_pos = checkpoints[self.next_checkpoint_id]
        self.next_check_dist = dist(self.pos, self.next_check_pos)


class EnemyInfo:
    def __init__(self, index):
        self.index = index
        self.prev_check = 0
        self.lap = 1

    def update(self, infos):
        if infos.next_checkpoint_id != self.prev_check:
            if not self.prev_check:
                self.lap += 1
            self.prev_check = infos.next_checkpoint_id


class PodController:
    def __init__(self, index):
        self.index = index
        self.init = False
        self.locked_target = False
        self.boost = 1
        self.previous_check = 1
        self.previous_check_aim = 0
        self.angle_diff = 0
        self.lap = 1
        self.angle_diff = 0
        self.ally_angle_diff = 180
        self.ally = None

    def get_output(self, infos: PodInfo):
        self.ally = ally_pod_info[1 - self.index]
        if self.index:
            return self.runner(infos)
        else:
            return self.fighter(infos)

    def runner(self, infos: PodInfo):

        if infos.next_checkpoint_id != self.previous_check and not self.previous_check:
            self.lap += 1
        if self.init and (infos.speed[0] or infos.speed[1]):
            # debug(str(infos.speed) + "m.s  " + str(infos.pos) + " pos  " + str(infos.next_check_pos) + " check pos")
            self.angle_diff = angle_btw(infos.speed, infos.pos, infos.next_check_pos)
            # debug("speed : " + str(infos.speed))
            # debug("rotation_difference : " + str(angle_btw(infos.speed, infos.pos, infos.next_check_pos)))
        # debug(infos.angle)
        # debug(rotate(np.array([0,0]), np.array([1,0]), infos.angle*pi/180))
        angle = angle_btw(rotate(np.array([0, 0]), np.array([1, 0]), infos.angle * pi / 180), infos.pos,
                          infos.next_check_pos)
        output_speed = 100
        output_speed = speed(angle)
        # debug("speed : " + str(speed(angle)) + "  angle : " + str(angle))
        """toggle direction"""
        sensitivity = .01
        if self.init and angle < 20 and (infos.speed[0] or infos.speed[1]):
            # debug("angle diff : " + str(self.angle_diff))
            rot1 = rotate(infos.pos, infos.next_check_pos, self.angle_diff * sensitivity).astype(int)
            rot2 = rotate(infos.pos, infos.next_check_pos, -1 * self.angle_diff * sensitivity).astype(int)
            # debug(str(infos.next_check_pos)+"/"+str(len(rot1)))
            if angle_btw(infos.speed, infos.pos, rot1) > angle_btw(infos.speed, infos.pos, rot2):
                to_reach_x, to_reach_y = rot1
            else:
                to_reach_x, to_reach_y = rot2
        else:
            to_reach_x = infos.next_check_pos[0]
            to_reach_y = infos.next_check_pos[1]

        speed_magnitude = magnitude(infos.speed)
        # debug("norme vitesse : " + str(speed_magnitude))
        ratio = 5
        debug("shift : " + str(tan(self.angle_diff * pi / 180) * infos.next_check_dist))
        if infos.next_check_dist < ratio * speed_magnitude and self.init and abs(
                tan(self.angle_diff * pi / 180) * infos.next_check_dist) < 500:
            debug("turn en avance!!")
            to_reach_x = checkpoints[(infos.next_checkpoint_id + 1) % checkpoint_count][0]
            to_reach_y = checkpoints[(infos.next_checkpoint_id + 1) % checkpoint_count][1]
        if self.angle_diff < 8 and self.boost and self.lap == 3 and infos.next_checkpoint_id == 0:
            output_speed = "BOOST"
            self.boost = 0
            debug("BOOOOOOST")
        for e in enemy_pod_info:
            if collide(infos.pos, infos.speed, e.pos, e.speed):
                output_speed = "SHIELD"

        if collide(infos.pos, infos.speed, self.ally.pos, self.ally.speed):
            output_speed = "SHIELD"
        self.init = True
        return str(to_reach_x) + " " + str(to_reach_y) + " " + str(output_speed)

    """second mode"""

    def fighter(self, infos: PodInfo):
        sensitivity = .01

        tot0 = enemies_infos[0].index + enemies_infos[0].lap * checkpoint_count
        tot1 = enemies_infos[1].index + enemies_infos[1].lap * checkpoint_count

        if tot0 > tot1:
            self.locked_target = enemy_pod_info[0]
        elif tot0 < tot1:
            self.locked_target = enemy_pod_info[1]
        if self.locked_target:
            if self.locked_target.next_check_dist < dist(infos.pos, self.locked_target.next_check_pos):
                target = checkpoints[(self.locked_target.next_checkpoint_id + 1) % checkpoint_count]
            else:
                target = ((self.locked_target.next_check_pos + self.locked_target.pos) / 2).astype(int)
                # todo better targeting if enemy is close
        else:
            target = infos.next_check_pos
        if magnitude(infos.speed):
            self.angle_diff = angle_btw(infos.speed, infos.pos, target)

        angle = angle_btw(rotate(np.array([0, 0]), np.array([1, 0]), infos.angle * pi / 180), infos.pos,
                          target)
        if angle < 20 and magnitude(infos.speed):
            rot1 = rotate(infos.pos, target, self.angle_diff * sensitivity).astype(int)
            rot2 = rotate(infos.pos, target, -1 * self.angle_diff * sensitivity).astype(int)
            if angle_btw(infos.speed, infos.pos, rot1) > angle_btw(infos.speed, infos.pos, rot2):
                to_reach_x, to_reach_y = rot1
            else:
                to_reach_x, to_reach_y = rot2
        else:
            to_reach_x = target[0]
            to_reach_y = target[1]
        output_speed = speed(angle)
        for e in enemy_pod_info:
            # debug("distance: " + str(dist(e.pos, infos.pos)))
            if collide(infos.pos, infos.speed, e.pos, e.speed):
                output_speed = "SHIELD"

        return str(to_reach_x) + " " + str(to_reach_y) + " " + str(output_speed)


def magnitude(vector: np.array):
    return dist(0, 0, vector[0], vector[1])


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
def rotate(center: np.array, point: np.array, a):
    rot_matrix = np.array([[cos(a), -sin(a)], [sin(a), cos(a)]])
    return rot_matrix.dot(point - center) + center


def dist(x1, y1, x2=0, y2=0):
    try:
        _ = iter(x1)
    except TypeError:
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5
    else:
        return ((x1[0] - y1[0]) ** 2 + (x1[1] - y1[1]) ** 2) ** .5


def debug(message):
    print(message, file=sys.stderr, flush=True)


def angle_btw(orientation: np.array, pos1: np.array, pos2: np.array):
    return int(acos(cos_btw(orientation, pos1, pos2)) * 180 / pi)


def cos_btw(orientation: np.array, pos1: np.array, pos2: np.array):
    return scalar(orientation, pos2 - pos1) / (magnitude(orientation) * magnitude(pos2 - pos1))


def scalar(u: np.array, v: np.array):
    return sum(u * v)


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


def collide(pos1, v1, pos2, v2):
    newpos1 = pos1 + v1
    newpos2 = pos2 + v2
    return dist(newpos1, newpos2) < 800



allies_controllers = [PodController(0), PodController(1)]
enemies_infos = [EnemyInfo(0), EnemyInfo(1)]
ally_laps = [1, 1]
enemy_laps = [1, 1]
# output_speeds = [100, 100]
checkpoints = []
lap_count = int(input())
checkpoint_count = int(input())
for i in range(checkpoint_count):
    checkpoints.append(np.array([int(j) for j in input().split()]))

# game loop


delta_t = .75

while True:
    ally_pod_info = []
    enemy_pod_info: List[PodInfo] = []
    for i in range(2):
        # x: x position of your pod
        # y: y position of your pod
        # vx: x speed of your pod
        # vy: y speed of your pod
        # angle: angle of your pod
        # next_check_point_id: next check point id of your pod
        inf = PodInfo([int(j) for j in input().split()])
        ally_pod_info.append(inf)
        if inf.next_checkpoint_id == 1 and ally_laps[i] > 1:
            ally_laps[i] += 1

    for i in range(2):
        # x_2: x position of the opponent's pod
        # y_2: y position of the opponent's pod
        # vx_2: x speed of the opponent's pod
        # vy_2: y speed of the opponent's pod
        # angle_2: angle of the opponent's pod
        # next_check_point_id_2: next check point id of the opponent's pod
        enemy_pod_info.append(PodInfo([int(j) for j in input().split()]))
        enemies_infos[i].update(enemy_pod_info[i])

    s = allies_controllers[0].get_output(ally_pod_info[0])

    print(s)
    print(allies_controllers[1].get_output(ally_pod_info[1]))
