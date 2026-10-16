# -*- coding: utf-8 -*-

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from masterserver.exc import ServerCollisionError
from .models import Server
import logging
import os
import socket


class SauerbratenStyleProtocol(LineReceiver):
    # Modern Twisted delivers lines as bytes; keep the delimiter bytes too.
    delimiter = b'\n'

    def __init__(self):
        self.logger = logging.getLogger("masterserver:sauerbraten")

    def timeoutReached(self, server, transport):
        self.logger.info(
            "server reached timeout: %s:%d" % (server.ip, server.port)
        )
        server.unregister()
        transport.loseConnection()

    def connectionMade(self):
        peer = self.transport.getPeer()
        ip = peer.host
        port = peer.port
        self.logger.debug("client connected: %s:%d" % (ip, port))

    def lineReceived(self, line):
        def fail():
            self.transport.write(b"failreg\n")
            self.transport.loseConnection()

        def success(server):
            self.transport.write(b"succreg\n")
            task = reactor.callLater(60*60, self.timeoutReached,
                                     server, self.transport)

        line = line.decode("utf-8", "replace").rstrip("\r").rstrip("\n")
        if line.startswith("regserv"):
            try:
                ip = self.transport.getPeer().host
                port = int(line.split()[1])
                server = Server.register(ip, port)
            except ServerCollisionError:
                self.logger.error(
                    "server already registered: %s:%d" % (ip, port)
                )
                fail()
            except (ValueError, IndexError):
                self.logger.error(
                    "bad syntax for registration: %s" % line
                )
                fail()
            else:
                self.logger.info(
                    "server registered successfully: %s:%d" % (ip, port)
                )
                success(server)

        elif line.strip() == "list":
            for server in Server.getlist():
                self.transport.write(
                    ("addserver %s %d\n" % (server.ip, server.port)).encode("utf-8")
                )
            # Close only after every addserver line has been written;
            # the original code closed the connection inside the loop,
            # which dropped every server after the first.
            self.transport.loseConnection()

        else:
            self.logger.error("client wanted something unknown: %s" % line)
            self.transport.loseConnection()


class SauerbratenStyleFactory(ServerFactory):
    protocol = SauerbratenStyleProtocol

    def startFactory(self):
        # Proxying the public Sauerbraten master list is off by default:
        # this master serves Revelade Revolution servers, and proxied
        # entries carry none of the fields the RR client expects.
        # Set MASTERSERVER_PROXY=1 to restore the old behaviour.
        if os.environ.get("MASTERSERVER_PROXY", "").lower() in ("1", "true", "yes"):
            LoopingCall(
                lambda: query_other_master("sauerbraten.org", 28787)
            ).start(300)


def query_other_master(ip, port, bufsize=65536):
    logger = logging.getLogger("masterserver:sauerbraten")

    logger.info("fetching servers from masterserver %s:%d" % (ip, port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug("connecting to %s:%d" % (ip, port))
    sock.connect((ip, port))

    logger.debug("retrieving server list")
    sock.sendall(b"list\n")

    data = b""
    while True:
        buffer = sock.recv(bufsize)
        data += buffer
        if not buffer:
            break

    for line in data.decode("utf-8", "replace").split("\n"):
        if line.startswith("addserver"):
            try:
                ip = line.split()[1]
                port = int(line.split()[2])
                Server.register(ip, port, proxied=True)
            except ServerCollisionError:
                logger.debug("server already registered: %s:%d" % (ip, port))
            except (IndexError, ValueError):
                logger.warning("error parsing line: %s" % line)
            else:
                logger.info(
                    "server from other masterserver "
                    "registered: %s:%d" % (ip, port)
                )

    sock.close()
    logger.info("querying other masterserver finished successfully")
