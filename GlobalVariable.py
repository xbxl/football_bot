"""
用来存储全局变量
"""
from math import sqrt


class GlobalVariable:
    tick = -1


# 计算到中心距离
def get_distance(x, y, tar_x=0, tar_y=0):
    distance = sqrt((x-tar_x) ** 2 + (y-tar_y) ** 2)
    return distance


# 判断是否两个机器人太近了
def is_distance_too_close(robot1, robot2, least_distance):
    temp = sqrt((robot1[0] - robot2[0]) ** 2 + (robot1[1] - robot2[1]) ** 2)
    print(temp)
    return temp < least_distance


# 判断是最短距离
def get_closest_robot(robot_xy_list):
    # 最短的机器人编号
    robot_index = 0
    max_distance = 0
    for i in range(len(robot_xy_list)):
        distance = get_distance(robot_xy_list[i][0], robot_xy_list[i][1])
        if distance > max_distance:
            max_distance = distance
            robot_index = i
    return robot_index


# 记录坐标
# for i in range(0, 3):
#     opp_xy_info.append((oppRobots[i].get_pos().x, oppRobots[i].get_pos().y))
#     base_xy_info.append((baseRobots[i].get_pos().x, baseRobots[i].get_pos().y))
def save_xy(robot_list, robot_info_list):
    for i in range(0, 3):
        robot_info_list.append((robot_list[i].get_pos().x, robot_list[i].get_pos().y))
