import os
import random

from decorator import decorator
from pymock import dummy, override, replay, use_pymock, verify
from sqlobject import ForeignKey, MultipleJoin, RelatedJoin, SQLObject, StringCol

class Student(SQLObject):
    fullName = StringCol(length=64)
    username = StringCol(length=16, default=None)
    emails = MultipleJoin('Email')
    courses = RelatedJoin('Course')

class Email(SQLObject):
    address = StringCol(length=255)
    student = ForeignKey('Student')

class Course(SQLObject):
    name = StringCol(length=64)
    students = RelatedJoin('Student')

def create_schema():
    Student.createTable()
    Email.createTable()
    Course.createTable()
