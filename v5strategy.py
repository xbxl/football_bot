"""
这段代码实现了一个的策略开发框架
"""
# import random
from typing import Tuple, Union
# from V5RPC import *
from baseRobot import *
from GlobalVariable import *

baseRobots = []  # 我方机器人数组
oppRobots = []  # 敌方机器人数组
data_loader = DataLoader()  # 数据加载器对象哦
race_state = -1  # 定位球状态
race_state_trigger = -1  # 触发方


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
def strategy(football_now_x, football_now_y):
    if race_state == JudgeResultEvent.ResultType.PlaceKick:
        if race_state_trigger == Team.Self:
            # baseRobots[0].set_wheel_velocity(125,125)
            baseRobots[0].moveto(120, 15)  # 进攻状态下分别避障跑位到110，±15
            baseRobots[1].moveto(120, -15)
        if race_state_trigger == Team.Opponent:  # 防守状态下直接冲对面
            # baseRobots[0].moveto(football_now_x, football_now_y)
            baseRobots[0].moveto(oppRobots[0].get_pos().x, oppRobots[0].get_pos().y)
            baseRobots[1].moveto(oppRobots[1].get_pos().x, oppRobots[1].get_pos().y)
            baseRobots[0].set_wheel_velocity(125, 125)
    for i in range(0, 5):  # 保存信息
        # baseRobots[i].set_wheel_velocity(125, 125);
        baseRobots[i].save_last_information(football_now_x, football_now_y)


# python start.py 20001


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
    strategy(football_now_x, football_now_y)  # 核心策略函数，调用此函数进行进入策略主函数
    data_loader.set_tick_state(GlobalVariable.tick, race_state)
    velocity_to_set = []
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
            print("开球进攻摆位")
            set_pos = [[-100, 20, 0],
                       [-100, -20, 180],
                       [-3, -10, 0],
                       [-3, 10, 0],
                       [-3, 0, 0],
                       [0.0, 0.0, 0.0]]
            # set_pos = [(-103, 0, 90), (30, 0, 0), (-3, -10, 0), (-3, 10, 0), (-3, 0, 0), (0.0, 0.0, 0.0)]
        else:  # if race_state_trigger == Team.Opponent:
            print("开球防守摆位")
            set_pos = [[-80, -3.5, 0],
                       [-80, 3.5, 0],
                       [-10, -80, -90],
                       [-10, 70, -90],
                       [-10, -80, -90],
                       [0.0, 0.0, 0.0]]
            # set_pos = [(-105, 0, 90), (10, 20, -90), (10, -20, -90), (10, 40, -90), (10, -40, -90), (0.0, 0.0, 0.0)]
    else:
        set_pos = [[-100, 20, 90],
                   [10, 20, -90],
                   [10, -20, -90],
                   [10, 40, -90],
                   [10, -40, -90],
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
    return final_set_pos  # 最后一个是球位置（x,y,角）,角其实没用
