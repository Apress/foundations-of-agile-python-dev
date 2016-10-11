# Application Type Adapters. This contains a fixture and a type adapter
#LegalNotices jhr2005
#endLegalNotices

from fit.ColumnFixture import ColumnFixture
from fit import TypeAdapter

class CustomIntAdapter(object):
    def __init__(self, aString):
        self.anInt = int(aString)

    def __eq__(self, other):
        return self.anInt == other.anInt

    def __str__(self):
        return str(self.anInt)

    def __add__(self, b):
        return CustomIntAdapter(self.anInt + b.anInt)

class AddFixture(ColumnFixture):
    _typeDict = {"a": "@customInt",
                 "a.columnType": "given",
                 "b": "@customInt",
                 "b.columnType": "given",
                 "c": "@customInt",
                 "c.columnType": "result"
                 }

    a = 0
    b = 0
    def c(self):
        return self.a + self.b

class CheckAdapterClass(ColumnFixture):
    _typeDict = {"name": "String",
                 "name.columnType": "given",
                 "className": "String",
                 "className.columnType": "result",
                 }

    name = ""

    def className(self):
        metadata = {"stuff": self.name}
        accessor = TypeAdapter.on(self, "stuff", metadata)
        adapter = accessor.adapter
        if accessor.protocol.protocolName == "ApplicationObject":
            classObj = adapter
        else:
            classObj = adapter.__class__
        return classObj.__name__
        
        
        
