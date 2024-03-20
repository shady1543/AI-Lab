"""
Project: ResolutionFOL.
Author : shady1543, Tokisakix
Time   : 24-03-15
"""
import re

def parse_predicate(predicate:str) -> tuple[str, list[str]]:
    """
    解析逻辑谓词字符串，提取谓词名称和参数列表。

    参数:
    - predicate: 字符串，表示逻辑谓词的字符串。

    返回值:
    - 元组，包含两个元素：谓词名称（字符串）和参数列表（字符串列表）。
      如果谓词被否定，谓词名称将包含否定符号(~)。
    """
    negation = False
    if predicate.startswith('~'):
        negation = True
        predicate = predicate[1:]

    name_end = predicate.find('(')
    name = predicate[:name_end]
    if negation:
        name = '~' + name

    args = predicate[name_end + 1:-1].split(',')

    return (name, args)


def is_variable(term:str) -> bool:
    """
    使用正则表达式判断给定的字符串是否表示一个变量。

    参数:
    - term: 一个字符串，待判断是否为变量的项。

    返回值:
    - 如果`term`符合变量的定义，则返回True；否则返回False。
    """
    return re.match(r'^[u-z]{1,2}$', term) is not None


def apply_mgu(predicate1:str, predicate2:str) -> dict:
    """
     应用最一般合一（Most General Unifier, MGU）算法，计算两个谓词的合一替换。

     参数:
     - predicate1: 字符串，表示第一个谓词的逻辑表达式。
     - predicate2: 字符串，表示第二个谓词的逻辑表达式。

     返回值:
     - 字典，包含合一替换，其中键是变量，值是替换后的表达式；
       如果两个谓词无法合一，则返回None。
     """
    _, args1 = parse_predicate(predicate1)
    _, args2 = parse_predicate(predicate2)

    substitutions = {}
    for arg1, arg2 in zip(args1, args2):
        if arg1 == arg2:
            continue
        if is_variable(arg1) and is_variable(arg2):
            return None
        if is_variable(arg1):
            substitutions[arg1] = arg2
        elif is_variable(arg2):
            substitutions[arg2] = arg1
        else:
            return None
    return substitutions


def can_resolve(clause1:tuple[str], clause2:tuple[str]) -> tuple[bool, tuple[str, str]]:
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
            name1, args1 = parse_predicate(pred1)
            name2, args2 = parse_predicate(pred2)

            if (name1.startswith('~') != name2.startswith('~')) and (name1.lstrip('~') == name2.lstrip('~')):
                substitutions = apply_mgu(pred1, pred2)
                if substitutions is not None:
                    return True, (pred1, pred2)
    return False, ()


def apply_substitutions_to_clause(clause:tuple[str], substitutions:dict) -> tuple[list[str]]:
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
        name, args = parse_predicate(predicate)
        new_args = [substitutions.get(arg, arg) for arg in args]
        new_predicate = f"{name[1:] if name.startswith('~') else name}({','.join(new_args)})"
        if name.startswith('~'):
            new_predicate = f"~{new_predicate}"
        new_clause.append(new_predicate)
    return tuple(new_clause)


def ResolutionFOL(KB:set[tuple[str]]) -> list[str]:
    """
    主推理逻辑。执行归结推理算法，从知识库KB中推导出结论。

    参数:
    - KB: 知识库，一个包含逻辑子句的集合。

    返回值:
    - 步骤列表，记录了归结推理的每一步。
    """
    steps = []
    new_clauses = set()
    clauses = list(KB)
    resolved_pairs = set()
    clause_to_step = {clause: str(i + 1) for i, clause in enumerate(clauses)}

    for clause in clauses:
        steps.append(f"{clause_to_step[clause]} {clause}")

    def format_clause_index(clause:str, predicate_index:int, total_predicates:int) -> str:
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
        base_index = clause_to_step[clause]
        if total_predicates > 1:
            return f"{base_index}{chr(97 + predicate_index)}"
        return base_index

    while True:
        possible_resolutions = []
        for i, clause1 in enumerate(clauses):
            for j, clause2 in enumerate(clauses[i + 1:], start=i + 1):
                if (i, j) not in resolved_pairs and can_resolve(clause1, clause2)[0]:
                    # 推理
                    resolved_pairs.add((i, j))
                    _, predicates_to_resolve = can_resolve(clause1, clause2)
                    substitutions = apply_mgu(predicates_to_resolve[0], predicates_to_resolve[1])
                    unified = '{' + ', '.join(
                        [f"{k}={v}" for k, v in substitutions.items()]) + '}' if substitutions else ''
                    clause1_substituted = apply_substitutions_to_clause(clause1, substitutions)
                    clause2_substituted = apply_substitutions_to_clause(clause2, substitutions)
                    resolvents = set(clause1_substituted + clause2_substituted) - set(
                        apply_substitutions_to_clause(predicates_to_resolve, substitutions))
                    resolvents = tuple(sorted(resolvents, key=lambda x: x.replace('~', '')))

                    # 格式化
                    i_formatted = format_clause_index(clause1, clause1.index(predicates_to_resolve[0]), len(clause1))
                    j_formatted = format_clause_index(clause2, clause2.index(predicates_to_resolve[1]), len(clause2))
                    unified_str = unified if unified else ''
                    step_str = f"R[{i_formatted},{j_formatted}]{unified_str} = {resolvents}"

                    # 判断结束推理
                    if not resolvents:
                        steps.append(f"{len(steps) + 1} {step_str}")
                        return steps
                    possible_resolutions.append((step_str, resolvents))

        if not possible_resolutions:
            break

        for step_str, resolvents in possible_resolutions:
            if resolvents not in set(clauses) and resolvents not in new_clauses:
                new_clauses.add(resolvents)
                steps.append(f"{len(steps) + 1} {step_str}")
                clause_to_step[resolvents] = str(len(steps))

        clauses.extend(new_clauses)
        new_clauses.clear()

    return steps