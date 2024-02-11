from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI
import httpx


app = FastAPI()


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
        vi = data['violent']
        if vi:
            violent = f" AND ucr_code in("\
                      f"'100', '101', '107', '400', '401', "\
                      f"'200', '201', '202', '203', '204', '205', '206', '207', '208', "\
                      f"'300', '301', '302', '303', '304', '305', "\
                      f"'402', '403', '404', '405', '406', '407', '408', '409', '410', '411', "\
                      f"'805', '900', '901', '902', '903', '906', '909', '910', '911', "\
                      f"'1700', '1701', '1702', '1703', '1707', '1708', '1709', '1710', '1711', '1712', '1713', "\
                      f"'1714', '1715', '1716', '1717', '1718', '1719', '1720', '1721', '1722', '1723', '1724', "\
                      f"'2004', '2010', '2011', '2012', '2013', '2014', "\
                      f"'2404', '2406', '2407', '2408', '2409', '2410', "\
                      f"'2701', '2702', '2703', '2704', '2705', '2706', '2731', '2732', "\
                      f"'2800', '2801', '2802', '2803', '2804', '2805', "\
                      f"'4199')"
            path += violent
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
@app.get('/count/{zip}/{co}')
def count_all(zip: int, co: int):
    data = {
        'zip_code': zip,
        'select': 'count(incident_report_number)',
        'cutoff': co, 
    }
    path = make_path(data)
    response = httpx.get(path)
    match response.status_code:
        case 200:
            r = response.json()[0]
        case _:
            r = {'status_code': response.status_code}
    return r


# return a count of 'violent' crimes
@app.get('/count/violent/{zip}/{co}')
def count_violent(zip: int, co: int):
    data = {
        'zip_code': zip,
        'select': 'count(incident_report_number)',
        'cutoff': co,
        'violent': True,
    }
    path = make_path(data)
    response = httpx.get(path)
    match response.status_code:
        case 200:
            r = response.json()[0]
        case _:
            r = {'status_code': response.status_code}
    return r


@app.get('/')
def landing():
    data = {'message': 'append a zip code to url for crime count (last two years)'}
    return data
