from datetime import date
from dateutil.relativedelta import relativedelta
import sys
from fastapi import FastAPI
import httpx

from violent import violent

app = FastAPI()

print(sys.path)


# generate a formatted date cutoff for a SoQL query
def make_cutoff(years: int):
    today = date.today()
    threshold = today - relativedelta(years=years)
    th = threshold.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    return th


# generate URL query from dictionary and ignore missing keys
def make_path(data: dict):
    path = 'https://data.austintexas.gov/resource/fdj4-gpfu.json?'
    
    try:
        zi = data['zip_code']
        zip_code = f'&zip_code={zi}'
        path += zip_code
    except KeyError:
        pass

    try:
        se = data['select']
        select = f'&$select={se}'
        path += select
    except KeyError:
        pass

    try:
        cu = data['cutoff']
        co = make_cutoff(cu)
        cutoff = f'&$where=occ_date_time%20%3e%20%27{co}%27'
        path += cutoff
    except KeyError:
        pass

    try:
        li = data['limit'] 
        limit = f'&$limit={li}'
        path += limit
    except KeyError:
        pass

    return path


# absolute crime report count over two years
@app.get('/absolute/{zip}/{co}')
async def count_all(zip: int, co: int):

    async with httpx.AsyncClient() as client:
        data = {
            'zip_code': zip,
            'select': 'count(incident_report_number)',
            'cutoff': co
        }
        path = make_path(data)
        response = await client.get(path)
        match response.status_code:
            case 200:
                r = response.json()[0]
            case _:
                r = {'status_code': response.status_code}

    # response.json() is a list of JSON objects
    # return the first (and only) object
    return r


# return a count of 'violent' crimes
@app.get('/absolute/violent/{zip}/{co}')
async def count_violent(zip: int, co: int):
    
    async with httpx.AsyncClient() as client:
        lim = await count_all(zip, co)
        limit = int(lim['count_incident_report_number'])
        data = {
            'zip_code': zip,
            'select': 'ucr_code',
            'cutoff': co,
            'limit': limit
        }
        path = make_path(data)
        response = await client.get(path)
        v = [r['ucr_code'] for r in response.json() if r['ucr_code'] in violent]
        d = {'count_violent_incident_report_number': str(len(v))} 
    
    # FastAPI JSON-encodes the response
    return d


@app.get('/')
def landing():
    data = {'message': 'append a zip code to url for crime count (last two years)'}
    return data
