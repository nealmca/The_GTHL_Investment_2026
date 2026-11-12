import json, urllib.request, datetime

def chart(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]

def load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default

H = json.load(open("holdings.json"))["holdings"]
old = load("prices.json", {})
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
out = {"updated": now, "quotes": dict(old.get("quotes", {})),
       "usdcad": old.get("usdcad"), "spx": old.get("spx")}

for h in H:
    try:
        r = chart(h["symbol"])
        m = r["meta"]
        closes = [c for c in r["indicators"]["quote"][0]["close"] if c is not None]
        prev = closes[-2] if len(closes) >= 2 else None
        out["quotes"][h["symbol"]] = {"price": m["regularMarketPrice"],
            "prev": prev, "currency": m.get("currency")}
    except Exception as e:
        print("failed", h["symbol"], e)

try:
    out["usdcad"] = chart("USDCAD=X")["meta"]["regularMarketPrice"]
except Exception as e:
    print("fx failed", e)

try:
    out["spx"] = chart("%5EGSPC")["meta"]["regularMarketPrice"]
except Exception as e:
    print("spx failed", e)

json.dump(out, open("prices.json", "w"), indent=1)

# chart history: add a snapshot only if something changed
hist = load("history.json", [])
snap = {"t": now, "spx": out["spx"],
        "p": {k: v["price"] for k, v in out["quotes"].items()}}
if out["spx"] and (not hist or (hist[-1]["spx"], hist[-1]["p"]) != (snap["spx"], snap["p"])):
    hist.append(snap)
    json.dump(hist, open("history.json", "w"), separators=(",", ":"))
