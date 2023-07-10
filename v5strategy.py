"""
这个文件是主要开发文件，涵盖了策略全部的四个接口
-on_event接收比赛状态变化的信息。
    参数event_type type表示事件类型；
    参数EventArgument表示该事件的参数，如果不含参数，则为NULL。
-get_team_info控制队名。
    修改返回值的字符串即可修改自己的队名
-get_instruction控制5个机器人的轮速(leftspeed,rightspeed)，以及最后的reset(1即表明需要reset)
    通过返回值来给机器人赋轮速
    比赛中的每拍被调用，需要策略指定轮速，相当于旧接口的Strategy。
    参数field为In/Out参数，存储当前赛场信息，并允许策略修改己方轮速。
    ！！！所有策略的开发应该在此模块
-get_placement控制5个机器人及球在需要摆位时的位置
    通过返回值来控制机器人和球的摆位。
    每次自动摆位时被调用，需要策略指定摆位信息。
    定位球类的摆位需要符合规则，否则会被重摆
"""
from typing import Tuple, Union

from baseRobot import *

baseRobots = []  # 定义我方机器人数组
oppRobots = []  # 定义对方机器人数组
data_loader = DataLoader()
race_state = -1  # 定位球状态
race_state_trigger = -1  # 触发方


# 打印比赛状态，详细请对比v5rpc.py
@unbox_event
def on_event(event_type: int, args: EventArguments):
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
    if event_type == 0:
        race_state = args.judge_result.type
        race_state_trigger = args.judge_result.offensive_team
        if race_state == JudgeResultEvent.ResultType.PlaceKick:
            print("Place Kick")
        elif race_state == JudgeResultEvent.ResultType.PenaltyKick:
            print("Penalty Kick")
        elif race_state == JudgeResultEvent.ResultType.GoalKick:
            print("Goal Kick")
        elif (race_state == JudgeResultEvent.ResultType.FreeKickLeftBot
              or race_state == JudgeResultEvent.ResultType.FreeKickRightBot
              or race_state == JudgeResultEvent.ResultType.FreeKickLeftTop
              or race_state == JudgeResultEvent.ResultType.FreeKickRightTop):
            print("Free Kick")

        actor = {
            Team.Self: lambda: print("By Self"),
            Team.Opponent: lambda: print("By Opp"),
            Team.Nobody: lambda: print("By Nobody"),
        }
        actor[race_state_trigger]()

    event[event_type]()


@unbox_int
def get_team_info(server_version: int) -> str:
    version = {
        0: "V1.0",
        1: "V1.1"
    }
    print(f'server rpc version: {version.get(server_version, "V1.0")}')
    return 'Python Strategy Server'  # 在此行修改双引号中的字符串为自己的队伍名


def strategy(football_now_x, football_now_y):
    # 1号机器人在限制范围内追球，其他机器人固定x坐标，在一条直线上上下运动
    baseRobots[1].moveto_within_x_limits(80, football_now_x, football_now_y)
    baseRobots[2].move_in_still_x(-30, football_now_y)
    baseRobots[3].move_in_still_x(-50, football_now_y)
    baseRobots[4].move_in_still_x(-80, football_now_y)

    if baseRobots[0].get_pos().x <= -110 + 2.4:  # 守门员行为
        baseRobots[0].moveto(-110 + 1.5, 0)
    else:
        if np.fabs(football_now_y) < 20 - 0.7:  # 球的y坐标在门框范围内
            if football_now_x > -110 + 17:  # 如果球离门很远
                baseRobots[0].moveto(-110 + 1.6, football_now_y)  # 如果球离门很远
            else:  # 如果球的y在门框范围外
                baseRobots[0].moveto(football_now_x, football_now_y)
        else:
            if football_now_y > 0:  # 上半场
                baseRobots[0].moveto(-110 + 1.6, 20 - 2.2)  # 门将在门框上侧摆动
            else:  # 下半场
                baseRobots[0].moveto(-110 + 1.6, -(20 - 2.2))

    for i in range(0, 5):
        baseRobots[i].save_last_information(football_now_x, football_now_y)


# python start.py 20001
'''
获得策略信息
策略接口，相当于策略执行的主模块，可以不恰当地理解为main函数,是主要开发的部分
'''


@unbox_field
def get_instruction(field: Field):
    # python start.py 20000    print(field.tick)  # tick从2起始
    GlobalVariable.tick = field.tick
    for i in range(0, 5):
        baseRobots.append(BaseRobot())
        oppRobots.append(BaseRobot())
        baseRobots[i].update(field.self_robots[i])  # 每一拍更新己方机器人信息给BaseRobot
        oppRobots[i].update(field.opponent_robots[i])  # 每一拍更新对方机器人信息给OppRobot
        # print(field.self_robots[i].position)
        # print("baseRobot information: " + str(baseRobots[i].get_pos().x) + "," + str(baseRobots[i].get_pos().y))
    football_now_x = -field.ball.position.x  # 黄方假设，球坐标取反
    football_now_y = -field.ball.position.y
    strategy(football_now_x, football_now_y)  # 执行策略
    data_loader.set_tick_state(GlobalVariable.tick, race_state)
    velocity_to_set = []
    for i in range(0, 5):
        velocity_to_set.append((baseRobots[i].robot.wheel.left_speed, baseRobots[i].robot.wheel.right_speed))
    return velocity_to_set, 0  # 以第二元素的(0,1)表明重置开关,1表示重置


@unbox_field
def get_placement(field: Field) -> List[Tuple[float, float, float]]:
    final_set_pos: List[Union[Tuple[int, int, int], Tuple[float, float, float]]]
    if race_state == JudgeResultEvent.ResultType.PlaceKick:
        if race_state_trigger == Team.Self:
            print("开球进攻摆位")
            set_pos = [[-100, 20, 0],
                       [42, 42, 180],
                       [-30, -10, 0],
                       [-50, 10, 0],
                       [-80, 0, 0],
                       [0.0, 0.0, 0.0]]
            # set_pos = [(-103, 0, 90), (30, 0, 0), (-3, -10, 0), (-3, 10, 0), (-3, 0, 0), (0.0, 0.0, 0.0)]
        else:  # if race_state_trigger == Team.Opponent:
            print("开球防守摆位")
            set_pos = [[-100, 20, 0],
                       [-10, 80, -90],
                       [-30, -80, -90],
                       [-50, 70, -90],
                       [-80, -80, -90],
                       [0.0, 0.0, 0.0]]
            # set_pos = [(-105, 0, 90), (10, 20, -90), (10, -20, -90), (10, 40, -90), (10, -40, -90), (0.0, 0.0, 0.0)]
    elif race_state == JudgeResultEvent.ResultType.PenaltyKick:
        if race_state_trigger == Team.Self:
            print("点球进攻摆位")
            set_pos = [[-103, 0, 90],
                       [30, 0, 0],
                       [-3, -10, 0],
                       [-3, 10, 0],
                       [-3, 0, 0],
                       [0.0, 0.0, 0.0]]
        else:  # if race_state_trigger == Team.Opponent:
            print("点球防守摆位")
            set_pos = [[-105, 0, 00],
                       [30, 0, 0],
                       [10, -10, 0],
                       [10, 10, 0],
                       [10, 0, 0],
                       [0.0, 0.0, 0.0]]
    elif race_state == JudgeResultEvent.ResultType.GoalKick:
        if race_state_trigger == Team.Self:
            print("门球进攻摆位")
            set_pos = [[-103, 0, 0],
                       [30, 0, 0],
                       [-30, -10, 0],
                       [-50, 10, 0],
                       [-80, 0, 0],
                       [-110 + 15, 0.0, 0.0]]
        else:  # if race_state_trigger == Team.Opponent:
            print("门球防守摆位")
            set_pos = [[-105, 0, 0],
                       [30, 0, 0],
                       [-30, -10, 0],
                       [-50, 10, 0],
                       [-80, 0, 0],
                       [0.0, 0.0, 0.0]]
    elif (race_state == JudgeResultEvent.ResultType.FreeKickLeftTop
          or race_state == JudgeResultEvent.ResultType.FreeKickRightTop
          or race_state == JudgeResultEvent.ResultType.FreeKickRightBot
          or race_state == JudgeResultEvent.ResultType.FreeKickLeftBot):
        if race_state_trigger == Team.Self:
            print("争球进攻摆位")
            set_pos = [[-103, 0, 90],
                       [30, 0, 0],
                       [-3, -10, 0],
                       [-3, 10, 0],
                       [-3, 0, 0],
                       [0.0, 0.0, 0.0]]
        else:  # if race_state_trigger == Team.Opponent:
            print("争球防守摆位")
            set_pos = [[-105, 0, 00],
                       [30, 0, 0],
                       [10, -10, 0],
                       [10, 10, 0],
                       [10, 0, 0],
                       [0.0, 0.0, 0.0]]
    else:
        print("race_state = " + str(race_state))

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
                     (set_pos[5][0], set_pos[5][1], set_pos[5][2])]

    print(final_set_pos)
    return final_set_pos  # 最后一个是球位置（x,y,角）,角其实没用
