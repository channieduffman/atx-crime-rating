import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI
import geopy
from geopy.geocoders import Nominatim
import httpx
from math import sqrt, pow
from urllib.parse import quote


app = FastAPI()


import re


def validate_address(address):
    # Regular expression to match a typical physical address pattern
    pattern = r"^\d+\s+[\w\s]+\s+\w+[\.,]?\s+\w+\s*,?\s*\w*\s*,?\s*\w+\s*\d*,?\s*\w*$"

    # Compile the regular expression
    regex = re.compile(pattern)

    # Check if the address matches the pattern
    if regex.match(address):
        return True
    else:
        return False



@app.get("/v2/address/{addr}")
async def get_v2(addr: str):

    base = "https://data.austintexas.gov/resource/fdj4-gpfu.json?"

    today = date.today()
    threshold = today - relativedelta(years=2)
    th = threshold.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    timeframe = f"$where=occ_date_time > '{th}'"
    
    murder = ['100', '101', '102']
    rape = ['200', '202', '203', '204', '206', '207']
    robbery = ['300', '302', '303', '305']
    assault = ['402', '403', '405', '406', '407', '408', '409', '410', '411', '900']
    sexual_assault = ['1700', '1701', '1707', '1708', '1709', '1710', '1712', '1714', '1715', '1716', '1718', '1719', '1720', '1721', '1722', '1724']

    geolocator = Nominatim(user_agent="my_app")
    loc = geolocator.geocode(addr)
    lat = loc.latitude
    lon = loc.longitude

    location = geolocator.geocode("201 W 4th ST Austin TX")
    print(location)

    # represents a radius in nautical miles
    radius = 4 

    # limit search area to a 2 * dist by 2 * dist square
    max_y = lat + (radius * (1 / 60))
    min_y = lat - (radius * (1 / 60))
    max_x = lon + (radius * (1 / 60))
    min_x = lon - (radius * (1 / 60))

    proximity = f" AND latitude < {max_y} AND latitude > {min_y} AND longitude < {max_x} AND longitude > {min_x}"

    violent = [
        " AND ucr_code in('100', '101', '102')",
        " AND ucr_code in('200', '202', '203', '204', '206', '207')",
        " AND ucr_code in('300', '302', '303', '305')",
        " AND ucr_code in('402', '403', '405', '406', '407', '408', '409', '410', '411', '900')",
        " AND ucr_code in('1700', '1701', '1707', '1708', '1709', '1710', '1712', '1714', '1715', '1716', '1718', '1719', '1720', '1721', '1722', '1724')",
    ]

    path = base + timeframe # + proximity

    results = httpx.get(path + " AND ucr_code in('200', '202', '203', '204', '206', '207')")
    # results = await make_requests(path, violent)
    # data = [[r for r in res if is_within_range(loc, r, radius)] for res in results]
    return results.json()


# assumes 'center' is geopy Location,
# and 'record' is a dataset entry with lat/lon
def is_within_range(center, record, rad: int) -> bool:
    # convert dist to decimal degree
    # one nautical mile is one minute (1 / 60 of a degree)
    z = rad * (1 / 60)
    # normalize x and y coordinates
    x = float(record["latitude"]) - center.latitude
    y = float(record["longitude"]) - center.longitude
    # check with distance formula
    if sqrt(pow(x, 2) + pow(y, 2)) <= z:
        return True
    else:
        return False


# coroutine for launching requests asynchronously
async def make_request(base: str, filter: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(base + filter)
        return res.json()


# gather make_request() coros
async def make_requests(base: str, filters: list):
    return await asyncio.gather(*[make_request(base, filter) for filter in filters])
