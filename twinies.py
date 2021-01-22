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

    def get_output(self, infos: PodInfo):

        if self.index:
            return self.runner(infos)
        else:
            return self.idle_fighter(infos)

    def runner(self, infos: PodInfo):
        ally = ally_pod_info[1 - self.index]
        next_check_pos = checkpoints[infos.next_checkpoint_id]
        next_check_dist = dist(infos.pos, next_check_pos)
        if infos.next_checkpoint_id != self.previous_check and not self.previous_check:
            self.lap += 1
        if self.init and (infos.speed[0] or infos.speed[1]):
            # debug(str(infos.speed) + "m.s  " + str(infos.pos) + " pos  " + str(next_check_pos) + " check pos")
            self.angle_diff = angle_btw(infos.speed, infos.pos, next_check_pos)
            # debug("speed : " + str(infos.speed))
            # debug("rotation_difference : " + str(angle_btw(infos.speed, infos.pos, next_check_pos)))
        # debug(infos.angle)
        # debug(rotate(np.array([0,0]), np.array([1,0]), infos.angle*pi/180))
        angle = angle_btw(rotate(np.array([0, 0]), np.array([1, 0]), infos.angle * pi / 180), infos.pos, next_check_pos)
        output_speed = 100
        output_speed = speed(angle)
        # debug("speed : " + str(speed(angle)) + "  angle : " + str(angle))
        """toggle direction"""
        sensitivity = .01
        if self.init and angle < 20 and (infos.speed[0] or infos.speed[1]):
            # debug("angle diff : " + str(self.angle_diff))
            rot1 = rotate(infos.pos, next_check_pos, self.angle_diff * sensitivity).astype(int)
            rot2 = rotate(infos.pos, next_check_pos, -1 * self.angle_diff * sensitivity).astype(int)
            # debug(str(next_check_pos)+"/"+str(len(rot1)))
            if angle_btw(infos.speed, infos.pos, rot1) > angle_btw(infos.speed, infos.pos, rot2):
                to_reach_x, to_reach_y = rot1
            else:
                to_reach_x, to_reach_y = rot2
        else:
            to_reach_x = next_check_pos[0]
            to_reach_y = next_check_pos[1]

        speed_magnitude = magnitude(infos.speed)
        debug("norme vitesse : " + str(speed_magnitude))
        ratio = 5
        debug("shift : " + str(tan(self.angle_diff) * next_check_dist))
        if next_check_dist < ratio * speed_magnitude and self.init and abs(
                tan(self.angle_diff) * next_check_dist) < 500:
            debug("turn en avance!!")
            to_reach_x = checkpoints[(infos.next_checkpoint_id + 1) % checkpoint_count][0]
            to_reach_y = checkpoints[(infos.next_checkpoint_id + 1) % checkpoint_count][1]
        op_check_dist = []
        # for j in range(2):
        #     if enemy_pod_info[j].next_checkpoint_id == infos.next_checkpoint_id:
        #         op_check_dist.append(dist(enemy_pod_info[j].pos, next_check_pos))
        #
        # for op_dist in op_check_dist:
        #     if 0 < op_dist - next_check_dist < 2000 and output_speed == 100 \
        #             and not (self.lap == lap_count and
        #                      (checkpoint_count - infos.next_checkpoint_id < 3 or infos.next_checkpoint_id == 0)):
        #         debug("WE ARE SLOWING DOWN")
        #         output_speed = 50
        #
        # if op_check_dist < min(next_check_dist, 2000):
        #     if not self.locked_target and dist(opponent_x, opponent_y, x,
        #                                        y) < 1000 and next_checkpoint_x != self.previous_check_aim:
        #         self.locked_target = True
        #         debug("TARGET LOCKED")
        # if self.locked_target:
        #     to_reach_x = opponent_x
        #     to_reach_y = opponent_y
        #     s = 100
        #     debug(dist(opponent_x, opponent_y, x, y))
        # if dist(opponent_x, opponent_y, x, y) < 1000 and self.locked_target:
        #     locked_target = False
        #     self.previous_check_aim = next_check_pos[0]
        #     debug("_______________TARGET UNLOCKED__________________")
        if self.angle_diff < 8 and self.boost and self.lap == 3 and infos.next_checkpoint_id == 0:
            output_speed = "BOOST"
            self.boost = 0
            debug("BOOOOOOST")
        for e in enemy_pod_info:
            if dist(e.pos, infos.pos) < 1500 and self.init and not (infos.speed[0] == 0 == infos.speed[1]):
                debug("relative magn speed :" + str(magnitude(e.speed - infos.speed)))
                if dist(e.pos, infos.pos) < 1500 and self.init:
                    debug("relative magn speed :" + str(magnitude(e.speed - infos.speed)))
                    if magnitude(e.speed - infos.speed) > 100:
                        if magnitude(infos.speed) > 100:
                            if angle_btw(infos.speed, infos.pos, e.pos) < 10:
                                output_speed = "SHIELD"
                                debug("SHIELD UP")
                        if magnitude(e.speed) > 100:
                            if angle_btw(e.speed, e.pos, infos.pos) < 10:
                                output_speed = "SHIELD"
                                debug("SHIELD UP")
        if dist(ally.pos, infos.pos) < 1500:
            if magnitude(infos.speed) > 0 and magnitude(ally.speed - infos.speed) > 100:
                if angle_btw(infos.speed, infos.pos, ally.pos) < 15:
                    output_speed = "SHIELD"
        self.init = True
        return str(to_reach_x) + " " + str(to_reach_y) + " " + str(output_speed)

    """second mode"""

    def idle_fighter(self, infos: PodInfo):
        ally = ally_pod_info[1 - self.index]
        ally_check_id = ally.next_checkpoint_id
        next_check_pos = checkpoints[
            (ally_check_id + (dist(checkpoints[ally_check_id], ally.pos) < 8000)) % checkpoint_count]
        next_check_dist = dist(infos.pos, next_check_pos)
        if self.init and (infos.speed[0] or infos.speed[1]):
            # debug(str(infos.speed) + "m.s  " + str(infos.pos) + " pos  " + str(next_check_pos) + " check pos")
            self.angle_diff = angle_btw(infos.speed, infos.pos, next_check_pos)
            self.ally_angle_diff = angle_btw(infos.speed, infos.pos, ally_pod_info[1 - self.index].pos)
            # debug("speed : " + str(infos.speed))
            # debug("rotation_difference : " + str(angle_btw(infos.speed, infos.pos, next_check_pos)))
        # debug(infos.angle)
        # debug(rotate(np.array([0,0]), np.array([1,0]), infos.angle*pi/180))
        angle = angle_btw(rotate(np.array([0, 0]), np.array([1, 0]), infos.angle * pi / 180), infos.pos, next_check_pos)
        for e in enemy_pod_info:
            if dist(e.pos, infos.pos) < 4000 and next_check_dist < 1000:
                self.locked_target = e
        if self.locked_target:
            next_check_pos = self.locked_target.pos

        output_speed = speed(angle) if self.locked_target else min(speed(angle), int(next_check_dist / 50))
        # debug("speed : " + str(speed(angle)) + "  angle : " + str(angle))
        """toggle direction"""
        sensitivity = .01
        if self.init and angle < 20 and (infos.speed[0] or infos.speed[1]):
            # debug("angle diff : " + str(self.angle_diff))
            rot1 = rotate(infos.pos, next_check_pos, self.angle_diff * sensitivity).astype(int)
            rot2 = rotate(infos.pos, next_check_pos, -1 * self.angle_diff * sensitivity).astype(int)
            # debug(str(next_check_pos)+"/"+str(len(rot1)))
            if angle_btw(infos.speed, infos.pos, rot1) > angle_btw(infos.speed, infos.pos, rot2):
                to_reach_x, to_reach_y = rot1
            else:
                to_reach_x, to_reach_y = rot2
        else:
            to_reach_x = next_check_pos[0]
            to_reach_y = next_check_pos[1]

        if self.ally_angle_diff < 10 and dist(infos.pos, ally_pod_info[1 - self.index].pos) < 3000:
            output_speed = 10
        if self.angle_diff < 8 and self.boost and next_check_dist < 1000 and allies_controllers[1 - self.index].lap > 1:
            output_speed = "BOOST"
            self.boost = 0
            debug("BOOOOOOST")

        dist_ally = dist(infos.pos, ally_pod_info[1 - self.index].pos)
        if self.ally_angle_diff < 10 and dist_ally < 3000 and not (
                self.locked_target and dist(infos.pos, self.locked_target.pos) < dist_ally):
            output_speed = 10
        for e in enemy_pod_info:
            if dist(e.pos, infos.pos) < 1500 and self.init:
                debug("relative magn speed :" + str(magnitude(e.speed - infos.speed)))
                if magnitude(e.speed - infos.speed) > 100:
                    if magnitude(infos.speed) > 100:
                        if angle_btw(infos.speed, infos.pos, e.pos) < 10:
                            output_speed = "SHIELD"
                            debug("SHIELD UP")
                            self.locked_target = 0
                    if magnitude(e.speed) > 100:
                        if angle_btw(e.speed, e.pos, infos.pos) < 10:
                            output_speed = "SHIELD"
                            debug("SHIELD UP")
                            self.locked_target = 0
                if self.locked_target:
                    output_speed = "SHIELD"
                    self.locked_target = 0
            if next_check_dist < 500 and not self.locked_target and dist(e.pos, infos.pos) < 3000:
                output_speed = "SHIELD"
        if output_speed != "SHIELD" and next_check_dist < 600 and not self.locked_target:
            to_reach_x = checkpoints[(ally_check_id + 1) % checkpoint_count][0]
            to_reach_y = checkpoints[(ally_check_id + 1) % checkpoint_count][1]
            output_speed = 0
        self.init = True

        return str(to_reach_x) + " " + str(to_reach_y) + " " + str(output_speed)

    def move_fighter(self, infos: PodInfo):
        next_check_pos = enemy_pod_info[0].pos
        next_check_dist = dist(infos.pos, next_check_pos)
        if self.init and (infos.speed[0] or infos.speed[1]):
            # debug(str(infos.speed) + "m.s  " + str(infos.pos) + " pos  " + str(next_check_pos) + " check pos")
            self.angle_diff = angle_btw(infos.speed, infos.pos, next_check_pos)
            self.ally_angle_diff = angle_btw(infos.speed, infos.pos, ally_pod_info[1 - self.index].pos)
            # debug("speed : " + str(infos.speed))
            # debug("rotation_difference : " + str(angle_btw(infos.speed, infos.pos, next_check_pos)))
        # debug(infos.angle)
        # debug(rotate(np.array([0,0]), np.array([1,0]), infos.angle*pi/180))
        angle = angle_btw(rotate(np.array([0, 0]), np.array([1, 0]), infos.angle * pi / 180), infos.pos, next_check_pos)
        output_speed = 100
        output_speed = speed(angle)
        # debug("speed : " + str(speed(angle)) + "  angle : " + str(angle))
        """toggle direction"""
        sensitivity = .01
        if self.init and angle < 20 and (infos.speed[0] or infos.speed[1]):
            # debug("angle diff : " + str(self.angle_diff))
            rot1 = rotate(infos.pos, next_check_pos, self.angle_diff * sensitivity).astype(int)
            rot2 = rotate(infos.pos, next_check_pos, -1 * self.angle_diff * sensitivity).astype(int)
            # debug(str(next_check_pos)+"/"+str(len(rot1)))
            if angle_btw(infos.speed, infos.pos, rot1) > angle_btw(infos.speed, infos.pos, rot2):
                to_reach_x, to_reach_y = rot1
            else:
                to_reach_x, to_reach_y = rot2
        else:
            to_reach_x = next_check_pos[0]
            to_reach_y = next_check_pos[1]

        op_check_dist = []
        # for j in range(2):
        #     if enemy_pod_info[j].next_checkpoint_id == infos.next_checkpoint_id:
        #         op_check_dist.append(dist(enemy_pod_info[j].pos, next_check_pos))
        #
        # for op_dist in op_check_dist:
        #     if 0 < op_dist - next_check_dist < 2000 and output_speed == 100 \
        #             and not (self.lap == lap_count and
        #                      (checkpoint_count - infos.next_checkpoint_id < 3 or infos.next_checkpoint_id == 0)):
        #         debug("WE ARE SLOWING DOWN")
        #         output_speed = 50
        #
        # if op_check_dist < min(next_check_dist, 2000):
        #     if not self.locked_target and dist(opponent_x, opponent_y, x,
        #                                        y) < 1000 and next_checkpoint_x != self.previous_check_aim:
        #         self.locked_target = True
        #         debug("TARGET LOCKED")
        # if self.locked_target:
        #     to_reach_x = opponent_x
        #     to_reach_y = opponent_y
        #     s = 100
        #     debug(dist(opponent_x, opponent_y, x, y))
        # if dist(opponent_x, opponent_y, x, y) < 1000 and self.locked_target:
        #     locked_target = False
        #     self.previous_check_aim = next_check_pos[0]
        #     debug("_______________TARGET UNLOCKED__________________")
        if self.ally_angle_diff < 10:
            output_speed = 10
        if self.angle_diff < 8 and self.boost and next_check_dist < 1000 and allies_controllers[1 - self.index].lap > 1:
            output_speed = "BOOST"
            self.boost = 0
            debug("BOOOOOOST")

        for e in enemy_pod_info:
            if dist(e.pos, infos.pos) < 1500 and self.init and not (infos.speed[0] == 0 == infos.speed[1]):
                debug("relative magn speed :" + str(magnitude(e.speed - infos.speed)))
                if magnitude(e.speed - infos.speed) > 100:
                    if angle_btw(infos.speed, infos.pos, e.pos) < 10 and magnitude(infos.speed) > 100 or angle_btw(
                            e.speed, e.pos, infos.pos) < 10 and magnitude(e.speed) > 100:
                        output_speed = "SHIELD"
                        debug("SHIELD UP")
        self.init = True
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
    return int(acos(sum(orientation * (pos2 - pos1)) / (
            sum(orientation ** 2) ** .5 * sum((pos2 - pos1) ** 2) ** .5)) * 180 / pi)



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
    debug(s)
    print(s)
    print(allies_controllers[1].get_output(ally_pod_info[1]))
