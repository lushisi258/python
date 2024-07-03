from QRobot import QRobot
import random

"""
题目要求:  编程实现 DQN 算法在机器人自动走迷宫中的应用
输入: 由 Maze 类实例化的对象 maze
必须完成的成员方法：train_update()、test_update()
补充：如果想要自定义的参数变量，在 \_\_init\_\_() 中以 `self.xxx = xxx` 创建即可
"""

class Robot(QRobot):

    def __init__(self, maze):
        """
        初始化 Robot 类
        :param maze:迷宫对象
        """
        super(Robot, self).__init__(maze)
        self.maze = maze

    def train_update(self):
        """
        以训练状态选择动作并更新Deep Q network的相关参数
        :return :action, reward 如："u", -1
        """

        action, reward = "u", -1.0

        # -----------------请实现你的算法代码--------------------------------------

        self.state = self.maze.sense_robot() # 获取机器人当初所处迷宫位置

        # 检索Q表，如果当前状态不存在则添加进入Q表
        if self.state not in self.q_table:
            self.q_table[self.state] = {a: 0.0 for a in self.valid_action}

        action = random.choice(self.valid_action) if random.random() < self.epsilon else max(self.q_table[self.state], key=self.q_table[self.state].get) # action为机器人选择的动作
        reward = self.maze.move_robot(action) # 以给定的方向移动机器人,reward为迷宫返回的奖励值
        next_state = self.maze.sense_robot() # 获取机器人执行指令后所处的位置

        # 检索Q表，如果当前的next_state不存在则添加进入Q表
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.valid_action}

        # 更新 Q 值表
        current_r = self.q_table[self.state][action]
        update_r = reward + self.gamma *float(max(self.q_table[next_state].values()))
        self.q_table[self.state][action] = self.alpha * self.q_table[self.state][action] +(1 - self.alpha) * (update_r - current_r)
        self.epsilon *= 0.5 # 衰减随机选择动作的可能性
        return action, reward

        # -----------------------------------------------------------------------

        return action, reward
