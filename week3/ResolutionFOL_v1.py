#!/usr/bin/env python
# coding: utf-8

# In[1]:


def parse_predicate(predicate):
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


# In[2]:


import re


def is_variable(term):
    return re.match(r'^[u-z]{1,2}$', term) is not None


def apply_mgu(predicate1, predicate2):
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


def can_resolve(clause1, clause2):
    for pred1 in clause1:
        for pred2 in clause2:
            name1, args1 = parse_predicate(pred1)
            name2, args2 = parse_predicate(pred2)

            if (name1.startswith('~') != name2.startswith('~')) and (name1.lstrip('~') == name2.lstrip('~')):
                substitutions = apply_mgu(pred1, pred2)
                if substitutions is not None:
                    return True, (pred1, pred2)
    return False, ()


# In[3]:


def apply_substitutions_to_clause(clause, substitutions):
    new_clause = []
    for predicate in clause:
        name, args = parse_predicate(predicate)
        new_args = [substitutions.get(arg, arg) for arg in args]
        new_predicate = f"{name[1:] if name.startswith('~') else name}({','.join(new_args)})"
        if name.startswith('~'):
            new_predicate = f"~{new_predicate}"
        new_clause.append(new_predicate)
    return tuple(new_clause)


# In[4]:


def ResolutionFOL(KB):
    steps = []
    new_clauses = set()
    clauses = list(KB)
    resolved_pairs = set()
    clause_to_step = {clause: str(i + 1) for i, clause in enumerate(clauses)}

    for clause in clauses:
        steps.append(f"{clause_to_step[clause]} {clause}")

    def format_clause_index(clause, predicate_index, total_predicates):
        base_index = clause_to_step[clause]
        if total_predicates > 1:
            return f"{base_index}{chr(97 + predicate_index)}"
        return base_index

    while True:
        possible_resolutions = []
        for i, clause1 in enumerate(clauses):
            for j, clause2 in enumerate(clauses[i + 1:], start=i + 1):
                if (i, j) not in resolved_pairs and can_resolve(clause1, clause2)[0]:
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

                    i_formatted = format_clause_index(clause1, clause1.index(predicates_to_resolve[0]), len(clause1))
                    j_formatted = format_clause_index(clause2, clause2.index(predicates_to_resolve[1]), len(clause2))
                    unified_str = unified if unified else ''
                    step_str = f"R[{i_formatted},{j_formatted}]{unified_str} = {resolvents}"
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


KB = {('GradStudent(sue)',), ('~GradStudent(x)', 'Student(x)'), ('~Student(x)', 'HardWorker(x)'), ('~HardWorker(sue)',)}
resolution_steps = ResolutionFOL(KB)

for step in resolution_steps:
    print(step)

# In[5]:


KB1 = {('A(tony)',), ('A(mike)',), ('A(john)',), ('L(tony,rain)',), ('L(tony,snow)',),
       ('~A(x)', 'S(x)', 'C(x)'), ('~C(y)', '~L(y,rain)'), ('L(z,snow)', '~S(z)'),
       ('~L(tony,u)', '~L(mike,u)'), ('L(tony,v)', 'L(mike,v)'), ('~A(w)', '~C(w)', 'S(w)')}

resolution_steps_kb1 = ResolutionFOL(KB1)
for step in resolution_steps_kb1:
    print(step)

# In[6]:


KB2 = {('On(tony,mike)',), ('On(mike,john)',), ('Green(tony)',), ('~Green(john)',),
       ('~On(xx,yy)', '~Green(xx)', 'Green(yy)')}

resolution_steps_kb2 = ResolutionFOL(KB2)
for step in resolution_steps_kb2:
    print(step)

# In[ ]:


# In[ ]:


# In[ ]:
