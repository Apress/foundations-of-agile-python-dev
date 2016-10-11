# Classes for Table Fixture Acceptance Test and Example
#LegalNotices jr05 gpl
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalNotices

from types import StringTypes
from fit.Parse import Parse
from fitnesse.fixtures.TableFixture import TableFixture
from fit import TypeAdapter
from fit.Utilities import em

class Invoice(object):
    def __init__(self, **kwds):
        for key, value in kwds.items():
            setattr(self, key, value)
        self.lineItems = []

    def addLineItem(self, lineItem):
        self.lineItems.append(lineItem)

class LineItem(object):        
    def __init__(self, **kwds):
        for key, value in kwds.items():
            setattr(self, key, value)

class Valid(object):
    def __init__(self):
        self.valid = True

    def itemValid(self, boolean):
        self.valid = self.valid and boolean

    def __nonzero__(self):
        return self.valid

class PosInteger(int):
    def __init__(self, unused='value'):
        if self < 1:
            raise ValueError("Value must be greater than zero")

class Currency(object):
    def __init__(self, aString):
        if isinstance(aString, StringTypes):
            parts = aString.strip().split(".")
            if len(parts) != 2:
                raise ValueError, "Currency must have exactly one decimal point"
            invalid = [x for x in parts if not x.isdigit()]
            if invalid:
                raise ValueError, "Currency must be digits"
            self.value = int(parts[0]) * 100 + int(parts[1])
        elif isinstance(aString, int):
            self.value = aString
        elif isinstance(aString, Currency):
            self.value = aString.value
        else:
            raise TypeError, "Currency must be a string"

    def __add__(self, other):
        return Currency(self.value + other.value)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __str__(self):
        integ, frac = divmod(self.value, 100)
        return "%i.%02i" % (integ, frac)

class StoreTable(TableFixture):
    def doStaticTable(self, numRows):
        valid = Valid()
        recipient = self.validateString(valid, 0, 0)
        address = self.validateString(valid, 1, 0)
        city = self.validateString(valid, 2, 0)
        attention = self.validateString(valid, 1, 1)
        location = self.validateString(valid, 2, 1)
        invoiceNumber = self.validateString(valid, 0, 3)
        orderDate = self.validateString(valid, 1, 3)
        orderNumber = self.validateString(valid, 2, 3)
        customerID = self.validateString(valid, 3, 3)
        specialDeliveryCode = self.validateString(valid, numRows - 1, 1)
        invoice = Invoice(recipient = recipient,
                          address = address,
                          city = city,
                          attention = attention,
                          location = location,
                          invoiceNumber = invoiceNumber,
                          orderDate = orderDate,
                          orderNumber = orderNumber,
                          customerID = customerID,
                          specialDeliveryCode = specialDeliveryCode)
        row = 5
        lastRow = numRows - 3
        runningTotal = Currency("0.00")
        while row <= lastRow:
            lineNumber = self.validatePosInteger(valid, row, 0)
            partNumber = self.validateString(valid, row, 1)
            description = self.validateString(valid, row, 2)
            dispatch = self.validatePosInteger(valid, row, 3)
            price = self.validateCurrency(valid, row, 4)
            lineTotal = self.validateCurrency(valid, row, 5)
            lineItem = LineItem(lineNumber = lineNumber,
                                partNumber = partNumber,
                                description = description,
                                dispatch = dispatch,
                                price = price,
                                lineTotal = lineTotal)
            invoice.addLineItem(lineItem)
            if valid:
                runningTotal = runningTotal + lineTotal
            row += 1
        total = self.validateCurrency(valid, row, 2)
        symbolCell = self.getArgCells()[1]
        if valid:
            if runningTotal != total:
                self.wrong(self.getCell(row, 2), "total does not add up!")
                valid.itemValid(False)
        if valid:
            self.setSymbol(self.getArgs()[0], invoice)
            self.right(symbolCell)
        else:
            self.wrong(symbolCell, "error - no object created")

    def validateString(self, valid, row, col):
        __pychecker__ = "no-argsused" # valid
        cell = self.getCell(row, col)
        self.right(cell)
        return cell.text()

    def validatePosInteger(self, valid, row, col):
        cell = self.getCell(row, col)
        try:
            number = int(cell.text())
            if number < 1:
                raise TypeError("must be greater than zero")
            self.right(cell)
        except Exception, e:
            self.exception(cell, e)
            valid.itemValid(False)
            number = 1
        return number

    def validateCurrency(self, valid, row, col):
        cell = self.getCell(row, col)
        try:
            amount = Currency(cell.text())
            self.right(cell)
        except Exception, e:
            self.exception(cell, e)
            valid.itemValid(False)
            amount = Currency(0)
        return amount

class CheckTable1(TableFixture):
    def doStaticTable(self, numRows):
        self.valid = Valid()
        invoice = self.getSymbol(self.getArgs()[0])
        self.checkString((0, 0), invoice.recipient)
        self.checkString((1, 0), invoice.address)
        self.checkString((2, 0), invoice.city)
        self.checkString((1, 1), invoice.attention)
        self.checkString((2, 1), invoice.location)
        self.checkString((0, 3), invoice.invoiceNumber)
        self.checkString((1, 3), invoice.orderDate)
        self.checkString((2, 3), invoice.orderNumber)
        self.checkString((3, 3), invoice.customerID)
        self.checkString((numRows - 1, 1),
                         invoice.specialDeliveryCode)
        numLineItems = numRows - 7
        if len(invoice.lineItems) != numLineItems:
            pass # report error and mark all rows ignored
        row = 5
        runningTotal = Currency("0.00")
        for lineItem in invoice.lineItems:
            self.checkPosInteger((row, 0), lineItem.lineNumber)
            self.checkString((row, 1), lineItem.partNumber)
            self.checkString((row, 2), lineItem.description)
            self.checkPosInteger((row, 3), lineItem.dispatch)
            self.checkCurrency((row, 4), lineItem.price)
            self.checkCurrency((row, 5), lineItem.lineTotal)
            if self.valid:
                runningTotal = runningTotal + lineItem.lineTotal
            row += 1
        self.checkCurrency((row, 2), runningTotal)
        symbolCell = self.getArgCells()[1]
        if self.valid:
            self.right(symbolCell)
        else:
            self.wrong(symbolCell, "Validation Error")

    def checkString(self, cell, expected):
        cell = self._getCell(cell)
        actual = cell.text()
        isValid = self._check(cell, actual, expected)
        self.valid.itemValid(isValid)
        return isValid

    def _check(self, cell, actual, expected):
        match = actual == expected
        if match:
            self.right(cell)
        else:
            self.wrong(cell, str(expected))
        return match

    def _getCell(self, cell):
        if isinstance(cell, Parse):
            return cell
        return self.getCell(cell[0], cell[1])

    def checkPosInteger(self, cell, actual):
        cell = self._getCell(cell)
        isValid, expected = self.parsePosInteger(cell)
        if isValid:
            isValid = self._check(cell, actual, expected)
        self.valid.itemValid(isValid)
        return isValid

    def parsePosInteger(self, cell):
        valid = True
        try:
            number = int(cell.text())
            if number < 1:
                raise TypeError("must be greater than zero")
            self.right(cell)
        except Exception, e:
            self.exception(cell, e)
            valid = False
            number = 1
        return valid, number

    def checkCurrency(self, cell, actual):    
        cell = self._getCell(cell)
        isValid, expected = self.parseCurrency(cell)
        if isValid:
            isValid = self._check(cell, actual, expected)
        self.valid.itemValid(isValid)
        return isValid

    def parseCurrency(self, cell):
        cell = self._getCell(cell)
        isValid = True
        try:
            amount = Currency(cell.text())
            self.right(cell)
        except Exception, e:
            self.exception(cell, e)
            isValid = False
            amount = Currency(0)
        return isValid, amount

class CheckTableUsingTA(TableFixture):
    def doStaticTable(self, numRows):
        self.valid = Valid()
        invoice = self.getSymbol(self.getArgs()[0])
        self.checkString((0, 0), invoice, "recipient")
        self.checkString((1, 0), invoice, "address")
        self.checkString((2, 0), invoice, "city")
        self.checkString((1, 1), invoice, "attention")
        self.checkString((2, 1), invoice, "location")
        self.checkString((0, 3), invoice, "invoiceNumber")
        self.checkString((1, 3), invoice, "orderDate")
        self.checkString((2, 3), invoice, "orderNumber")
        self.checkString((3, 3), invoice, "customerID")
        self.checkString((numRows - 1, 1), invoice, 
                         "specialDeliveryCode")
        numLineItems = numRows - 7
        row = 5
        if len(invoice.lineItems) != numLineItems:
            self.wrong(self.getCell(4, 0),
                       "Wrong number of line items. Expected: %s Got: %s"
                       % (len(invoice.lineItems), numLineItems))
            aRow = self.getRow(row)
            while numLineItems > 0:
                self.ignore(aRow)
                aRow = aRow.more
                numLineItems -= 1
            self.valid.itemValid(False)
        else:
            self.runningTotal = Currency("0.00")
            for lineItem in invoice.lineItems:
                self.checkPosInteger((row, 0), lineItem, "lineNumber")
                self.checkString((row, 1), lineItem, "partNumber")
                self.checkString((row, 2), lineItem, "description")
                self.checkPosInteger((row, 3), lineItem, "dispatch")
                self.checkCurrency((row, 4), lineItem, "price")
                self.checkCurrency((row, 5), lineItem, "lineTotal")
                if self.valid:
                    self.runningTotal = self.runningTotal + lineItem.lineTotal
                row += 1
            self.checkCurrency((row, 2), self, "runningTotal")
        symbolCell = self.getArgCells()[1]
        if self.valid:
            self.right(symbolCell)
        else:
            self.wrong(symbolCell, "Validation Error")

    def checkString(self, cell, obj, identifier):
        return self._check(cell, obj, identifier, "String")

    def checkPosInteger(self, cell, obj, identifier):
        return self._check(cell, obj, identifier, PosInteger)

    def checkCurrency(self, cell, obj, identifier):
        return self._check(cell, obj, identifier, Currency)

    def _check(self, cell, obj, identifier, typeName):
        cell = self._getCell(cell)
        ta = TypeAdapter.on(obj, identifier, {identifier: typeName})
        checkResult = self.check(cell, ta)
        isValid = checkResult.isRight()
        self.valid.itemValid(isValid)
        return isValid

    def _getCell(self, cell):
        if isinstance(cell, Parse):
            return cell
        return self.getCell(cell[0], cell[1])
