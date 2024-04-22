import multiprocessing
import random
import time
import logging
import os
import numpy as np
import matplotlib.pyplot as plt

from multiprocessing import Pool


class GeneticAlgTSP:
    def __init__(self, filename):
        self.name = filename.split('/')[2].split(".")[0]
        self.cities = self.load_cities(filename)
        self.population_size = 2
        self.population = self.add_population(self.population_size)
        self.distances = []
        self.depth = 3
        self.check_dir()
        self.setup_logging()

    def check_dir(self):
        if not os.path.exists(f'./results/{self.name}'):
            os.makedirs(f'./results/{self.name}')

    def setup_logging(self):
        logging.basicConfig(filename=f'./results/{self.name}/log.txt',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def logging(self, msg):
        logging.info(msg)
        print(msg)

    def load_cities(self, filename):
        cities = []
        start = False
        with open(filename, 'r') as file:
            for line in file.readlines():
                if line == 'NODE_COORD_SECTION\n' and start is False:
                    start = True
                    continue

                parts = line.strip().split()
                if len(parts) == 3 and start:
                    _, x, y = parts
                    cities.append((float(x), float(y)))
        return np.array(list(set(cities)))

    def add_population(self, population_size):
        n = len(self.cities)
        population = [random.sample(range(1, n + 1), n) for _ in range(population_size)]
        return population

    def crossover_and_mutation(self, parents):
        # 交叉
        child1, child2 = self.pmx_crossover(parents[0].copy(), parents[1].copy())
        # 倒置变异
        child1 = self.inversion_mutation(child1)
        child2 = self.inversion_mutation(child2)
        # 交换变异
        child1 = self.swap_mutation(child1)
        child2 = self.swap_mutation(child2)

        return child1, child2

    def calculate_distance(self, individual):
        total_distance = 0
        for i in range(len(individual)):
            city_from = individual[i - 1]
            city_to = individual[i]
            distance = np.linalg.norm(self.cities[city_from - 1] - self.cities[city_to - 1])
            total_distance += distance
        return total_distance

    def calculate_fitness(self, individual):
        total_distance = self.calculate_distance(individual)
        return 1 / total_distance

    def select_parents(self, population):
        # 排序
        # return population[0], population[1]

        # 轮盘赌
        fitness_values = [self.calculate_fitness(individual) for individual in population]
        total_fitness = sum(fitness_values)
        selection_probs = [fitness / total_fitness for fitness in fitness_values]
        p1, p2 = np.random.choice(len(population), 2, p=selection_probs)
        return population[p1], population[p2]

    def pmx_crossover(self, p1, p2):
        length = len(p1)
        # 随机生成两个在0~length-1范围的下标s,t，确保s<t
        s, t = sorted(random.sample(range(length), 2))

        # 交换p1,p2在s~t的部分
        new_p1 = p1[:s] + p2[s:t + 1] + p1[t + 1:]
        new_p2 = p2[:s] + p1[s:t + 1] + p2[t + 1:]

        # 存储映射关系
        mapping_p1_p2 = {}
        for i in range(s, t + 1):
            mapping_p1_p2[p1[i]] = p2[i]

        # 处理链式映射
        def apply_mapping(seq, mapping, s, t):
            new_seq = seq
            for i in range(len(seq)):
                if not (s <= i <= t):
                    while new_seq[i] in mapping.values():
                        # 查找链式映射直到找到一个不在交换段内的值
                        for k, v in mapping.items():
                            if v == new_seq[i]:
                                new_seq[i] = k
                                break
            return new_seq

        new_p1 = apply_mapping(new_p1, mapping_p1_p2, s, t)
        # 反转映射关系，用于第二个子代
        mapping_p2_p1 = {v: k for k, v in mapping_p1_p2.items()}
        new_p2 = apply_mapping(new_p2, mapping_p2_p1, s, t)

        return new_p1, new_p2

    def inversion_mutation(self, individual):
        length = len(individual)
        # 随机生成两个在0~length-1范围的下标s,t，确保s<t
        s, t = sorted(random.sample(range(length), 2))
        # 将s,t中间部分倒置
        individual[s:t + 1] = individual[s:t + 1][::-1]
        return individual

    def swap_mutation(self, individual):
        # 选择两个不同的随机索引
        idx1, idx2 = random.sample(range(len(individual)), 2)
        # 交换这两个索引对应的值
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual

    def iterate(self, num_iterations):
        best_dist = float('inf')
        stag_count = 0

        with Pool(processes=multiprocessing.cpu_count()) as pool:
            for iteration in range(num_iterations):
                start_time = time.time()

                # 选择父母并进行交叉变异
                parent_pairs = [self.select_parents(self.population) for _ in range(len(self.population) // 2)]
                children = pool.map(self.crossover_and_mutation, parent_pairs)
                children = [child for pair in children for child in pair]  # 展平列表

                # 更新种群
                self.population += children
                self.population.sort(key=self.calculate_fitness, reverse=True)
                self.population = self.population[:self.population_size]

                sol = self.select_best_solution()
                dist = self.calculate_distance(sol)

                # 检查是否更新了最优解
                if dist < best_dist:
                    best_dist = dist
                    stag_count = 0
                    self.distances.append(dist)
                else:
                    stag_count += 1
                    self.distances.append(dist)

                # 扩大搜索范围
                if len(self.cities) * 20 > stag_count >= len(self.cities) * 10 and self.depth:
                    self.depth -= 1
                    # 扩大种群数量
                    self.population_size *= 2
                    self.population += self.add_population(self.population_size - len(self.population))
                    # 头部变异
                    for i in range(1, self.population_size):
                        self.population[i] = self.swap_mutation(self.population[i])

                    self.logging(f'Population size doubled to: {self.population_size}')
                    self.logging(f'Depth: {3 - self.depth}')

                    stag_count = 0

                # 早停
                if stag_count >= len(self.cities) * 20:
                    self.logging(f'Early stopping: No improvement in the last {len(self.cities) * 20} iterations.')
                    break

                end_time = time.time()
                self.logging(f'Iteration: {iteration + 1}, '
                             f'Time: {end_time - start_time:.2f} seconds, '
                             f'Best Distance: {dist}')

                if iteration % (num_iterations / 10) == 0:
                    self.logging(f'Results @ iteration {iteration}:\n'
                                 f'Solution = {sol}\n'
                                 f'Distance = {dist}\n')

            self.plot_distances()

            self.logging(f'---- BEGIN 2-OPTIMIZATION ----')
            self.logging(f'Before 2-opt:\n'
                         f'Best Solution = {sol}\n'
                         f'Best Distance = {dist}\n')
            two_opt_sol = self.two_opt(sol)
            two_opt_dist = self.calculate_distance(two_opt_sol)
            self.logging(f'After 2-opt:\n'
                         f'Best Solution = {two_opt_sol}\n'
                         f'Best Distance = {two_opt_dist}\n')

            self.logging(f'---- BEGIN 3-OPTIMIZATION ----')
            self.logging(f'Before 3-opt:\n'
                         f'Best Solution = {two_opt_sol}\n'
                         f'Best Distance = {two_opt_dist}\n')
            three_opt_sol = self.three_opt(two_opt_sol)
            three_opt_dist = self.calculate_distance(three_opt_sol)
            self.logging(f'After 3-opt:\n'
                         f'Best Solution = {three_opt_sol}\n'
                         f'Best Distance = {three_opt_dist}\n')

            self.plot_path(three_opt_sol)

            return three_opt_sol, three_opt_dist

    def select_best_solution(self):
        best_fitness = float('-inf')
        best_individual = None
        for individual in self.population:
            fitness = self.calculate_fitness(individual)
            if fitness > best_fitness:
                best_fitness = fitness
                best_individual = individual
        return best_individual

    def two_opt(self, route):
        best = route
        improved = True
        while improved:
            improved = False
            for i in range(0, len(route) - 1):
                for j in range(i + 1, len(route)):
                    new_route = route[:i] + route[i:j][::-1] + route[j:]
                    new_dist = self.calculate_distance(new_route)
                    prev_dist = self.calculate_distance(best)
                    if new_dist < prev_dist:
                        self.logging(f'Route optimized to: {new_route}\n'
                                     f'With distance: {new_dist}')
                        best = new_route
                        improved = True
            route = best
        return best

    def three_opt(self, route):
        # 如果城市太多，放弃3-opt优化
        if len(self.cities) > 500:
            return route

        best = route
        improved = True
        while improved:
            improved = False
            for i in range(0, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    for k in range(j + 1, len(route)):
                        # A: route[:i], B: route[i:j], C: route[j:k] D:route[k:]
                        new_routes = [
                            route[:i] + route[i:j] + route[j:k] + route[k:],
                            route[:i] + route[i:j][::-1] + route[j:k] + route[k:],
                            route[:i] + route[i:j] + route[j:k][::-1] + route[k:],
                            route[:i] + route[i:j][::-1] + route[j:k][::-1] + route[k:],
                            route[:i] + route[j:k] + route[i:j] + route[k:],
                            route[:i] + route[j:k] + route[i:j][::-1] + route[k:],
                            route[:i] + route[j:k][::-1] + route[i:j] + route[k:],
                            route[:i] + route[j:k][::-1] + route[i:j][::-1] + route[k:],
                        ]
                        for new_route in new_routes:
                            new_dist = self.calculate_distance(new_route)
                            best_dist = self.calculate_distance(best)
                            if new_dist < best_dist:
                                best = new_route
                                improved = True
                                self.logging(f'Route optimized to: {new_route}\n'
                                             f'With distance: {new_dist}')
                                break
                        if improved:
                            break
                    if improved:
                        break
            route = best
        return best

    def plot_path(self, path):
        path = path + [path[0]]
        coordinates = np.array([self.cities[i - 1] for i in path])

        plt.figure(figsize=(10, 5))
        plt.rc('font', family='Times New Roman')
        plt.plot(coordinates[:, 0], coordinates[:, 1], 'o-', markersize=5, linewidth=1, label='Path')
        plt.plot(coordinates[0, 0], coordinates[0, 1], 'ro', label='Start')

        plt.title("Best Path")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.legend()
        plt.savefig(f'./results/{self.name}/best_path.png')
        plt.show()

    def plot_distances(self):
        plt.figure(figsize=(10, 5))
        plt.rc('font', family='Times New Roman')
        plt.plot(self.distances, label='Best Distance')
        plt.xlabel('Iteration')
        plt.ylabel('Distance')
        plt.title('Distance vs. Iteration')
        plt.legend()
        plt.savefig(f'./results/{self.name}/distance_vs_iteration.png')
        plt.show()


def main():
    start = time.time()
    ga_tsp = GeneticAlgTSP("./data/uy734.tsp")
    best_solution, best_distance = ga_tsp.iterate(len(ga_tsp.cities) * 100)
    end = time.time()
    print('---- FINAL RESULTS ----')
    print(f'Best Solution: {best_solution}')
    print(f'Minimum Distance: {best_distance}')
    print(f'Execute Time: {end - start}')


if __name__ == '__main__':
    main()
