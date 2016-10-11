# Comment Fixture - from FitNesse version of Fit
#LegalNotices om2004 jr2004 jr2005
#endLegalNotices

# change in 0.8 - no longer marks cells as ignored.


from fit.Fixture import Fixture

class Comment(Fixture):
    def doTable(self, table):
        return
