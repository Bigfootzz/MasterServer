# -*- coding: utf-8 -*-

from twisted.application import internet, service
from masterserver.sauerfork.sauerbraten import SauerbratenStyleFactory
from masterserver.sauerfork.http import httpsite
from twisted.internet import reactor
from twisted.python import log
import logging
import os


observer = log.PythonLoggingObserver(loggerName="twisted")
observer.start()

# The Revelade Revolution client talks HTTP to its master on port 16962
# (RR_MASTER_PORT in the game's src/fpsgame/game.h), so the HTTP site is
# the primary interface. The classic Sauerbraten TCP protocol keeps its
# traditional port 28787. Both can be overridden by environment.
HTTP_PORT = int(os.environ.get("MASTERSERVER_HTTP_PORT", "16962"))
TCP_PORT = int(os.environ.get("MASTERSERVER_TCP_PORT", "28787"))


def configure_logging(filename=None, loglevel=logging.INFO):
    for loggername in ("twisted",
                       "masterserver",
                       "masterserver:sauerbraten"):
        logger = logging.getLogger(loggername)
        logger.setLevel(loglevel)

        if filename is not None:
            handler = logging.FileHandler(filename)
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: [{0}] %(message)s'.format(loggername)
        ))
        logger.addHandler(handler)


def get_reactor():
    configure_logging(loglevel=logging.DEBUG)
    reactor.listenTCP(TCP_PORT, SauerbratenStyleFactory())
    reactor.listenTCP(HTTP_PORT, httpsite)
    return reactor


def get_application():
    configure_logging(filename="server.log")
    application = service.Application("masterserver")

    internet.TCPServer(
        TCP_PORT, SauerbratenStyleFactory()
    ).setServiceParent(application)
    internet.TCPServer(HTTP_PORT, httpsite).setServiceParent(application)

    return application
