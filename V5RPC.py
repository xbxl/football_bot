"""
This is types and helpers for strategies with PyV5Adapter.
阅读代码时只需要了解各个class中存在哪些变量即可
"""
from typing import Optional, List


def unbox_field(func):
    def unbox_func(field: Field):
        new_field = None
        if(field is not None):
            new_field = Field.copy(field)
        return func(new_field)
    return unbox_func

def unbox_event(func):
    def unbox_func(event_type: int, args: EventArguments):
        new_event_type = event_type
        new_args = None
        if(args is not None):
            new_args = EventArguments.copy(args)
        return func(new_event_type, new_args)
    return unbox_func

def unbox_int(func):
    def unbox_func(i: int):
        new_i = i
        return func(new_i)
    return unbox_func

class Team():
    Self = 0
    Opponent = 1
    Nobody = 2


class EventType():
    JudgeResult = 0
    MatchStart = 1
    MatchStop = 2
    FirstHalfStart = 3
    SecondHalfStart = 4
    OvertimeStart = 5
    PenaltyShootoutStart = 6


class Version():
    V1_0 = 0
    V1_1 = 1


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
        if(old is not None):
            new = JudgeResultEvent()
            if hasattr(old, 'type'):
                new.type = old.type
            if hasattr(old, 'offensive_team'):
                new.offensive_team = old.offensive_team
            if hasattr(old, 'reason'):
                new.reason = old.reason
        return new


class EventArguments:
    judge_result: Optional[JudgeResultEvent]

    def copy(old):
        new = None
        if(old is not None):
            new = EventArguments()
            if hasattr(old, 'judge_result'):
                new.judge_result = JudgeResultEvent.copy(old.judge_result)
        return new



class Vector2:
    x: float
    y: float

    def copy(old):
        new = None
        if(old is not None):
            new = Vector2()
            if hasattr(old, 'x'):
                new.x = old.x
            if hasattr(old, 'y'):
                new.y = old.y
        return new


class Wheel:
    left_speed: float
    right_speed: float

    def copy(old):
        new = None
        if(old is not None):
            new = Wheel()
            if hasattr(old, 'left_speed'):
                new.left_speed = old.left_speed
            if hasattr(old, 'right_speed'):
                new.right_speed = old.right_speed
        return new


class Robot:
    position: Vector2
    rotation: float
    wheel: Wheel

    def copy(old):
        new = None
        if(old is not None):
            new = Robot()
            if hasattr(old, 'position'):
                new.position = Vector2.copy(old.position)
            if hasattr(old, 'rotation'):
                new.rotation = old.rotation
            if hasattr(old, 'wheel'):
                new.wheel = Wheel.copy(old.wheel)
        return new


class Ball:
    position: Vector2

    def copy(old):
        new = None
        if(old is not None):
            new = Ball()
            if hasattr(old, 'position'):
                new.position = Vector2.copy(old.position)
        return new


class Field:
    self_robots: List[Robot]
    opponent_robots: List[Robot]
    ball: Ball
    tick: int

    def copy(old):
        new = None
        if(old is not None):
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
