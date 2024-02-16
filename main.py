import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI
import httpx
from urllib.parse import quote

import time


app = FastAPI()


# generate a formatted date string for a SoQL query
def make_cutoff(years: int) -> str:
    today = date.today()
    threshold = today - relativedelta(years=years)
    th = threshold.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    return th


def filter_violent() -> dict:

    violent = {
        "murder": [
            "100",
            "101" "102",
        ],
        "rape": [
            "200",
            "202",
            "203",
            "204",
            "206",
            "207",
        ],
        "agg_robbery": [
            "300",
            "302",
            "303",
            "305",
        ],
        "agg_assault": [
            "402",
            "403",
            "405",
            "406",
            "407",
            "408",
            "409",
            "410",
            "411",
            # arson / assault with injury
            "805",
            "900",
        ],
        "sexual_assault": [
            "1700",
            "1701",
            "1707",
            "1708",
            "1709",
            "1710",
            "1712",
            "1714",
            "1715",
            "1716",
            "1718",
            "1719",
            "1720",
            "1721",
            "1722",
            "1724",
        ],
        "kidnapping": [
            "2801",
        ],
        "trafficking": [
            "4199",
        ],
    }

    queries = {}

    for item in violent:
        v = " AND ucr_code in("
        for index, value in enumerate(violent[item]):
            if index > 0 and index < len(violent[item]) - 1:
                v = v + ", " + value
            elif index == 0 and index == len(violent[item]) - 1:
                v = v + value + ")"
            elif index == len(violent[item]) - 1:
                v = v + ", " + value + ")"
            else:
                v = v + value
        queries[item] = quote(v)

    return queries


# generate URL query from dictionary
def make_path(zc: int, co: str, tail: str | None) -> str:
    path = "https://data.austintexas.gov/resource/fdj4-gpfu.json?"
    select = f"$select=count(*)&zip_code={zc}"
    where = f"&$where=occ_date_time%20%3E%20%27{co}%27"
    path = path + select + where
    if tail is not None:
        path += tail
    return path


# coroutine for launching requests asynchronously
async def make_request(base: str, q: str, k: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(base + q)
        return {k: res.json()[0]["count"]}


# gather make_request() coros
async def make_requests(base: str, qs: dict):
    return await asyncio.gather(*[make_request(base, qs[k], k) for k in qs])


# return a breakdown of reported violent crimes
@app.get("/{zc}/{cut}")
async def count_violent(zc: int, cut: int):
    co = make_cutoff(cut)
    base = make_path(zc, co, None)
    vq = filter_violent()
    try:
        results = await make_requests(base, vq)
    except Exception as e:
        results = e

    return results


# absolute crime report count over two years
@app.get("/count/all/{zip}/{cut}")
def count_all(zip: int, cut: int):
    start = time.time()
    co = make_cutoff(cut)
    path = make_path(zip, co, None)
    response = httpx.get(path)
    return response.json(), time.time() - start
