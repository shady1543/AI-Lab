import numpy as np
import pandas as pd


class Sarsa:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.95):
        self.actions = actions  # a list
        self.lr      = learning_rate
        self.gamma   = reward_decay
        self.epsilon = e_greedy

        ''' build q table'''
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation):
        ''' choose action from q table '''
        self.check_state_exist(observation)
        if np.random.rand() < self.epsilon:
            state_action = self.q_table.loc[observation, :]
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_):
        ''' update q table '''
        self.check_state_exist(s_)
        # 和Q_learning的区别，这里的a_是采用epsilon贪心选择
        a_     = self.choose_action(s_)
        q_pre  = self.q_table.loc[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, a_]
        else:
            q_target = r
        self.q_table.loc[s, a] += self.lr * (q_target - q_pre)

    def n_steps_learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        self.state_action_reward.append((s, a, r))

        if len(self.state_action_reward) >= self.n_steps:
            G = sum([self.gamma**i * self.state_action_reward[i][2] for i in range(self.n_steps)])
            if s_ != 'terminal':
                s_n, a_n = s_, self.choose_action(s_)
                G += self.gamma**self.n_steps * self.q_table.at[s_n, a_n]
            
            s_n, a_n, _ = self.state_action_reward.pop(0)
            q_pre = self.q_table.at[s_n, a_n]
            self.q_table.at[s_n, a_n] += self.lr * (G - q_pre)
        
        if s_ == 'terminal':
            self.state_action_reward = []
        
        return

    def check_state_exist(self, state):
        ''' check state '''
        if state not in self.q_table.index:
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )