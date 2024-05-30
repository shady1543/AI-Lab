# 使用Q-Learning和SARSA解决迷宫问题

## 文件结构

- `code/`：代码文件夹。
- `Task.pdf`：任务描述。
- `Tutor.pptx`：教学课件。

## 算法原理

### Q-Learning

Q-Learning 是一种无模型的强化学习算法，通过学习动作值函数 $Q(s, a)$ 来指导代理在给定状态 $s$ 下选择最优动作 $a$。其核心思想是利用Bellman方程对Q值进行迭代更新，以逼近最优Q值函数 $Q^*(s, a)$。

#### 算法步骤

1. **初始化**：初始化 $Q(s, a)$ 对所有状态 $s$ 和动作 $a$ 为任意值（通常为零）。

2. **重复以下步骤，直到收敛**：
    
    - 从当前状态 $s$ 选择动作 $a$，通常使用 ε-greedy 策略。
    
    - 执行动作 $a$，观察即时奖励 $r$ 和下一个状态 $s'$。
    
    - 使用贝尔曼方程更新Q值函数：
      $$
      Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]
      $$
      其中， $\alpha$ 是学习率， $\gamma$ 是折扣因子， $\delta = r + \gamma \max_{a'} Q(s', a') - Q(s, a)$ 即时序差分误差。
    
    - 将状态更新为 $s \leftarrow s'$。

### SARSA 算法

SARSA（State-Action-Reward-State-Action）是一种基于在线策略的强化学习算法，与Q-Learning不同的是，SARSA更新Q值时使用的是实际执行的动作值，而不是估计的最优动作值。

#### 算法步骤

1. **初始化**：初始化 $Q(s, a)$ 对所有状态 $s$ 和动作 $a$ 为任意值（通常为零）。

2. **重复以下步骤，直到收敛**：
    - 从当前状态 $s$ 选择动作 $a$，通常使用 ε-greedy 策略。
    
    - 执行动作 $a$，观察即时奖励 $r$ 和下一个状态 $s'$。
    
    - 从状态 $s'$ 选择下一个动作 $a'$，通常使用相同的 ε-greedy 策略。
    
    - 更新Q值函数：
      $$
      Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma Q(s', a') - Q(s, a) \right]
      $$
      其中 $\delta = r + \gamma Q(s', a') - Q(s, a)$ 即时序差分误差。
    
    - 将状态和动作更新为 $s \leftarrow s'$， $a \leftarrow a'$​。

### 比较

- **策略性质**：Q-Learning 是一种离策略算法，因为更新时所用的 $\max_{a'} Q(s', a')$ 不依赖于当前策略；而SARSA是基于当前策略的在策略算法。
- **更新方式**：Q-Learning 使用的是下一状态的最优动作值来更新当前状态的Q值；SARSA使用的是实际选择的动作值来更新当前状态的Q值。

Q-Learning 通常可以收敛到最优策略，而 SARSA 在探索期间可能会更为稳定。

### 创新点

**多步学习**

参考函数 `n_steps_learn()`。