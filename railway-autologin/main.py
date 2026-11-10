"""
Daily Angel One login for a hosted OpenAlgo, run as a Railway cron service (08:30 IST, Mon-Fri).

It does what you do in the browser: logs in to OpenAlgo, then submits OpenAlgo's Angel form
(client code, PIN, a fresh TOTP). Scheduled strategies waiting for the login start by themselves.

Variables (set on this cron service in Railway, never in code):
    OPENALGO_URL          e.g. https://openalgo-production-bfa6.up.railway.app
    OPENALGO_USERNAME     your OpenAlgo login
    OPENALGO_PASSWORD
    ANGEL_CLIENT_CODE
    ANGEL_PIN
    ANGEL_TOTP_SECRET     the setup key behind your authenticator code, not a 6-digit code
    OPENALGO_API_KEY      optional: checks the broker answers and that Analyzer (sandbox) mode is on

Safety: Angel locks an account after repeated wrong attempts, so it tries Angel at most twice, and
only retries when the error names the TOTP (a code that expired in flight). Nothing secret is printed.
Exit code 1 on failure, so Railway marks the run failed.

Standard library only: TOTP is RFC 6238 (HMAC-SHA1, 6 digits, 30 s), the scheme authenticator apps use.
"""
import base64
import hashlib
import hmac
import http.cookiejar
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


def log(msg):
    print(f"[{datetime.now(IST):%Y-%m-%d %H:%M:%S} IST] {msg}", flush=True)


def totp(secret, at=None):
    key = base64.b32decode(secret.replace(" ", "").upper() + "=" * (-len(secret.replace(" ", "")) % 8))
    digest = hmac.new(key, struct.pack(">Q", int((at or time.time()) // 30)), hashlib.sha1).digest()
    o = digest[-1] & 0x0F
    return f"{(struct.unpack('>I', digest[o:o + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def fresh_totp(secret):
    """A code with at least 6 seconds left, so it does not expire between here and Angel."""
    left = 30 - int(time.time()) % 30
    if left < 6:
        time.sleep(left + 1)
    return totp(secret)


class Client:
    def __init__(self, base):
        self.base = base.rstrip("/")
        self.http = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(self, method, path, form=None, body=None, headers=None):
        h = {"Accept": "application/json", "Referer": self.base + "/login", "Origin": self.base, **(headers or {})}
        data = None
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            h["Content-Type"] = "application/x-www-form-urlencoded"
        elif body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=data, headers=h, method=method)
        try:
            with self.http.open(req, timeout=60) as r:
                status, text = r.status, r.read().decode(errors="replace")
        except urllib.error.HTTPError as e:
            status, text = e.code, e.read().decode(errors="replace")
        except (urllib.error.URLError, TimeoutError) as e:     # down, restarting, DNS: status 0
            return 0, {"message": f"cannot reach OpenAlgo ({getattr(e, 'reason', e)})"}
        try:
            return status, json.loads(text)
        except ValueError:
            return status, {"message": text[:200]}


def need(name):
    v = os.getenv(name, "").strip()
    if not v:
        sys.exit(f"{name} is not set on this Railway service")
    return v


def main():
    base = need("OPENALGO_URL")
    user, password = need("OPENALGO_USERNAME"), need("OPENALGO_PASSWORD")
    client_code, pin, secret = need("ANGEL_CLIENT_CODE"), need("ANGEL_PIN"), need("ANGEL_TOTP_SECRET")
    totp(secret)                                    # a malformed key fails here, before any login attempt
    c = Client(base)

    for _ in range(10):                             # the app may be restarting: wait up to ~5 minutes
        status, t = c.call("GET", "/auth/csrf-token")
        if status == 200:
            break
        log(f"OpenAlgo not answering yet (HTTP {status}); waiting")
        time.sleep(30)
    else:
        sys.exit("OpenAlgo did not answer for 5 minutes; is the service running?")

    token = t.get("csrf_token", "")                 # /auth/login checks it too
    status, r = c.call("POST", "/auth/login", form={"username": user, "password": password, "csrf_token": token},
                       headers={"X-CSRFToken": token})
    if r.get("status") == "totp_required":
        sys.exit("OpenAlgo asks for its own 2-factor code at login; this script does not handle that yet")
    if status != 200 or r.get("status") != "success":
        sys.exit(f"OpenAlgo login refused: {r.get('message')}")
    if r.get("redirect") == "/dashboard":
        log("Angel session from earlier today is still valid; nothing to do")
    else:
        for attempt in (1, 2):
            _, t = c.call("GET", "/auth/csrf-token")
            status, r = c.call("POST", "/angel/callback",
                               form={"userid": client_code, "pin": pin, "totp": fresh_totp(secret),
                                     "csrf_token": t.get("csrf_token", "")},
                               headers={"X-CSRFToken": t.get("csrf_token", ""), "Referer": base + "/broker/angel/totp"})
            if status == 200 and r.get("status") == "success":
                log("Angel connected")
                break
            msg = str(r.get("message"))
            if attempt == 1 and "totp" in msg.lower():
                log(f"Angel refused the code ({msg}); one retry with the next code")
                time.sleep(31)
                continue
            sys.exit(f"Angel login refused: {msg}. Not retrying, so the account is not locked.")

    key = os.getenv("OPENALGO_API_KEY", "").strip()
    if key:
        _, p = c.call("POST", "/api/v1/ping", body={"apikey": key})
        if p.get("status") != "success":
            sys.exit(f"Angel is connected, but OPENALGO_API_KEY was refused ({p.get('message')}). "
                     "Generate a key at /apikey and put it on this Railway service.")
        _, a = c.call("POST", "/api/v1/analyzer", body={"apikey": key})
        mode = (a.get("data") or {}).get("mode", "?")
        log(f"check: broker {((p.get('data') or {}).get('broker') or '?')}, mode {mode}")
        if not (a.get("data") or {}).get("analyze_mode"):
            sys.exit("Logged in, but Analyzer (sandbox) mode is OFF: the strategies will refuse to start")


if __name__ == "__main__":
    main()
