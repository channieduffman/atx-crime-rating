import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI
from geopy.geocoders import Nominatim
import httpx
from urllib.parse import quote


app = FastAPI()


# generate a formatted date string for a SoQL query
def make_cutoff(years: int) -> str:
    today = date.today()
    threshold = today - relativedelta(years=years)
    th = threshold.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    return th


# generate URL query 
# assumes 'co' is properly formatted SoQL date string as defined by SODA
def make_path(zc: int | None, co: str, tail: str | None) -> str:
    path = "https://data.austintexas.gov/resource/fdj4-gpfu.json?"
    select = f"$select=count(*)"
    # zip code will be not be used for address search endpoint
    if zc:
        zip = f"&zip_code={zc}"
        select += zip
    where = f"&$where=occ_date_time%20%3E%20%27{co}%27"
    path = path + select + where
    # 'tail' allows for additional query params to be added
    if tail:
        path += tail
    return path

# create a dictionary of query strings for filtering violent crime
def filter_violent() -> dict:

    # UCR codes for violent crimes as defined by the FBI
    violent = {
        "murder": [
            "100",
            "101",
            "102",
        ],
        "rape": [
            "200",
            "202",
            "203",
            "204",
            "206",
            "207",
        ],
        "aggravated_robbery": [
            "300",
            "302",
            "303",
            "305",
        ],
        "aggravated_assault": [
            "402",
            "403",
            "405",
            "406",
            "407",
            "408",
            "409",
            "410",
            "411",
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
        ]
    }

    queries = {}

    # add specific codes to query string and format
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

import re

def validate_address(address):
    # Regular expression to match a typical physical address pattern
    pattern = r'^\d+\s+[\w\s]+\s+\w+[\.,]?\s+\w+\s*,?\s*\w*\s*,?\s*\w+\s*\d*,?\s*\w*$'
    
    # Compile the regular expression
    regex = re.compile(pattern)
    
    # Check if the address matches the pattern
    if regex.match(address):
        return True
    else:
        return False


# coroutine for launching requests asynchronously
# returns a single key value pair as dictionary
async def make_request(base: str, q: str, k: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(base + q)
        return {k: res.json()[0]["count"]}


# gather make_request() coros
async def make_requests(base: str, qs: dict):
    # returns a list of dictionaries each with a single key: value pair
    return await asyncio.gather(*[make_request(base, qs[k], k) for k in qs])


# return a breakdown of reported violent crimes
@app.get("/zipcode/{zc}/{cut}")
async def get_violent(zc: int, cut: int):
    try:
        co = make_cutoff(cut)
        base = make_path(zc, co, None)
        # generate dict of queries to launch with make_requests()
        vq = filter_violent()
        results = await make_requests(base, vq)
        categories = {}
        for res in results:
            k, v = next(iter(res.items()))
            categories[k] = v
        data = {
            "zip_code": str(zc),
            "number_of_years": str(cut),
            "reported_violent_crime_count": str(sum([int(categories[k]) for k in categories])),
            "by_category": categories
        }
    except Exception as e:
        data = {
            "error": e.__repr__()     
        }

    return data


@app.get("/address/{addr}/{co}")
async def count_within_radius(addr: str, co: int):
    try:
        data = {}
        geolocator = Nominatim(user_agent="my_app")
        loc = geolocator.geocode(addr)
        if loc and hasattr(loc, "latitude") and hasattr(loc, "longitude"):
            lat = loc.latitude
            lon = loc.longitude

            max_y = lat + (1 / 120)
            min_y = lat - (1 / 120)
            max_x = lon + (1 / 120)
            min_x = lon - (1 / 120)

            tail = f" AND latitude < {max_y} AND latitude > {min_y} AND longitude < {max_x} AND longitude > {min_x}"
            cut = make_cutoff(co)
            base = make_path(None, cut, quote(tail))

            # generate dict of queries to launch with make_requests()
            vq = filter_violent()
            results = await make_requests(base, vq)
            categories = {}
            for res in results:
                k, v = next(iter(res.items()))
                categories[k] = v
            data = {
                "last_n_years": str(co),
                "square_nautical_miles": "1",
                "reported_violent_crime_count": str(sum([int(categories[k]) for k in categories])),
                "by_category": categories
            }
    except Exception as e:
        data = {
            "error": e.__repr__()     
        }
        
    return data
