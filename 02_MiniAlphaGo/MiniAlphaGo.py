import random
import math
import copy
# 导入黑白棋文件
from game import Game  


class RandomPlayer:
    """
    随机玩家, 随机返回一个合法落子位置
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color
        

    def random_choice(self, board):
        """
        从合法落子位置中随机选一个落子位置
        :param board: 棋盘
        :return: 随机合法落子位置, e.g. 'A1' 
        """
        # 用 list() 方法获取所有合法落子位置坐标列表
        action_list = list(board.get_legal_actions(self.color))

        # 如果 action_list 为空，则返回 None,否则从中选取一个随机元素，即合法的落子坐标
        if len(action_list) == 0:
            return None
        else:
            return random.choice(action_list)

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))
        action = self.random_choice(board)
        return action

class HumanPlayer:
    """
    人类玩家
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color
    

    def get_move(self, board):
        """
        根据当前棋盘输入人类合法落子位置
        :param board: 棋盘
        :return: 人类下棋落子位置
        """
        # 如果 self.color 是黑棋 "X",则 player 是 "黑棋"，否则是 "白棋"
        if self.color == "X":
            player = "黑棋"
        else:
            player = "白棋"

        # 人类玩家输入落子位置，如果输入 'Q', 则返回 'Q'并结束比赛。
        # 如果人类玩家输入棋盘位置，e.g. 'A1'，
        # 首先判断输入是否正确，然后再判断是否符合黑白棋规则的落子位置
        while True:
            action = input(
                    "请'{}-{}'方输入一个合法的坐标(e.g. 'D3'，若不想进行，请务必输入'Q'结束游戏。): ".format(player,
                                                                                 self.color))

            # 如果人类玩家输入 Q 则表示想结束比赛
            if action == "Q" or action == 'q':
                return "Q"
            else:
                row, col = action[1].upper(), action[0].upper()

                # 检查人类输入是否正确
                if row in '12345678' and col in 'ABCDEFGH':
                    # 检查人类输入是否为符合规则的可落子位置
                    if action in board.get_legal_actions(self.color):
                        return action
                else:
                    print("你的输入不合法，请重新输入!")


class AIPlayer:
    """
    AI 玩家
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """

        self.color = color

    def get_move(self, board):
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))

#-----------------AI玩家的代码实现-----------------
        class node_state:
            def __init__(self, board, color):
                self.board = board
                self.color = color
            def move(self, action):
                self.board._move(action, self.color)
                self.color = "X" if self.color == "O" else "O"
        # 蒙特卡洛树搜索节点，储存节点信息
        class Node:
            def __init__(self, state, action=None, parent=None):
                self.state = state
                self.curr_action = action
                self.parent = parent    # 父节点
                self.children = []      # 子节点
                self.wins = 0           # 超过对手的棋子数
                self.visits = 0         # 访问次数
                self.uct = 0            # UCT值
                if self.state is not None:
                    self.untried_actions = list(self.state.board.get_legal_actions(self.state.color))    # 未尝试的动作
                else:
                    self.untried_actions = []

            # 利用UCT算法选择最佳的子节点
            def UCTSelectChild(self):
                # UCT算法：子节点赢的棋子数/子节点访问次数 + √(2ln(当前节点访问次数)/子节点访问次数)，选择最大值 
                s = max(self.children, key=lambda child: child.uct)
                return s
            
            # 添加子节点
            def add_child(self, a):
                # 添加子节点，从untriedActions中删除此action，添加为新的节点，a为action，s为新的状态，并返回新的节点
                n = Node(action=a, parent=self, state=copy.deepcopy(self.state).move(a))
                n.parent = self
                self.untried_actions.remove(a)
                self.children.append(n)
                return n
            
            # 更新节点信息，visits，wins，uct
            def update(self, result):
                self.visits += 1
                self.wins += result
                if self.parent and self.parent.visits != 0:
                    self.uct = self.wins / self.visits + 2 * math.sqrt(2 * math.log(self.parent.visits) / self.visits)
                else:
                    self.uct = self.wins / self.visits

        # 根节点
        sim_board = copy.deepcopy(board)
        root_state = node_state(sim_board, self.color)        
        root_node = Node(state=root_state)

        for _ in range(100):
            node = root_node                    # 从根节点开始
            state = copy.deepcopy(root_state)    # 复制当前棋盘状态
            # 选择
            while node.untried_actions == [] and node.children != []:
                node = node.UCTSelectChild()
                state.move(node.curr_action)
            # 扩展
            if node.untried_actions != []:
                a = random.choice(node.untried_actions)
                state.move(a)
                node = node.add_child(a)
            # 模拟
            while list(state.board.get_legal_actions(state.color)):
                a = random.choice(list(state.board.get_legal_actions(state.color)))
                state.move(a)
            # 回溯
            while node != None:
                win_diff = state.board.count(self.color) - state.board.count('O' if self.color == 'X' else 'X')
                node.update(win_diff)
                node = node.parent
        return root_node.UCTSelectChild().curr_action                                                               




#-----------------AI玩家的代码实现-----------------

        # return action


# AI玩家黑棋初始化
black_player = AIPlayer("X")

# 随机玩家白棋初始化
white_player = RandomPlayer("O")

# 游戏初始化，第一个玩家是黑棋，第二个玩家是白棋
game = Game(black_player, white_player)

# 开始下棋
game.run()