import json, urllib.request, datetime

H = json.load(open("holdings.json"))["holdings"]
out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "quotes": {}}

for h in H:
    sym = h["symbol"]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        meta = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]["meta"]
        out["quotes"][sym] = {
            "price": meta["regularMarketPrice"],
            "prev": meta.get("chartPreviousClose"),
            "currency": meta.get("currency"),
        }
    except Exception as e:
        print("failed", sym, e)

# keep old quotes for any symbol that failed this run
try:
    old = json.load(open("prices.json"))["quotes"]
    for k, v in old.items():
        out["quotes"].setdefault(k, v)
except Exception:
    pass

json.dump(out, open("prices.json", "w"), indent=1)
