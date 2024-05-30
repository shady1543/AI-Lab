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
        """choose an action from q table."""
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
        """update the q table."""
        self.check_state_exist(s_)
        q_pre  = self.q_table.loc[s,a]
        # Qlearning的a'的选择采用的是贪心选择，直接接受最大值
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()
        else:
            q_target = r
        self.q_table.loc[s,a] += self.lr * (q_target - q_pre)

    def n_steps_learn(self, s, a, r, s_):
        """n-step learning optimization."""
        self.check_state_exist(s_)
        self.state_action_reward.append((s, a, r))

        if len(self.state_action_reward) >= self.n_steps:
            G = sum([self.gamma**i * self.state_action_reward[i][2] for i in range(self.n_steps)])
            if s_ != 'terminal':
                G += self.gamma**self.n_steps * self.q_table.loc[s_, :].max()
            
            s_n, a_n, _ = self.state_action_reward.pop(0)
            q_pre = self.q_table.at[s_n, a_n]
            self.q_table.at[s_n, a_n] += self.lr * (G - q_pre)
        
        if s_ == 'terminal':
            self.state_action_reward = []
        
        return

    def check_state_exist(self, state):
        """check the state."""
        # 检查当前状态是否在Q值表里，如果不在则补充
        if state not in self.q_table.index:
            self.q_table.loc[state] = [0] * len(self.actions)