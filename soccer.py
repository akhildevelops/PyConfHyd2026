import random
from threading import Thread, Lock
import json
from optparse import Option
from email.utils import formatdate
from typing import Dict, Optional, List, Tuple
import asyncio
from copy import deepcopy

MAX_PLAYERS = 1024
MAX_TEAMS = 2
REQUEST_SIZE = 4 * 1024

INTRO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Name Form</title>
    <style>
        /* Basic styling to center the form and make it look nice */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f2f5;
        }

        .form-container {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 300px;
        }

        h2 {
            margin-top: 0;
            color: #333;
            font-size: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box; /* Ensures padding doesn't affect width */
        }

        button {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>

    <div class="form-container">
        <h2>Welcome</h2>
        <form>
            <label for="userName">Name</label>
            <input type="text" id="userName" name="userName" placeholder="Enter your name" required>
            <button type="submit">Submit</button>
        </form>
    </div>

</body>
</html>
"""
FOTTBALL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FootBall</title>
    <style>
        body { margin: 0; overflow: hidden; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; }
        
        #target-svg {
            position: absolute;
            cursor: pointer;
            transition: opacity 0.3s ease;
        }

        #success-message {
            display: none;
            text-align: center;
            animation: fadeIn 0.5s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        #info { color: #666; font-family: monospace; position: fixed; top: 10px; left: 10px; pointer-events: none; }
        .success-icon { font-size: 3rem; color: #4CAF50; margin-bottom: 10px; }
    </style>
</head>
<body>

    <div id="info">Waiting for click...</div>

    <div id="success-message">
        <div class="success-icon">✓</div>
        <h2>Passed the Football</h2>
        <p id="final-stats"></p>
    </div>

    <svg id="target-svg" xmlns="http://www.w3.org/2000/svg" viewBox="-2500 -2500 5000 5000" width="60" height="60">
        <title>soccer ball</title>
        <g stroke="#000" stroke-width="24">
            <circle fill="#fff" r="2376"></circle>
            <path fill="none" d="m-1643-1716 155 158m-550 2364c231 231 538 195 826 202m-524-2040c-491 351-610 1064-592 1060m1216-1008c-51 373 84 783 364 1220m-107-2289c157-157 466-267 873-329m-528 4112c-50 132-37 315-8 510m62-3883c282 32 792 74 1196 303m-404 2644c310 173 649 247 1060 180m-340-2008c-242 334-534 645-872 936m1109-2119c-111-207-296-375-499-534m1146 1281c100 3 197 44 290 141m-438 495c158 297 181 718 204 1140"></path>
        </g>
        <path fill="#000" d="m-1624-1700c243-153 498-303 856-424 141 117 253 307 372 492-288 275-562 544-724 756-274-25-410-2-740-60 3-244 84-499 236-764zm2904-40c271 248 537 498 724 788-55 262-105 553-180 704-234-35-536-125-820-200-138-357-231-625-340-924 210-156 417-296 616-368zm-3273 3033a2376 2376 0 0 1-378-1392l59-7c54 342 124 674 311 928-36 179-2 323 51 458zm1197-1125c365 60 717 120 1060 180 106 333 120 667 156 1000-263 218-625 287-944 420-372-240-523-508-736-768 122-281 257-561 464-832zm3013 678a2376 2376 0 0 1-925 1147l-116-5c84-127 114-297 118-488 232-111 464-463 696-772 86 30 159 72 227 118zm-2287 1527a2376 2376 0 0 1-993-251c199 74 367 143 542 83 53 75 176 134 451 168z"></path>
    </svg>

    <script>
        const renderTimestamp = performance.now();
        const svg = document.getElementById('target-svg');
        const info = document.getElementById('info');
        const successMessage = document.getElementById('success-message');
        const finalStats = document.getElementById('final-stats');

        async function sendEvent(clickTime) {
            const timeElapsedMs = (clickTime - renderTimestamp).toFixed(2);
            const params = new URLSearchParams({ latencyMs: timeElapsedMs });
            const url = `/pass?${params.toString()}`;

            try {
                // Perform the fetch
                const response = await fetch(url, { method: 'GET' });

                // Update UI upon successful response (or just proceed if offline/demo)
                showSuccessState(timeElapsedMs);

            } catch (err) {
                console.warn("Server unavailable, but showing local success state.");
                showSuccessState(timeElapsedMs);
            }
        }

        function showSuccessState(latency) {
            // 1. Stop showing/remove the SVG
            svg.style.display = 'none';
            info.style.display = 'none';

            // 2. Show the success message
            successMessage.style.display = 'block';
            finalStats.innerText = `Pass time: ${latency}ms`;
        }

        svg.addEventListener('click', (e) => {
            const clickTime = performance.now();
            sendEvent(clickTime);
        });

        // Initial random placement
        svg.style.left = `${Math.random() * (window.innerWidth - 80)}px`;
        svg.style.top = `${Math.random() * (window.innerHeight - 80)}px`;
    </script>
</body>
</html>
"""

START_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live SSE Metrics Dashboard</title>
    <style>
        :root {
            --bg: #f4f7f6;
            --card-bg: #ffffff;
            --text: #333;
            --red-team: #ff4d4d;
            --blue-team: #007bff;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px;
            margin: 0;
        }

        .status-bar {
            margin-bottom: 20px;
            font-size: 0.9rem;
            padding: 5px 15px;
            border-radius: 20px;
            background: #ddd;
        }

        .status-connected { background: #d4edda; color: #155724; }
        .status-disconnected { background: #f8d7da; color: #721c24; }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 800px;
        }

        .card {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }

        .card h3 { margin: 0 0 10px 0; font-size: 0.9rem; text-transform: uppercase; color: #666; }
        .card .value { font-size: 2.5rem; font-weight: bold; }

        .red-value { color: var(--red-team); }
        .blue-value { color: var(--blue-team); }
        
        #total-players { color: #2c3e50; }
    </style>
</head>
<body>

    <h1>Performance Metrics</h1>
    <div id="status" class="status-bar">Connecting to stream...</div>

    <div class="dashboard">
        <div class="card">
            <h3>Total Players</h3>
            <div id="total-players" class="value">0</div>
        </div>

        <div class="card">
            <h3>Red Avg Pass Time</h3>
            <div id="red-latency" class="value red-value">0<span style="font-size: 1rem;">ms</span></div>
        </div>

        <div class="card">
            <h3>Blue Avg Pass Time</h3>
            <div id="blue-latency" class="value blue-value">0<span style="font-size: 1rem;">ms</span></div>
        </div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const playersEl = document.getElementById('total-players');
        const redEl = document.getElementById('red-latency');
        const blueEl = document.getElementById('blue-latency');

        // Initialize SSE Connection
        const eventSource = new EventSource('/metrics');

        eventSource.onopen = () => {
            statusEl.innerText = '● Connected Live';
            statusEl.className = 'status-bar status-connected';
        };

        eventSource.onmessage = (event) => {
            try {
                // Parse the JSON data sent from Python
                const data = JSON.parse(event.data);
                
                // Update the DOM elements
                playersEl.innerText = data.total_players;
                redEl.innerHTML = `${data.red_avg_latency.toFixed(2)}<span style="font-size: 1rem;">ms</span>`;
                blueEl.innerHTML = `${data.blue_avg_latency.toFixed(2)}<span style="font-size: 1rem;">ms</span>`;
                
            } catch (err) {
                console.error("Error parsing SSE data:", err);
            }
        };

        eventSource.onerror = () => {
            statusEl.innerText = '○ Disconnected - Reconnecting...';
            statusEl.className = 'status-bar status-disconnected';
        };
    </script>
</body>
</html>"""


class StrByteCache:
    _cache: Dict[str, bytes] = {}

    @classmethod
    def get(cls, string: str) -> bytes:
        if string not in cls._cache:
            cls._cache[string] = string.encode()
        return cls._cache[string]


class Request:
    def __init__(
        self,
        req_type: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[bytes],
    ):
        self.headers = headers
        self.body = body
        self.path = path
        self.req_type = req_type

    def __str__(self) -> str:
        return f"""Req_type: {self.req_type}
        Path: {self.path}
        Headers: 
{"\n".join([f"{i:>20}:{self.headers[i]:>30}" for i in self.headers])}\n\n"""

    @classmethod
    def parse_from_bytes(cls, blob: bytes) -> "Request":
        header, body = blob.split(b"\r\n\r\n")
        request_meta, *headers = header.split(b"\r\n")
        req_type, path, _ = request_meta.split(b" ")
        headers_dict = {}
        for header in headers:
            key, value = header.split(b":", 1)
            headers_dict[key.decode()] = value.decode()
        return Request(
            req_type.decode(),
            path.decode(),
            headers_dict,
            None if body == b"" else body,
        )


class Player:
    def __init__(
        self, name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        self.name = name
        self.reader = reader
        self.writer = writer
        self.event = asyncio.Event()
        self.latency: Optional[float] = None


class Team:
    def __init__(self, players: Dict[int, Player]):
        self.players = players

    def add(self, player: Player) -> int:
        with player_lock:
            player_id = len(self.players)
            self.players[player_id] = player
        return player_id


player_lock = Lock()
sort_team = "red"
red_team = Team(dict())
blue_team = Team(dict())
current_red_player: Optional[int] = None
current_blue_player: Optional[int] = None
status_code_str = {200: "OK", 404: "Not Found"}


def make_partial_response(
    status_code: int, content_type: str, cookies: Optional[List[str]]
) -> bytes:
    response = ""
    response += f"HTTP/1.1 {status_code} {status_code_str[status_code]}\r\n"
    date_header = formatdate(timeval=None, localtime=False, usegmt=True)
    response += f"Date: {date_header}\r\n"
    response += "Server: Somewhere\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += "Access-Control-Allow-Origin: *"
    response += "Connection: keep-alive\r\n"  # Explicitly keep open
    if cookies is not None:
        for cookie in cookies:
            response += f"Set-Cookie: {cookie}\r\n"
    return response.encode()


def make_response(html: bytes, status_code: int, content_type: str) -> bytes:
    response = ""
    response += f"HTTP/1.1 {status_code} {status_code_str[status_code]}\r\n"
    date_header = formatdate(timeval=None, localtime=False, usegmt=True)
    response += f"Date: {date_header}\r\n"
    response += "Server: Somewhere\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += "Access-Control-Allow-Origin: *"
    response += f"Content-Length: {len(html)}\r\n"
    response += "\r\n"

    response_bytes = bytearray(response.encode())
    response_bytes.extend(html)

    return bytes(response_bytes)


def avg_latency(players: Dict[int, Player]) -> float:
    filter_players = [
        player.latency for player in players.values() if player.latency is not None
    ]
    if len(filter_players) == 0:
        return 0
    return sum(filter_players) / len(filter_players)


def filter_not_set_players(players: Dict[int, Player]):
    with player_lock:
        available_players = [
            (player_id, players[player_id])
            for player_id in players
            if not players[player_id].event.is_set()
        ]
    return available_players


def give_pass():
    global current_blue_player
    global current_red_player
    while True:
        available_red_players: List[Tuple[int, Player]] = filter_not_set_players(
            red_team.players
        )
        available_blue_players: List[Tuple[int, Player]] = filter_not_set_players(
            blue_team.players
        )
        if len(available_red_players) > 0 and current_red_player is None:
            player_id, player = random.choice(available_red_players)
            current_red_player = player_id
            player.event.set()
        if len(available_blue_players) > 0 and current_blue_player is None:
            player_id, player = random.choice(available_blue_players)
            current_red_player = player_id
            player.event.set()


async def router(
    request: Request, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> Optional[bytes]:
    global sort_team
    global red_team
    global blue_team
    global current_blue_player
    global current_red_player
    match request.path.split("="):
        case ["/"]:
            return make_response(
                StrByteCache.get(INTRO_HTML), 200, "text/html; charset=utf-8"
            )
        case ["/?userName", name]:
            name: str = name
            player = Player(name, reader, writer)
            player_id = None
            team = deepcopy(sort_team)
            if sort_team == "red":
                player_id = red_team.add(player)
                sort_team = "blue"
            else:
                player_id = blue_team.add(player)
                sort_team = "red"

            hang_resp = make_partial_response(
                200,
                "text/html; charset=utf-8",
                [f"player_id={player_id};", f"team={team};"],
            )
            writer.write(hang_resp)
            await writer.drain()
            await player.event.wait()
            football_svg = StrByteCache.get(FOTTBALL_HTML)
            writer.write(f"Content-Length: {len(football_svg)}\r\n\r\n".encode())
            writer.write(football_svg)
            await writer.drain()
            return "ignore".encode()
        case ["/start"]:
            Thread(target=give_pass).start()

            return make_response(
                StrByteCache.get(START_HTML), 200, "text/html; charset=utf-8"
            )
        case ["/pass?latencyMs", latency]:
            player_id_str: str = request.headers["Cookie"]
            cookie1, cookie2, *_ = player_id_str.split(";")
            cookie1 = cookie1.strip()
            cookie2 = cookie2.strip()
            if cookie1.strip().startswith("player"):
                player_id_part = cookie1
                team_part = cookie2
            else:
                team_part = cookie1
                player_id_part = cookie2
            player_id = int(player_id_part.split("=")[-1])
            team_name: str = team_part.split("=")[-1]
            if team_name == "red":
                red_team.players[player_id].latency = float(latency)
                current_red_player = None
            else:
                blue_team.players[player_id].latency = float(latency)
                current_blue_player = None
        case ["/metrics"]:
            partial_resp = make_partial_response(200, "text/event-stream", None)
            writer.write(partial_resp)
            writer.write(StrByteCache.get("\r\n\r\n"))
            await writer.drain()
            while True:
                total_players = len(red_team.players) + len(blue_team.players)
                red_avg_latency = avg_latency(red_team.players)
                blue_avg_latency = avg_latency(blue_team.players)
                writer.write(
                    f"data: {json.dumps({'total_players': total_players, 'red_avg_latency': red_avg_latency, 'blue_avg_latency': blue_avg_latency})}\n\n".encode()
                )
                await writer.drain()
                await asyncio.sleep(1)


async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = await reader.read(REQUEST_SIZE)

    req = Request.parse_from_bytes(
        data,
    )
    print(req)
    response = await router(req, reader, writer)
    if response != b"ignore":
        if response is None:
            response = make_response(StrByteCache.get(""), 404, "text/plain")

        writer.write(response)
        await writer.drain()

    writer.close()
    await writer.wait_closed()


async def run_server():
    server = await asyncio.start_server(handle_connection, host="127.0.0.1", port=8080)
    async with server:
        await server.serve_forever()


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
