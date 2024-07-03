from Maze import Maze
import numpy as np

def my_search(maze):
    """
    深度优先搜索算法
    :param maze: 迷宫对象
    :return :到达目标点的路径 如：["u","u","r",...]
    """

    path = []
    # -----------------请实现你的算法代码--------------------------------------
    # 获取迷宫大小
    size = maze.maze_size
    # 记录节点是否被访问过
    visited = np.zeros((size, size), dtype=bool)

    def dfs(x, y):
        # 如果到达终点，返回True
        if (x, y) == maze.destination:
            return True
        visited[x, y] = True
        # 当前节点可以移动的方向
        cma = maze.can_move_actions((x, y))
        for direction in cma:
            dx, dy = maze.move_map[direction]
            # 下一个节点的坐标
            next_x, next_y = x + dx, y + dy
            # 如果下一个节点未被访问过，继续搜索
            if not visited[next_x, next_y]:
                path.append(direction)
                if dfs(next_x, next_y):
                    return True
                path.pop()  # 回溯
        return False

    # 从起点开始搜索
    start_x, start_y = maze.sense_robot()
    dfs(start_x, start_y)

    # -----------------------------------------------------------------------
    return path

maze = Maze(10)
path = my_search(maze)
print(path)
print(maze)