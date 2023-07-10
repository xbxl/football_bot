"""
此文件用于定义机器人的一些底层基础动作
"""
#调用包，这几行不用管
from V5RPC import *
import math
import numpy as np
from GlobalVariable import *
"""
pid类的设定，具体原理详看pid相关讲解课程
pid_cal函数就是根据增量式pid原理，之前的误差 lasterror, pre_error，计算出一个用于调节轮速的值now_pid
"""
class PID:
    def __init__(self, proportion, integral, derivative, lasterror, pre_error):
        self.proportion = proportion    # 比例常数
        self.integral = integral    # 积分常数
        self.derivative = derivative    # 微分常数
        self.lastError = lasterror # 上一时刻的误差
        self.preError = pre_error # 两个时刻前的误差


    def pid_cal(self, nowPoint):
        now_error = 0 - nowPoint
        now_pid = (self.proportion * (now_error - self.lastError) + self.integral * now_error
                   + self.derivative * (now_error - 2 * self.lastError + self.preError))
        self.preError = self.lastError
        self.lastError = now_error
        return now_pid


class BaseRobot:
    def __init__(self):
        self.pid = PID(0.52, 0, 4.06, 0, 0)
        return
    pid: PID
    robot: Robot
    lastTargetX = 0# 机器人上一拍目标点y
    lastTargetY = 0  # 机器人上一拍目标点y
    lastRobotX = 0# 机器人上一拍位置坐标x
    lastRobotY = 0   # 机器人上一拍位置坐标y
    lastU = 0	 # pid控制变量U
    lastU1 = 0	 # pid控制变量U1
    lastRotation = 0# 机器人上一拍旋转角
    tick = GlobalVariable().tick # 拍数

    def update(self, env_robot: Robot):
        self.robot = env_robot# 把平台传给我们的Robot类机器人信息复制给我们自己定义的BaseRobot类中
        # 代码黄方假设，但vda是蓝方假设，所以把所有坐标反转，旋转角也反转，从而可以是赋的轮速不变从而达到相同效果
        self.robot.position.x = -self.robot.position.x
        self.robot.position.y = -self.robot.position.y
        self.robot.rotation = self.robot.rotation - 180
        if self.robot.rotation < -180:
            self.robot.rotation += 360

    def save_last_information(self, footBallNow_X, footBallNow_Y):	 # 保存机器人本拍信息，留作下一拍使用，可用于拓展保存更多信息
        self.lastRotation = self.robot.position
        if self.tick % 10 == 0:
            self.lastRobotX = self.robot.position.x
            self.lastRobotY = self.robot.position.y
        return

    def get_pos(self):   # 获取机器人位置
        return self.robot.position

    def get_last_pos(self):	 # 获取机器人上一拍位置
        last_pos: Vector2
        last_pos.x = self.lastRobotX
        last_pos.y = self.lastRobotY
        return last_pos

    def get_rotation(self):	 # 获取机器人旋转角
        return self.robot.rotation

    def get_left_wheel_velocity(self):	 # 获取机器人左轮速
        return self.robot.wheel.left_speed

    def get_right_wheel_velocity(self):	 # 获取机器人右轮速
        return self.robot.wheel.right_speed

    def set_wheel_velocity(self, vl, vr):	 # 直接赋左右轮速
        self.robot.wheel.left_speed = vl
        self.robot.wheel.right_speed = vr
    """
    moveto函数利用pid计算出一个差量self.pid_cal(angle_diff)，然后以此算出该赋的轮速并直接赋给双轮
    可以通过优化此函数来优化底层，如果只是上层策略开发不需要了解此函数
    """
    def moveto(self, tar_x, tar_y):  # pid跑位函数
        if self.tick == 1 or self.tick == 2 or self.tick == 3 or self.tick % 100 == 0:
            self.lastU = 0
            self.lastU1 = 0
        v_max = 125
        dx = tar_x - self.get_pos().x
        dy = tar_y - self.get_pos().y
        angle_to = 180 / math.pi * np.arctan2(dy, dx)
        angle_diff = self.get_rotation() - angle_to# 计算误差角
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360
        if math.fabs(angle_diff) < 85:
            self.lastU = self.lastU + self.pid.pid_cal(angle_diff)
            v_r = v_max + self.lastU
            v_l = v_max - self.lastU
        elif math.fabs(angle_diff) >= 90:
            angle_diff += 180
            if angle_diff > 180:
                angle_diff -= 360
            self.lastU = self.lastU + self.pid.pid_cal(angle_diff)
            v_r = -v_max + self.lastU
            v_l = -v_max - self.lastU
        else:
            v_r = 80
            v_l = -80
        self.set_wheel_velocity(v_l, v_r)


class DataLoader:
    def get_event(self, tick):  # 获得tick时刻的比赛状态
        return self.event_states[tick]

    def set_tick_state(self, tick, event_state):    # 设置此时的信息
        self.tick = tick
        self.event_states[tick] = event_state
    tick = 0
    event_states = [-1 for n in range(100000)]
