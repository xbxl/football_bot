"""
这段代码实现了一个的策略开发框架
"""
import random
from typing import Tuple, Union
# from V5RPC import *
from baseRobot import *
from GlobalVariable import *
import math

baseRobots = []  # 我方机器人数组
oppRobots = []  # 敌方机器人数组
data_loader = DataLoader()  # 数据加载器对象哦
race_state = -1  # 定位球状态
race_state_trigger = -1  # 触发方

# note 新增
not_ok_dict = {}  # note 维护字典，防止决策重复
right_border_dict = {}
robot_killed_nums = {0: 0, 1: 0, 2: 0}


# 时间处理函数
#   接收：比赛状态变化的信息
#   作用：根据事件类型打印相关的状态消息
@unbox_event
def on_event(event_type: int, args: EventArguments):
    # 打印当前状态，event表示比赛进入哪一阶段，比如暂停，上半场，下半场等等
    event = {
        0: lambda: print(args.judge_result.reason),
        1: lambda: print("Match Start"),
        2: lambda: print("Match Stop"),
        3: lambda: print("First Half Start"),
        4: lambda: print("Second Half Start"),
        5: lambda: print("Overtime Start"),
        6: lambda: print("Penalty Shootout Start"),
        7: lambda: print("MatchShootOutStart"),
        8: lambda: print("MatchBlockStart")
    }
    global race_state_trigger
    global race_state
    # 比赛进行过程中，打印当前状态，由于是突破重围策略，所以只打印开球状态，并打印出发球方
    if event_type == 0:
        race_state = args.judge_result.type
        race_state_trigger = args.judge_result.offensive_team
        if race_state == JudgeResultEvent.ResultType.PlaceKick:
            print("PlaceKick")
        actor = {
            Team.Self: lambda: print("By Self"),
            Team.Opponent: lambda: print("By Opp"),
            Team.Nobody: lambda: print("By Nobody"),
        }
        actor[race_state_trigger]()

    event[event_type]()


# 控制队名
@unbox_int
def get_team_info(server_version: int) -> str:
    version = {
        0: "V1.0",
        1: "V1.1"
    }
    print(f'server rpc version: {version.get(server_version, "V1.0")}')
    # 返回字符串表示队名
    return 'xbxl'


# 策略的核心函数：
#   接收：当前球的x,y坐标
#   作用：根据比赛状态(定位球状态+触发方)执行相应的策略
def strategy(football_now_x, football_now_y, tick):
    global not_ok_dict, right_border_dict, robot_killed_nums

    if race_state == JudgeResultEvent.ResultType.PlaceKick:
        # 进攻！！！
        if race_state_trigger == Team.Self:
            # baseRobots[0].set_wheel_velocity(125,125)
            opp_xy_info: List[Tuple[float, float]] = []  # 敌方坐标列表
            base_xy_info: List[Tuple[float, float]] = []  # 我方坐标列表
            # 保存x,y坐标
            save_xy(baseRobots, base_xy_info)
            save_xy(oppRobots, opp_xy_info)

            # 若不在圈内，则要进入
            for i in range(0, 3):
                if not is_safe(base_xy_info[i]):
                    baseRobots[i].moveto(120, random.randint(-5, 5))
                else:
                    # pass
                    baseRobots[i].moveto(120, random.randint(-5, 5))  # note 随机数，为的是能进去对方基地

            # 维护列表
            not_ok_dict = del_value_by_tick(not_ok_dict, tick - 2)  # 用来防堵
            right_border_dict = del_value_by_tick(right_border_dict, tick - 3)

            # 处理僵持 note 必须要防止重复！
            distance = 30  # 距离过近的阈值
            for i in range(len(base_xy_info)):  # 遍历我方坐标
                for j in range(len(opp_xy_info)):  # 遍历地方坐标
                    # 距离过近 处理逻辑
                    if is_distance_too_close(opp_xy_info[i], base_xy_info[j], distance):
                        # print(f"自己家的机器人{i + 1}和对面机器人{j + 1}之间的距离过近")     # 调试
                        opp_x, opp_y = opp_xy_info[j][0], opp_xy_info[j][1]
                        if is_safe(base_xy_info[i]):
                            baseRobots[i].moveto(120, random.randint(-20, 20))
                        # 右边界->则往中间靠
                        elif is_right_border(base_xy_info[i]):  # note 己方是否在对方基地边界
                            if i not in right_border_dict:
                                right_border_dict[i] = tick  # 添加到字典
                                baseRobots[i].moveto(opp_x, 0)
                                # baseRobots[i].moveto(base_xy_info[i][0],
                                #                      base_xy_info[i][1] + random.randint(-20, 20))
                            else:
                                pass
                                # if robot_killed_nums[i] > 8:
                                #     baseRobots[i].moveto(opp_x + random.randint(-20, 20),
                                #                          opp_y + random.randint(-20, 20))
                        else:
                            # print(i)  # 调试
                            # note 避障
                            if i not in not_ok_dict:
                                not_ok_dict[i] = tick
                                # print(not_ok_dict)  # 调试
                                robot_killed_nums[i] += 1
                                # baseRobots[i].moveto(opp_x, opp_y + random.randint(-20, 20))
                                baseRobots[i].moveto(opp_x - 10, opp_y + random.randint(-50, 50))

                    # else:
                    #     baseRobots[i].moveto(120, 0)
        # 防守！！！
        if race_state_trigger == Team.Opponent:
            # note 1+2防守: 假设0 为外围 1，2内围
            """
            防守大区域为 (-110,-40) -> (-75,40)
            防守小区域为 (-110,-25) -> (-94,25)
            """

            # todo 重点修改防守
            # 先记录此时坐标
            opp_xy_info: List[Tuple[float, float]] = []  # 敌方坐标列表
            base_xy_info: List[Tuple[float, float]] = []  # 我方坐标列表

            # 保存x,y坐标
            save_xy(baseRobots, base_xy_info)
            save_xy(oppRobots, opp_xy_info)

            # todo 集群：3个打一个推到对方基地(假设只攻击距离最近的那一个)
            # 距离最近，距离中心点最近(0，0):
            #   修改 (-110,0),并且不能在内
            opp_closest_robot_index = get_closest_robot(opp_xy_info)
            # 记录对方坐标
            opp_x = opp_xy_info[opp_closest_robot_index][0]
            opp_y = opp_xy_info[opp_closest_robot_index][1]
            # todo 数量限制（防止乌龙），一个死追，其它两个带预判
            if opp_y > -110:  # 对方在外面
                pass
            else:  # 否则换目标
                opp_closest_robot_index = (opp_closest_robot_index + 1) % 3
                # 记录对方坐标
                opp_x = opp_xy_info[opp_closest_robot_index][0]
                opp_y = opp_xy_info[opp_closest_robot_index][1]

            for i in range(0, 3):
                if opp_x < base_xy_info[opp_closest_robot_index][0]:  # 对方想逃逸
                    opp_x -= 10
                if math.fabs(opp_y) < base_xy_info[opp_closest_robot_index][1]:
                    opp_x -= 10
                    opp_y *= 0.9

                # todo 数量限制 对方到了边界
                if is_left_border((opp_x, opp_y)):
                    error_num = 0
                    error_index_lists = []  # 错误机器人编号列表
                    for j in range(0, 3):
                        if math.fabs(base_xy_info[i][1]) > math.fabs(opp_y):
                            error_num += 1
                        if error_num > 1:
                            error_index_lists.append(i)
                    for j in error_index_lists:
                        baseRobots[j].moveto(opp_x, opp_y * 0.9)
                baseRobots[i].moveto(opp_x, opp_y)

    for i in range(0, 5):  # 保存信息
        # baseRobots[i].set_wheel_velocity(125, 125)
        baseRobots[i].save_last_information(football_now_x, football_now_y)


# get_instruction函数，用于获取指令，接收 Field 对象，更新机器人状态
#   接收：Field 对象
#   作用：调用“strategy”函数执行策略
@unbox_field
def get_instruction(field: Field):
    # python start.py 20000pytprint(field.tick)  # tick从2起始
    GlobalVariable.tick = field.tick
    for i in range(0, 5):
        baseRobots.append(BaseRobot())
        oppRobots.append(BaseRobot())
        baseRobots[i].update(field.self_robots[i])
        oppRobots[i].update(field.opponent_robots[i])
        # print(field.self_robots[i].position)
        # print("baseRobot information: " + str(baseRobots[i].get_pos().x) + "," + str(baseRobots[i].get_pos().y))
    football_now_x = -field.ball.position.x  # 黄方假设，球坐标取反
    football_now_y = -field.ball.position.y
    strategy(football_now_x, football_now_y, GlobalVariable.tick)  # 核心策略函数，调用此函数进行进入策略主函数
    # print(baseRobots[0].lastTargetX)   # 调试
    data_loader.set_tick_state(GlobalVariable.tick, race_state)
    velocity_to_set = []
    # 这里就三个机器人，但是修改不了，也许默认平台是5个！！！
    for i in range(0, 5):
        velocity_to_set.append((baseRobots[i].robot.wheel.left_speed, baseRobots[i].robot.wheel.right_speed))
    return velocity_to_set, 0  # 以第二元素的(0,1)表明重置开关,1表示重置


# get_placement函数，获取摆位信息：
#   依据：比赛状态 和 触发方
#   返回：球的final location(无具体作用)
@unbox_field
def get_placement(field: Field) -> List[Tuple[float, float, float]]:
    final_set_pos: List[Union[Tuple[int, int, int], Tuple[float, float, float]]]
    if race_state == JudgeResultEvent.ResultType.PlaceKick:
        if race_state_trigger == Team.Self:
            print("进攻摆位")
            set_pos = [[-100, 20, 30],
                       [-120, 0, 0],
                       [-100, -20, -30],
                       [0, 0, 0],
                       [0, 0, 0],
                       [0.0, 0.0, 0.0]]

        else:  # if race_state_trigger == Team.Opponent:
            print("防守摆位")
            set_pos = [[-72.5, 0, 0],
                       [-100, 20, 0],
                       [-100, -20, 0],
                       [0, 0, 0],
                       [0, 0, 0],
                       [0.0, 0.0, 0.0]]
    else:
        set_pos = [[0, 20, 90],
                   [10, 20, -90],
                   [10, -20, -90],
                   [0, 0, 0],
                   [0, 0, 0],
                   [0.0, 0.0, 0.0]]

    for set_pos_s in set_pos:  # 摆位反转
        set_pos_s[0] = -set_pos_s[0]
        set_pos_s[1] = -set_pos_s[1]
        set_pos_s[2] -= 180
        if set_pos_s[2] < -180:
            set_pos_s[2] += 360

    final_set_pos = [(set_pos[0][0], set_pos[0][1], set_pos[0][2]),
                     (set_pos[1][0], set_pos[1][1], set_pos[1][2]),
                     (set_pos[2][0], set_pos[2][1], set_pos[2][2]),
                     (set_pos[3][0], set_pos[3][1], set_pos[3][2]),
                     (set_pos[4][0], set_pos[4][1], set_pos[4][2]),
                     (0.0, 0.0, 0.0)]

    print(final_set_pos)
    return final_set_pos  # 最后一个可以写球位置（x,y,角）,角其实没用
