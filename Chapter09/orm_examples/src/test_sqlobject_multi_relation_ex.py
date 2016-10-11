from sqlobject.sqlbuilder import LIKE
import sqlobject

from sqlobject_multi_relation_ex import *
from sqlobject_harness import *

@decorator
def with_sqlobject(tst):
    with_sqlobject_and_schema(create_schema, tst)

@with_sqlobject
def test_enrollment_add_and_remove():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    s1.addEnrolled(c1)
    assert s1.enrolled == [c1]
    s1.removeEnrolled(c1)
    assert s1.enrolled == []

@with_sqlobject
def test_enrollment_relations_are_separate():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    c2 = Course(name="Biochemistry")
    s1.addEnrolled(c1)
    s1.addCompleted(c2)
    assert s1.enrolled == [c1]
    assert s1.completed == [c2]