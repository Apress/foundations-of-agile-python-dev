
from twisted.application import service
from buildbot.slave.bot import BuildSlave

basedir = r'/usr/local/buildbot/slave/rsreader'
buildmaster_host = 'buildmaster'
port = 4484
slavename = 'rsreader-linux'
passwd = '"Fo74gh18"'
keepalive = 600
usepty = 1
umask = None

application = service.Application('buildslave')
s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask)
s.setServiceParent(application)

