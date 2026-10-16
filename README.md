MasterServer
============

This project provides a master server implementation for [Revelade Revolution](http://rr.theintercooler.com) and [Sauerbraten-Fork](https://github.com/sauerbraten-fork/sauerbraten-fork/).

License
-------

Copyright (C) 2014 TheAssassin

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.

3. This notice may not be removed or altered from any source
   distribution.

Running (updated for Revelade Revolution v1.1.1)
------------------------------------------------

The game client no longer uses the classic Sauerbraten master protocol
to browse servers. It speaks HTTP to its master:

- Server list: `GET /?version=<ver>&protocol=267` returns a bare JSON
  array of server objects, each with `uuid`, `name`, `ip`, `port` and
  `playercount`. The client keys servers by `uuid`.
- Version check: `GET /version/check-last?version=<ver>&protocol=267`
  returns `1` when the given version is the latest, `0` otherwise
  (the client reads only the first byte).

Setup (Python 3.10+):

    pip install -r requirements.txt
    python run.py

Listeners:

- HTTP API on port 16962 (the game's RR_MASTER_PORT; override with
  `MASTERSERVER_HTTP_PORT`).
- Classic Sauerbraten TCP protocol (`regserv` / `list`) on port 28787
  (override with `MASTERSERVER_TCP_PORT`).

Registering a server:

- HTTP: `curl "http://<master-host>:16962/register?port=27960&name=My+Server"`
  (or `POST /servers` with a JSON body `{"port": 27960, "name": "My Server"}`).
  Re-registering the same ip/port refreshes the entry and keeps its uuid.
  `/unregister?uuid=<uuid>` removes an entry.
- Classic TCP: send `regserv 27960` to port 28787; query with `list`.

Testing with the game:

1. Start this master server on the host you want to test with.
2. Start the game, open the console and set `mastername` to that host
   (the port is already 16962 by default), then run `updatefrommaster`
   or open the server browser.
3. Register a game server (above), refresh the server browser, and
   connect to it from the list.

Environment knobs:

- `MASTERSERVER_LATEST_VERSION`: version string that
  `/version/check-last` treats as current (default `0.1.0-alpha-4-r-1`,
  the RR_VERSION_STRING the v1.1.1 client reports).
- `MASTERSERVER_PROXY=1`: also mirror sauerbraten.org's public list
  (off by default; this master serves Revelade servers).
