
from twisted.application import service
from buildbot.master import BuildMaster

basedir = r'/usr/local/buildbot/master/rsreader'
configfile = r'master.cfg'

application = service.Application('buildmaster')
BuildMaster(basedir, configfile).setServiceParent(application)

