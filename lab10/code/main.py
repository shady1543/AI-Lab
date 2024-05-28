import argparse
import matplotlib.pyplot as plt
import gym
from argument import dqn_arguments, pg_arguments


def parse():
    parser = argparse.ArgumentParser(description="FINAL-PROJECT")
    parser.add_argument('--train_pg', default=False, type=bool, help='whether train policy gradient')
    parser.add_argument('--train_dqn', default=True, type=bool, help='whether train DQN')

    # parser = dqn_arguments(parser)
    parser = pg_arguments(parser)
    args   = parser.parse_args()
    return args


def run(args):
    if args.train_pg:
        env_name = args.env_name
        env      = gym.make(env_name)
        from agent_dir.agent_pg import AgentPG
        agent    = AgentPG(env, args)
        agent.run()

    if args.train_dqn:
        env_name      = args.env_name
        env           = gym.make(env_name)
        from agent_dir.agent_dqn import AgentDQN
        agent         = AgentDQN(env, args)
        total_rewards = agent.run()
        draw(total_rewards)


def draw(total_rewards):
    plt.figure(figsize=(10, 5))
    plt.plot(total_rewards, label='Total Reward per Episode')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Reward vs. Episode for DQN Agent')
    plt.legend()
    plt.grid(True)
    plt.show()
    return


if __name__ == '__main__':
    args = parse()
    run(args)
