import random
import copy
import numpy as np
import torch
from torch import nn, optim
from agent_dir.agent import Agent


class QNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, inputs):
        out = torch.relu(self.fc1(inputs))
        out = torch.relu(self.fc2(out))
        out = self.fc3(out)
        return out


class ReplayBuffer:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = []
        self.position = 0
        self.priorities = np.zeros((buffer_size,), dtype=np.float32)
        self.max_priority = 1.0
        return

    def __len__(self):
        return len(self.buffer)

    def push(self, *transition):
        if len(self.buffer) < self.buffer_size:
            self.buffer.append(None)
        self.buffer[self.position] = transition
        self.priorities[self.position] = self.max_priority
        self.position = (self.position + 1) % self.buffer_size
        return

    def sample(self, batch_size):
        priorities = self.priorities[:len(self.buffer)]
        probs = priorities ** 0.6
        probs /= probs.sum()
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        batch = [self.buffer[idx] for idx in indices]
        return batch, indices
    
    def update_priorities(self, indices, priorities):
        self.priorities[indices] = priorities
        self.max_priority = max(self.max_priority, np.max(priorities))
        return
    
    def clean(self):
        self.buffer = []
        self.position = 0
        return


class AgentDQN(Agent):
    def __init__(self, env, args):
        """
        Initialize every things you need here.
        For example: building your model
        """
        super(AgentDQN, self).__init__(env)
        self.env = env
        self.args = args
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = QNetwork(env.observation_space.shape[0], 256, env.action_space.n).to(self.device)
        self.target_network = copy.deepcopy(self.q_network)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=1e-3)
        self.replay_buffer = ReplayBuffer(8000)
        self.minimal_size = 200
        self.batch_size = 64
        self.gamma = 0.98
        self.epsilon = 0.9
        self.epsilon_decay = 0.95
        self.epsilon_min = 0.001
        self.update_target_every = 40
        self.steps = 0
        return
    
    def init_game_setting(self):
        """

        Testing function will call this function at the begining of new game
        Put anything you want to initialize if necessary

        """
        ##################
        # YOUR CODE HERE #
        ##################
        pass

    def train(self):
        """
        Implement your training algorithm here
        """
        if len(self.replay_buffer) < self.minimal_size:
            return

        transitions, indices = self.replay_buffer.sample(self.batch_size)
        batch = list(zip(*transitions))

        states = torch.tensor(np.array(batch[0]), dtype=torch.float32).to(self.device)
        actions = torch.tensor(batch[1], dtype=torch.int64).to(self.device)
        rewards = torch.tensor(batch[2], dtype=torch.float32).to(self.device)
        next_states = torch.tensor(np.array(batch[3]), dtype=torch.float32).to(self.device)
        dones = torch.tensor(batch[4], dtype=torch.float32).to(self.device)

        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        # next_q_values = self.target_network(next_states).max(1)[0] # DQN
        next_actions = self.target_network(next_states).max(1)[1].unsqueeze(-1) # DDQN
        next_q_values = self.target_network(next_states).gather(1, next_actions).squeeze(1) # DDQN
        expected_q_values = rewards + (self.gamma * next_q_values * (1 - dones))

        loss = nn.MSELoss()(q_values, expected_q_values.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.replay_buffer.update_priorities(indices, (q_values - expected_q_values).abs().cpu().detach().squeeze(-1).numpy())

        if self.steps % self.update_target_every == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        return

    def make_action(self, observation, test=True):
        """
        Return predicted action of your agent
        Input:observation
        Return:action
        """
        if test or random.random() > self.epsilon:
            observation = torch.tensor(observation, dtype=torch.float32).unsqueeze(0).to(self.device)
            with torch.no_grad():
                action = self.q_network(observation).argmax().item()
        else:
            action = self.env.action_space.sample()
        return action

    def run(self):
        """
        Implement the interaction between agent and environment here
        """
        total_rewards = []
        for episode in range(100):
            state = self.env.reset()
            total_reward = 0
            done = False
            while not done:
                action = self.make_action(state, test=False)
                next_state, reward, done, _ = self.env.step(action)
                self.replay_buffer.push(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                self.train()
                self.steps += 1

            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            total_rewards.append(total_reward)
            print(f"Episode {episode + 1:3d}, Total Reward: {total_reward}, Epsilon: {self.epsilon:.6f}")
        return total_rewards