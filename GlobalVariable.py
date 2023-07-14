"""
用来存储全局变量
"""
from math import sqrt


class GlobalVariable:
    tick = -1


# 计算到中心距离
def get_distance(x, y, tar_x=-110, tar_y=0):
    distance = sqrt((x - tar_x) ** 2 + (y - tar_y) ** 2)
    return distance


# 判断是否两个机器人太近了
def is_distance_too_close(robot1, robot2, least_distance):
    temp = get_distance(robot1[0], robot1[1], robot2[0], robot2[1])
    # print(temp)     # 调试
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


# 右侧边界
def is_right_border(temp):
    return 105 < temp[0] < 110 and (temp[1] > 20 or temp[1] < -20)


def is_left_border(temp):
    return -110 < temp[0] < -105 and (temp[1] > 20 or temp[1] < -20)


# 上边界
def is_up_border(temp):
    return temp > 75


# 下边界
def is_down_border(temp):
    return temp < 75


def is_safe(temp):
    return temp[0] > 110


# 根据tick维护字典
def del_value_by_tick(_dict, _tick):
    value_to_remove = _tick
    temp_dict = {key: value for key, value in _dict.items() if value != value_to_remove}
    return temp_dict

# if race_state_trigger == Team.Opponent:
#     # todo 重点修改防守
#
#     # 先记录此时坐标
#     opp_xy_info: List[Tuple[float, float]] = []  # 敌方坐标列表
#     base_xy_info: List[Tuple[float, float]] = []  # 我方坐标列表
#
#     # 保存x,y坐标
#     save_xy(baseRobots, base_xy_info)
#     save_xy(oppRobots, opp_xy_info)
#
#     # 各追各的
#     for i in range(0, 3):
#         baseRobots[i].moveto(opp_xy_info[i][0], opp_xy_info[i][1])
#     return
#
#     # 距离最近，距离中心点最近(-110,0)
#     opp_closest_robot_index = get_closest_robot(opp_xy_info)
#     # 记录对方坐标
#     opp_x = opp_xy_info[opp_closest_robot_index][0]
#     opp_y = opp_xy_info[opp_closest_robot_index][1]
#     # todo 数量限制（防止乌龙），一个死追，其它两个带预判
#     if opp_y > -110:  # 对方在外面
#         pass
#     else:  # 否则换目标
#         opp_closest_robot_index = (opp_closest_robot_index + 1) % 3
#         # 记录对方坐标
#         opp_x = opp_xy_info[opp_closest_robot_index][0]
#         opp_y = opp_xy_info[opp_closest_robot_index][1]
#
#     if opp_x < base_xy_info[opp_closest_robot_index][0]:  # 对方想逃逸
#         opp_x -= 10
#     if math.fabs(opp_y) < base_xy_info[opp_closest_robot_index][1]:
#         opp_y *= 0.9
#
#     # note 到了边界也不放走
#     error_index_lists = []  # 初始化+ 错误机器人编号列表
#     if is_left_border((opp_x, opp_y)):
#         error_num = 0  # 临时记录地方卡在边界的数量
#         for j in range(0, 3):
#             if math.fabs(base_xy_info[j][1]) > math.fabs(opp_y):  # 防守机器人在两侧
#                 error_num += 1
#             if error_num > 1:
#                 error_index_lists.append(j)
#         for j in error_index_lists:
#             baseRobots[j].moveto(opp_x, opp_y * 0.9)
