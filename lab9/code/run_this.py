"""
Reinforcement learning maze example.

Red rectangle:          explorer.
Black rectangles:       hells       [reward = -1].
Yellow bin circle:      paradise    [reward = +1].
All other states:       ground      [reward = 0].

This script is the main part which controls the update method of this example.
"""

from maze_env import Maze
from RL_q_learning import QLearning
from RL_sarsa import Sarsa
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif']    = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False       # 用来正常显示符号


def update():
    flag   = []
    number = []
    for episode in range(100):
        # initial observation
        observation = env.reset()
        step        = 0
        while True:
            # fresh env
            '''Renders policy once on environment. Watch your agent play!'''
            env.render()

            '''
            RL choose action based on observation
            e.g: action = RL.choose_action(str(observation))
            '''
            action = RL.choose_action(str(observation))

            # RL take action and get next observation and reward
            observation_, reward, done = env.step(action)
            step += 1
            '''
            RL learn from this transition
            e.g: RL.learn(str(observation), action, reward, str(observation_), is_lambda=True)
                 RL.learn(str(observation), action, reward, str(observation_), is_lambda_return=True)
            '''
            RL.learn(str(observation), action, reward, str(observation_))

            # swap observation

            observation = observation_

            # break while loop when end of this episode
            if done:
                print('Episode', episode, end=' ')
                if reward == 1:
                    flag.append('green')
                    number.append(step)
                    print("Success! Number of steps: ", step)
                else:
                    flag.append('red')
                    number.append(step)
                    print("Fail! Number of steps: ", step)
                break

    # end of game
    print('game over')
    print(RL.q_table)
    env.destroy()

    '''
    画出迭代结果和迭代次数的关系曲线图
    '''
    plt.title('Result analysis', fontsize=20)
    plt.xlabel('iteration times', fontsize=20)
    plt.ylabel('number of steps', fontsize=20)
    plt.scatter(np.arange(100), number, c=flag)
    plt.show()


if __name__ == "__main__":
    env = Maze()

    '''
    build RL Class
    RL = QLearning(actions=list(range(env.n_actions)))
    RL = Sarsa(actions=list(range(env.n_actions)))
    '''

    RL = QLearning(actions=list(range(env.n_actions)))

    # RL = Sarsa(actions=list(range(env.n_actions)))

    env.after(100, update)
    env.mainloop()

