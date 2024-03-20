"""
Project: ResolutionFOL Testing.
Author : Tokisakix
Time   : 24-03-20
"""
import pytest

from ResolutionFOL_v2 import ResolutionFOL


# ------Test------

@pytest.mark.skip
def test_func(KB:set) -> None:
    resolution_steps = ResolutionFOL()(KB)
    print("\n\n")
    for step in resolution_steps:
        print(step)
    return

def test1_1() -> None:
    KB = {('GradStudent(sue)',), ('~GradStudent(x)', 'Student(x)'), ('~Student(x)', 'HardWorker(x)'), ('~HardWorker(sue)',)}
    test_func(KB)
    return

def test1_2() -> None:
    KB = {('A(tony)',), ('A(mike)',), ('A(john)',), ('L(tony,rain)',), ('L(tony,snow)',),
        ('~A(x)', 'S(x)', 'C(x)'), ('~C(y)', '~L(y,rain)'), ('L(z,snow)', '~S(z)'),
        ('~L(tony,u)', '~L(mike,u)'), ('L(tony,v)', 'L(mike,v)'), ('~A(w)', '~C(w)', 'S(w)')}
    test_func(KB)
    return

def test1_3() -> None:
    KB = {('On(tony,mike)',), ('On(mike,john)',), ('Green(tony)',), ('~Green(john)',),
        ('~On(xx,yy)', '~Green(xx)', 'Green(yy)')}
    test_func(KB)
    return

def test2_1() -> None:
    KB = {('GradStudent(sue)',),
        ('~GradStudent(x)', 'Student(x)'),
        ('~Student(x)', 'HardWorker(x)'),
        ('~HardWorker(sue)',)}
    test_func(KB)
    return

def test2_2() -> None:
    KB = {
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
    test_func(KB)
    return

def test2_3() -> None:
    KB  = {('On(tony,mike)',),
       ('On(mike,john)',),
       ('Green(tony)',),
       ('~Green(john)',),
       ('~On(xx,yy)', '~Green(xx)', 'Green(yy)')}
    test_func(KB)
    return

def test2_4() -> None:
    KB = {('I(bb)',),
       ('U(aa,bb)',),
       ('~F(u)',),
       ('~I(y)', '~U(x,y)', 'F(f(z))'),
       ('~I(v)', '~U(w,v)', 'E(w,f(w))')}
    test_func(KB)
    return

def test2_5() -> None:
    KB = {('~P(aa)',),
        ('P(z)', '~Q(f(z),f(u))'),
        ('Q(x,f(g(y)))', 'R(s)'),
        ('~R(t)',)}
    test_func(KB)
    return