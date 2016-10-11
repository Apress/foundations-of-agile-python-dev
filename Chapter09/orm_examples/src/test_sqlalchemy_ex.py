from nose.tools import assert_raises
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exceptions import InvalidRequestError

from sqlalchemy_ex import Course, Email, schema, Student, student_table

def test_schema_creation():
    engine = create_engine('sqlite:///:memory:')
    schema.create_all(engine)
    
def test_create_unsaved_student():
    s1 = Student(username="jeff", full_name="Jeff Younker")
    assert s1.username == "jeff"
    assert s1.full_name == "Jeff Younker"
    assert s1.id is None

def test_getting_a_session():
    engine = create_engine('sqlite:///:memory:')
    schema.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True,
    transactional=True)
    unused_session = Session()
    
def test_getting_a_session_and_binding_later():
    engine = create_engine('sqlite:///:memory:')
    schema.create_all(engine)
    Session = sessionmaker(autoflush=True, transactional=True)
    Session.configure(bind=engine)
    unused_session = Session()
    
def test_create_and_save_student():
    engine = create_engine('sqlite:///:memory:')
    schema.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True, \
    transactional=True)
    session = Session()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    session.save(s1)
    assert s1.id is None
    session.flush()
    assert s1.id is not None

def session_from_new_db():
    engine = create_engine('sqlite:///:memory:')
    schema.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=True,
    transactional=True)
    return Session()

def test_create_and_save_and_flush_student():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    session.save(s1)
    assert s1.id is None
    session.flush()
    assert s1.id is not None

def test_retrieve_from_database():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    session.save(s1)
    f = session.query(Student).filter_by(username="jeff").first()
    assert f is s1
    assert s1.id is not None
    
def test_commit_changes():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    session.save(s1)
    session.commit()

def test_set_and_modify_database():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    session.save(s1)
    #
    f = session.query(Student).filter_by(full_name=\
    "Jeff M. Younker").first()
    assert f is None
    #
    s1.full_name = "Jeff M. Younker" # flush happens before query
    f = session.query(Student).filter_by(full_name=\
    "Jeff M. Younker").first()
    assert f is s1
    
def test_query_slice():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    s2 = Student(username="doub", full_name="Doug McBride")
    s3 = Student(username="amy", full_name="Amy Woodward")
    for s in [s1, s2, s3]:
        session.save(s)
    sliced = session.query(Student)[1:3]
    assert [s2, s3] == list(sliced)
    assert [s2, s3] != sliced
    
def test_query_results_with_index():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    s2 = Student(username="doub", full_name="Doug McBride")
    session.save(s1)
    session.save(s2)
    f = session.query(Student)[0]
    assert s1 == f
    
def prepare_two_students(session):
    s1 = Student(username="jeff", full_name="Jeff Younker")
    s2 = Student(username="doub", full_name="Doug McBride")
    session.save(s1)
    session.save(s2)
    return (s1, s2)

def test_query_results_with_index():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student)[0]
    assert f == s1
    
def test_query_results_all():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).all()
    assert f == [s1, s2]
    
def test_query_results_first():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).first()
    assert f == s1
    
def test_query_results_one_with_one_result():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).filter_by(username="jeff").one()
    assert f == s1

def test_query_results_one_raises_error_with_multiple_results():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    assert_raises(InvalidRequestError, session.query(Student).one)
    

# SECTION: Filter Expressions

def test_simple_filter_expressions():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).filter(Student.username == "jeff")
    g = session.query(Student).\
    filter(student_table.c.username == "jeff")
    assert list(f) == list(g) == [s1]
    
def test_sql_filter_expressions():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).filter(Student.username.like('%ef%'))
    assert list(f) == [s1]
    
def test_simple_literal_sql_filter_expressions():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).filter("username = 'jeff'")
    g = session.query(Student).\
    filter("username = :un").params(un="jeff")
    assert list(f) == list(g) == [s1]
    
def test_from_statement():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    query = "SELECT * FROM student WHERE username like :match"
    f = session.query(Student).from_statement(query).\
    params(match='%ou%').one()
    assert f == s2


# SECTION: Keyword Queries

def test_filter_by():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    f = session.query(Student).filter_by(username="jeff").one()
    assert f == s1
    

# SECTION: Chaining

def test_chained_filters():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    s2 = Student(username="jeffs", full_name="Jeff Smith")
    session.save(s1)
    session.save(s2)
    f = session.query(Student).\
    filter(Student.full_name.like('Jeff%')).\
    filter_by(username="jeffs").one()
    assert f == s2


# SECTION: One-to-Many Relationships

# This particular test is only works before you defined the
# relation between Student and Email
#
#def test_email_doesnt_have_student_attribute():
#    e1 = Email(address="jeff@not.real.com")
#    assert_raises(AttributeError, getattr, e1, 'student')

def test_email_now_has_student_attribute():
    e1 = Email(address="jeff@not.real.com")
    assert e1.student is None

def test_email_adding_via_one_to_many_side():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    e1 = Email(address="jeff@not.real.com")
    session.save(s1)
    s1.emails.append(e1)
    session.flush()
    assert s1.emails == [e1]
    assert e1.student == s1

def test_email_adding_via_many_to_one_side():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    e1 = Email(address="jeff@not.real.com")
    session.save(s1)
    e1.student = s1
    assert s1.emails == [e1]
    assert e1.student == s1

# This test will only work if you make the foreign key from
# email to student nullable.
# 
#def test_email_removing_via_many_to_one_side():
#    session = session_from_new_db()
#    s1 = Student(username="jeff", full_name="Jeff Younker")
#    e1 = Email(address="jeff@not.real.com")
#    session.save(s1)
#    s1.emails.append(e1)
#    session.flush()
#    del s1.emails[0]
#    session.flush()
#    assert s1.emails == []


# SECTION: Many-to-Many relationships

def prepare_two_courses(session):
    c1 = Course('Modern Algebra')
    c2 = Course('Biochemistry')
    session.save(c1)
    session.save(c2)
    return (c1, c2)

def test_enrolled_adding():
    session = session_from_new_db()
    (s1, unused_s2) = prepare_two_students(session)
    (c1, c2) = prepare_two_courses(session)
    s1.enrolled.append(c1)
    c2.enrolled.append(s1)
    session.flush()
    assert set(s1.enrolled) == set([c1, c2])
    assert c1.enrolled == [s1]
    assert c2.enrolled == [s1]
    

# SECTION: Querying Relations

def test_select_student_by_course():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    (c1, c2) = prepare_two_courses(session)
    s1.enrolled.append(c1) # Course "Modern Algebra"
    s2.enrolled.append(c2) # Course "Biochemistry"
    session.flush()
    f = session.query(Student).join('enrolled').\
    filter(Course.name=="Biochemistry").one()
    assert f == s2


# SECTION: Deleting

def test_delete_student():
    session = session_from_new_db()
    (s1, s2) = prepare_two_students(session)
    session.flush()
    session.delete(s1)
    students = session.query(Student).all()
    assert students == [s2]
    
def test_delete_cascade():
    session = session_from_new_db()
    s1 = Student(username="jeff", full_name="Jeff Younker")
    e1 = Email(address="jeff@not.real.com")
    session.save(s1)
    s1.emails.append(e1)
    session.flush()
    session.delete(s1)
    session.flush()
    email = session.query(Email).all()
    assert email == []