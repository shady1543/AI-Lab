import numpy as np
import pandas as pd


class QLearning:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.99):
        self.actions = actions  # a list
        self.lr      = learning_rate
        self.gamma   = reward_decay
        self.epsilon = e_greedy

        ''' build q table'''
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation):
        ''' choose action from q table '''
        self.check_state_exist(observation)
        # 以一定的概率选择Q值最大的action
        if np.random.uniform() < self.epsilon:
            # 可能出现Q值相同的，则在Q值相同且为最大值的action中随机选择
            state_action = self.q_table.loc[observation, :]
            action       = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            action       = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        ''' update q table '''
        self.check_state_exist(s_)
        q_pre  = self.q_table.loc[s,a]
        # Qlearning的a'的选择采用的是贪心选择，直接接受最大值
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()
        else:
            q_target = r
        self.q_table.loc[s,a] += self.lr * (q_target - q_pre)

    def check_state_exist(self, state):
        ''' check state '''
        # 检查当前状态是否在Q值表里，如果不在则补充
        if state not in self.q_table.index:
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )