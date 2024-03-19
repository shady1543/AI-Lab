"""
Project: ResolutionFOL.
Author : xiezx (stuID:22336261)
Time   : 24-03-15
"""
import re


class ResolutionFOL:
    def __init__(self):
        pass

    def __call__(self, KB):
        """
        主推理逻辑。执行归结推理算法，从知识库KB中推导出结论。

        参数:
        - KB: 知识库，一个包含逻辑子句的集合。

        返回值:
        - 步骤列表，记录了归结推理的每一步。
        """
        self.steps = []
        self.new_clauses = set()
        self.resolved_pairs = set()
        self.clause_to_step = {}
        self.clauses = list(KB)
        # 为每个子句分配一个初始步骤编号
        self.clause_to_step = {clause: str(i + 1) for i, clause in enumerate(self.clauses)}

        # 记录知识库中的每个子句作为初始步骤
        for clause in self.clauses:
            self.steps.append(f"{self.clause_to_step[clause]} {clause}")

        # 不断尝试归结，直到无法进一步归结或推导出空子句
        while True:
            possible_resolutions = []  # 存储可能的归结结果
            for i, clause1 in enumerate(self.clauses):
                for j, clause2 in enumerate(self.clauses[i + 1:], start=i + 1):
                    # 检查两个子句是否可以归结，并未被之前归结过
                    if (i, j) not in self.resolved_pairs and self.can_resolve(clause1, clause2)[0]:
                        self.resolved_pairs.add((i, j))  # 标记为已归结
                        _, predicates_to_resolve = self.can_resolve(clause1, clause2)
                        # 尝试合一互补的谓词对
                        substitutions = self.apply_mgu(predicates_to_resolve[0], predicates_to_resolve[1])
                        unified = '{' + ', '.join(
                            [f"{k}={v}" for k, v in substitutions.items()]) + '}' if substitutions else ''
                        # 应用替换，生成新的子句
                        clause1_substituted = self.apply_substitutions_to_clause(clause1, substitutions)
                        clause2_substituted = self.apply_substitutions_to_clause(clause2, substitutions)
                        # 生成归结结果
                        resolvents = set(clause1_substituted + clause2_substituted) - set(
                            self.apply_substitutions_to_clause(predicates_to_resolve, substitutions))
                        resolvents = tuple(sorted(resolvents, key=lambda x: x.replace('~', '')))

                        i_formatted = self.format_clause_index(clause1, clause1.index(predicates_to_resolve[0]),
                                                               len(clause1))
                        j_formatted = self.format_clause_index(clause2, clause2.index(predicates_to_resolve[1]),
                                                               len(clause2))
                        step_str = f"R[{i_formatted},{j_formatted}]{unified} = {resolvents}"
                        # 如果归结结果为空子句，推理成功
                        if not resolvents:
                            self.steps.append(f"{len(self.steps) + 1} {step_str}")
                            return self.steps  # 返回推理步骤
                        possible_resolutions.append((step_str, resolvents))

            # 如果没有新的归结结果，结束推理
            if not possible_resolutions:
                break

            # 将新的归结结果加入知识库，并记录步骤
            for step_str, resolvents in possible_resolutions:
                if resolvents not in set(self.clauses) and resolvents not in self.new_clauses:
                    self.new_clauses.add(resolvents)
                    self.steps.append(f"{len(self.steps) + 1} {step_str}")
                    self.clause_to_step[resolvents] = str(len(self.steps))

            self.clauses.extend(self.new_clauses)  # 更新知识库
            self.new_clauses.clear()

        return self.steps  # 返回所有推理步骤

    def is_variable(self, term):
        """
        使用正则表达式判断给定的字符串是否表示一个变量。

        参数:
        - term: 一个字符串，待判断是否为变量的项。

        返回值:
        - 如果`term`符合变量的定义，则返回True；否则返回False。
        """
        # 使用正则表达式匹配小写字母t到z之间的1到2个字符，判断是否为变量
        return re.match(r'^[t-z]{1,2}$', term) is not None

    def parse_predicate(self, predicate):
        """
        解析逻辑谓词字符串，提取谓词名称和参数列表。

        参数:
        - predicate: 字符串，表示逻辑谓词的字符串。

        返回值:
        - 元组，包含两个元素：谓词名称（字符串）和参数列表（字符串列表）。
          如果谓词被否定，谓词名称将包含否定符号(~)。
        """
        negation = False

        # 检查谓词是否以否定符号(~)开头
        if predicate.startswith('~'):
            negation = True
            predicate = predicate[1:]
        name_end = predicate.find('(')
        name = predicate[:name_end]
        # 如果谓词被否定，将否定符号(~)添加到谓词名称前
        if negation:
            name = '~' + name
        # 分割圆括号内的字符串，得到参数列表
        args = predicate[name_end + 1:-1].split(',')

        return (name, args)

    def apply_mgu(self, predicate1, predicate2):
        """
        应用最一般合一（Most General Unifier, MGU）算法，计算两个谓词的合一替换。

        参数:
        - predicate1: 字符串，表示第一个谓词的逻辑表达式。
        - predicate2: 字符串，表示第二个谓词的逻辑表达式。

        返回值:
        - 字典，包含合一替换，其中键是变量，值是替换后的表达式；
          如果两个谓词无法合一，则返回None。
        """
        _, args1 = self.parse_predicate(predicate1)
        _, args2 = self.parse_predicate(predicate2)

        substitutions = {}
        for arg1, arg2 in zip(args1, args2):
            if arg1 == arg2:
                continue
            # 处理嵌套谓词或函数的合一
            if '(' in arg1 and '(' in arg2:
                inner_substitutions = self.apply_mgu(arg1, arg2)
                if inner_substitutions is None:
                    return None  # 嵌套结构无法合一
                substitutions.update(inner_substitutions)
            elif self.is_variable(arg1) and self.is_variable(arg2):
                return None  # 不允许变量替换变量
            elif self.is_variable(arg1):
                substitutions[arg1] = arg2  # 变量替换为表达式
            elif self.is_variable(arg2):
                substitutions[arg2] = arg1  # 变量替换为表达式
            else:
                return None  # 常量之间冲突，无法合一

        return substitutions

    def can_resolve(self, clause1, clause2):
        """
        检查两个子句是否可以通过归结来解决，即是否存在互补的谓词对。

        参数:
        - clause1: 子句1，包含多个逻辑谓词的元组。
        - clause2: 子句2，包含多个逻辑谓词的元组。

        返回值:
        - 布尔值和谓词对元组：如果可以解决，则返回True和可归结的谓词对；否则返回False和空元组。
        """
        for pred1 in clause1:
            for pred2 in clause2:
                name1, args1 = self.parse_predicate(pred1)
                name2, args2 = self.parse_predicate(pred2)

                # 检查谓词对是否互补
                if (name1.startswith('~') != name2.startswith('~')) and (name1.lstrip('~') == name2.lstrip('~')):
                    substitutions = self.apply_mgu(pred1, pred2)
                    # 如果找到有效的合一替换，则认为这两个子句可以归结
                    if substitutions is not None:
                        return True, (pred1, pred2)
        # 如果没有找到可以归结的互补谓词对，返回False和空元组
        return False, ()

    def apply_substitutions_to_clause(self, clause, substitutions):
        """
        在一个子句中应用变量替换。

        参数:
        - clause: 包含多个逻辑谓词的元组，代表一个逻辑子句。
        - substitutions: 一个字典，其中键是变量名，值是替换后的值或表达式。

        返回值:
        - 元组，包含应用了替换的新子句。
        """
        new_clause = []
        for predicate in clause:
            name, args = self.parse_predicate(predicate)
            new_args = []
            for arg in args:
                # 应用每个替换规则，只替换完整的变量名
                for var, sub in substitutions.items():
                    arg = re.sub(r'\b' + var + r'\b', sub, arg)
                new_args.append(arg)
            # 根据谓词是否否定来构建新的谓词表达式
            new_predicate = f"{name[1:] if name.startswith('~') else name}({','.join(new_args)})"
            if name.startswith('~'):
                new_predicate = f"~{new_predicate}"
            new_clause.append(new_predicate)
        return tuple(new_clause)

    def format_clause_index(self, clause, predicate_index, total_predicates):
        """
        格式化子句索引。

        参数:
        - clause: 子句，表示当前处理的逻辑子句。
        - predicate_index: 整数，表示在子句中的谓词索引（从0开始）。
        - total_predicates: 整数，表示子句中总的谓词数量。

        返回值:
        - 字符串，表示格式化后的子句索引。如果子句中只有一个谓词，则返回基础索引；
          如果子句包含多个谓词，则返回基础索引加上谓词的特定字母标识（如1a, 1b等）。
        """
        base_index = self.clause_to_step[clause]
        # 子句中有多个谓词时，添加字母标识区分不同谓词
        if total_predicates > 1:
            return f"{base_index}{chr(97 + predicate_index)}"
        # 子句中只有一个谓词时，直接返回基础索引
        return base_index


solver = ResolutionFOL()

KB1 = {('GradStudent(sue)',),
       ('~GradStudent(x)', 'Student(x)'),
       ('~Student(x)', 'HardWorker(x)'),
       ('~HardWorker(sue)',)}

print('--- Test case # 1 ---')
resolution_steps1 = solver(KB1)
for step in resolution_steps1:
    print(step)

KB2 = {
    ('A(tony)',),
    ('A(mike)',),
    ('A(john)',),
    ('L(tony,rain)',),
    ('L(tony,snow)',),
    ('~A(x)', 'S(x)', 'C(x)'),
    ('~C(y)', '~L(y,rain)'),
    ('L(z,snow)', '~S(z)'),
    ('~L(tony,u)', '~L(mike,u)'),
    ('L(tony,v)', 'L(mike,v)'),
    ('~A(w)', '~C(w)', 'S(w)')}

print('--- Test case # 2 ---')
resolution_steps2 = solver(KB2)
for step in resolution_steps2:
    print(step)

KB3 = {('On(tony,mike)',),
       ('On(mike,john)',),
       ('Green(tony)',),
       ('~Green(john)',),
       ('~On(xx,yy)', '~Green(xx)', 'Green(yy)')}

print('--- Test case # 3 ---')
resolution_steps3 = solver(KB3)
for step in resolution_steps3:
    print(step)

KB4 = {('I(bb)',),
       ('U(aa,bb)',),
       ('~F(u)',),
       ('~I(y)', '~U(x,y)', 'F(f(z))'),
       ('~I(v)', '~U(w,v)', 'E(w,f(w))')}

print('--- Test case # 4 ---')
resolution_steps4 = solver(KB4)
for step in resolution_steps4:
    print(step)

KB5 = {('~P(aa)',),
       ('P(z)', '~Q(f(z),f(u))'),
       ('Q(x,f(g(y)))', 'R(s)'),
       ('~R(t)',)}

print('--- Test case # 5 ---')
resolution_steps5 = solver(KB5)
for step in resolution_steps5:
    print(step)
