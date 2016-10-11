from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table, String
from sqlalchemy.orm import mapper, relation

schema = MetaData()
student_table = Table('student', schema,
    Column('id', Integer, primary_key=True),
    Column('username', String(16)),
    Column('full_name', String(64)),
)

email_table = Table('email', schema,
    Column('id', Integer, primary_key=True),
    Column('address', String(255), nullable=False),
    Column('student_id', Integer, \
    ForeignKey('student.id'), nullable=False),
)

course_table = Table('course', schema,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), nullable=False),
)

enrolled_assc_table = \
    Table('enrolled_assc', schema,
    Column('student_id', Integer, ForeignKey('student.id')),
    Column('course_id', Integer, ForeignKey('course.id')),
)

class Student(object):
    
    def __init__(self, username, full_name):
        self.username = username
        self.full_name = full_name


class Email(object):

    def __init__(self, address):
        self.address = address


class Course(object):

    def __init__(self, name):
        self.name = name

mapper(Student, student_table, properties={
   'emails': relation(Email,
                      backref="student",
                      cascade="all, delete, delete-orphan")
})

mapper(Email, email_table)

mapper(Course, course_table, properties={
    'enrolled': relation(Student,
                         secondary=enrolled_assc_table,
                         backref='enrolled')
})