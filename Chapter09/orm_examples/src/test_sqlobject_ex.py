from sqlobject.sqlbuilder import LIKE
import sqlobject

from sqlobject_ex import *
from sqlobject_harness import *

@decorator
def with_sqlobject(tst):
    with_sqlobject_and_schema(create_schema, tst)

# SECTION: Introduction

@with_sqlobject
def test_creating_student():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    assert s1.username == "jeff"
    assert s1.fullName == "Jeff Younker"

@with_sqlobject
def test_get():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student.get(s1.id)
    assert s1 is s2


# SECTION: Selecting Objects

@with_sqlobject
def test_select():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student(username="doug", fullName="Doug McBride")
    students = list(Student.select())
    assert len(students) == 2
    assert set(students) == set([s1, s2])
    
@with_sqlobject
def test_select_using_full_name():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    unused_s2 = Student(username="doug", fullName="Doug McBride")
    students = Student.select(Student.q.fullName == "Jeff Younker")
    assert list(students) == [s1]
    
@with_sqlobject
def test_select_using_partial_name():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student(username="doug", fullName="Doug McBride")
    unused_s3 = Student(username="amy", fullName="Amy Woodward")
    students = Student.select(LIKE(Student.q.fullName, '%ou%'))
    assert set(students) == set([s1, s2])
    
@with_sqlobject
def test_selectBy_full_name():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    unused_s3 = Student(username="amy", fullName="Amy Woodward")
    students = Student.selectBy(fullName="Jeff Younker")
    assert list(students) == [s1]

@with_sqlobject
def test_selectBy_all():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student(username="doug", fullName="Doug McBride")
    students = Student.selectBy()
    assert set(students) == set([s1, s2])
    
# SECTION: Updating fields

@with_sqlobject
def test_modify_values():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s1.fullName = "Jeff M. Younker"
    students = Student.selectBy(fullName="Jeff M. Younker")
    assert list(students) == [s1]

@with_sqlobject
def test_delete():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s1.destroySelf()
    students = Student.select()
    assert list(students) == []
  
  
# SECTION: Foreign Keys

@with_sqlobject
def test_email_creation():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student(username="doug", fullName="Doug McBride")
    e1 = Email(address="jeff@not.real.org", student=s1)
    assert e1.student is s1
    e1.student = s2
    assert e1.student is s2
    
@with_sqlobject
def test_direct_id_access():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student(username="doug", fullName="Doug McBride")
    e1 = Email(address="jeff@not.real.org", student=s1)
    assert e1.studentID == s1.id
    e1.studentID = s2.id
    assert e1.student is s2


# SECTION: Multiple Joins

@with_sqlobject
def test_multiple_join():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    e1 = Email(address="jeff@not.real.org", student=s1)
    assert s1.emails == [e1]

@with_sqlobject
def test_multiple_join_empty_returns_empty_list():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    assert s1.emails == []

@with_sqlobject
def test_multiple_join_cant_assign():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    e1 = Email(address="jeff@not.real.org", student=s1)
    try:
        s1.emails = [e1]
        assert False
    except AttributeError:
        pass

@with_sqlobject
def test_changing_a_multiple_join():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    s2 = Student(username="doug", fullName="Doug McBride")
    e1 = Email(address="jeff@not.real.org", student=s1)
    e2 = Email(address="doug@not.real.org", student=s2)
    assert s1.emails == [e1]
    e2.student = s1
    assert set(s1.emails) == set([e1, e2])
    

# SECTION: Many-to-many Relationships

@with_sqlobject
def test_related_join_add():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    c2 = Course(name="Biochemistry")
    s1.addCourse(c1)
    s1.addCourse(c2)
    assert set(s1.courses) == set([c1, c2])
    assert c1.students == [s1]
    assert c2.students == [s1]

@with_sqlobject
def test_related_join_add_in_other_order():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    c2 = Course(name="Biochemistry")
    s1.addCourse(c1)
    c2.addStudent(s1)
    assert set(s1.courses) == set([c1, c2])
    assert c1.students == [s1]
    assert c2.students == [s1]

@with_sqlobject
def test_related_join_remove():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    c2 = Course(name="Biochemistry")
    s1.addCourse(c1)
    s1.addCourse(c2)
    assert set(s1.courses) == set([c1, c2])
    c2.removeStudent(s1)
    s1.removeCourse(c1)
    assert s1.courses == []
    assert c1.students == [] and c2.students == []
    
@with_sqlobject
def test_related_join_multiple_adds():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    s1.addCourse(c1)
    s1.addCourse(c1)
    assert s1.courses == [c1, c1]
    assert c1.students == [s1, s1]
    
@with_sqlobject
def test_related_join_removing_multiples():
    s1 = Student(username="jeff", fullName="Jeff Younker")
    c1 = Course(name="Modern Algebra")
    s1.addCourse(c1)
    s1.addCourse(c1)
    s1.removeCourse(c1)
    assert s1.courses == []