import os
import random

from decorator import decorator
from pymock import dummy, override, replay, use_pymock, verify
from sqlobject import ForeignKey, MultipleJoin, RelatedJoin, SQLObject, StringCol

class Student(SQLObject):
    fullName = StringCol(length=64)
    username = StringCol(length=16, default=None)
    emails = MultipleJoin('Email')
    enrolled = RelatedJoin('Course',
        intermediateTable="enrolled_assc",
        joinColumn="studentID",
        otherColumn="courseID",
        addRemoveName="Enrolled")
    completed = RelatedJoin('Course',
        intermediateTable="completed_assc",
        joinColumn="studentID",
        otherColumn="courseID",
        addRemoveName="Completed")

class Email(SQLObject):
    address = StringCol(length=255)
    student = ForeignKey('Student')

class Course(SQLObject):
    name = StringCol(length=64)
    enrolled = RelatedJoin('Student',
        intermediateTable="enrolled_assc",
        joinColumn="courseID",
        otherColumn="studentID",
        addRemoveName="Enrolled")
    completed = RelatedJoin('Student',
        intermediateTable="completed_assc",
        joinColumn="courseID",
        otherColumn="studentID",
        addRemoveName="Completed")

def create_schema():
    Student.createTable()
    Email.createTable()
    Course.createTable()
