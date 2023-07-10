"""
这段代码提供了一些用于策略开发的类型定义和辅助函数。
"""
from typing import Optional, List

"""
unbox_field、unbox_event和unbox_int是三个装饰器函数，
用于处理函数的输入参数，将传入的对象进行拷贝（深拷贝）操作，避免对原始对象的修改。
这些装饰器函数可以应用于其他函数上，用于处理传入的Field、EventArguments和int类型的参数。
"""


def unbox_field(func):
    def unbox_func(field: Field):
        new_field = None
        if (field is not None):
            new_field = Field.copy(field)
        return func(new_field)

    return unbox_func


def unbox_event(func):
    def unbox_func(event_type: int, args: EventArguments):
        new_event_type = event_type
        new_args = None
        if (args is not None):
            new_args = EventArguments.copy(args)
        return func(new_event_type, new_args)

    return unbox_func


def unbox_int(func):
    def unbox_func(i: int):
        new_i = i
        return func(new_i)

    return unbox_func


# 定义队伍：
#   我方，对方
#   一般用于调用各方机器人或判断定位球执行者
class Team():
    Self = 0
    Opponent = 1
    Nobody = 2


# 定义一些事件类型：
#   判罚结果，比赛开始，比赛暂停，上半场开始，下半场开始，加时开始，5v5比赛的点球大战开始，点球大战比赛开始，突破重围开始
class EventType():
    JudgeResult = 0
    MatchStart = 1
    MatchStop = 2
    FirstHalfStart = 3
    SecondHalfStart = 4
    OvertimeStart = 5
    PenaltyShootoutStart = 6


# 定义版本常量(似乎没用)
class Version():
    V1_0 = 0
    V1_1 = 1


# 定义一些判罚类型：
#   开球，门球，点球，争球
#   执行方
#   判罚原因
class JudgeResultEvent:
    class ResultType():
        PlaceKick = 0
        GoalKick = 1
        PenaltyKick = 2
        FreeKickRightTop = 3
        FreeKickRightBot = 4
        FreeKickLeftTop = 5
        FreeKickLeftBot = 6

    type: int  # ResultType
    offensive_team: int  # Team
    reason: str

    def copy(old):
        new = None
        if (old is not None):
            new = JudgeResultEvent()
            if hasattr(old, 'type'):
                new.type = old.type
            if hasattr(old, 'offensive_team'):
                new.offensive_team = old.offensive_team
            if hasattr(old, 'reason'):
                new.reason = old.reason
        return new


# 定义判罚事件：
class EventArguments:
    judge_result: Optional[JudgeResultEvent]

    def copy(old):
        new = None
        if (old is not None):
            new = EventArguments()
            if hasattr(old, 'judge_result'):
                new.judge_result = JudgeResultEvent.copy(old.judge_result)
        return new


# 定义坐标的二维向量
class Vector2:
    x: float
    y: float

    def copy(old):
        new = None
        if (old is not None):
            new = Vector2()
            if hasattr(old, 'x'):
                new.x = old.x
            if hasattr(old, 'y'):
                new.y = old.y
        return new


# 定义左右轮速
class Wheel:
    left_speed: float
    right_speed: float

    def copy(old):
        new = None
        if (old is not None):
            new = Wheel()
            if hasattr(old, 'left_speed'):
                new.left_speed = old.left_speed
            if hasattr(old, 'right_speed'):
                new.right_speed = old.right_speed
        return new


# 定义机器人类：
#   属性有：坐标，旋转角，轮（速）
class Robot:
    position: Vector2
    rotation: float
    wheel: Wheel

    def copy(old):
        new = None
        if (old is not None):
            new = Robot()
            if hasattr(old, 'position'):
                new.position = Vector2.copy(old.position)
            if hasattr(old, 'rotation'):
                new.rotation = old.rotation
            if hasattr(old, 'wheel'):
                new.wheel = Wheel.copy(old.wheel)
        return new


# 定义球的二维坐标
class Ball:
    position: Vector2

    def copy(old):
        new = None
        if (old is not None):
            new = Ball()
            if hasattr(old, 'position'):
                new.position = Vector2.copy(old.position)
        return new


# 定义环境类：
#   我方机器人数组，对方机器人数组，球，当前拍数（每秒66拍）
class Field:
    self_robots: List[Robot]
    opponent_robots: List[Robot]
    ball: Ball
    tick: int

    def copy(old):
        new = None
        if (old is not None):
            new = Field()
            if hasattr(old, 'self_robots'):
                new.self_robots = [Robot.copy(r) for r in old.self_robots]
            if hasattr(old, 'opponent_robots'):
                new.opponent_robots = [Robot.copy(r) for r in old.opponent_robots]
            if hasattr(old, 'ball'):
                new.ball = Ball.copy(old.ball)
            if hasattr(old, 'tick'):
                new.tick = old.tick
        return new
