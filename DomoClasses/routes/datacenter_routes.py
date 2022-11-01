import aiohttp
from pprint import pprint

from .get_data import get_data, looper
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


def generate_search_datacenter_body(entities_list: list[str] = ['DATASET'],
                                    filters: list[dict] = None,
                                    combineResults: bool = True,
                                    count: int = 10,
                                    offset: int = 0):
    return {
        "entities": entities_list,
        "filters": filters or [],
        "combineResults": combineResults,
        "query": "*",
        "count": count,
        "offset": offset}


async def search_datacenter(full_auth: DomoFullAuth,
                            arr_fn: callable,
                            alter_maximum_fn: callable,
                            maximum: int = None,
                            body: dict = None,
                            session: aiohttp.ClientSession = None,
                            limit=1000,
                            debug: bool = False, log_result: bool = False) -> ResponseGetData:
    is_close_session = False
    if not session:
        session = aiohttp.ClientSession()
        is_close_session = True

    if not body:
        body = {
            "entities": ["DATASET"],
            "filters": [],
            "combineResults": False,
            "query": "*"}

    url = f"https://{full_auth.domo_instance}.domo.com/api/search/v1/query"

    if debug:
        print(url)
        pprint(body)

    res = await looper(auth=full_auth,
                       session=session,
                       url=url,
                       body=body,
                       offset_params={
                           'offset': 'offset',
                           'limit': 'count'
                       },
                       arr_fn=arr_fn,
                       alter_maximum_fn=alter_maximum_fn,
                       method='POST',
                       offset_params_in_body=True,
                       limit=limit,
                       maximum=maximum,
                       debug=debug)

    if is_close_session:
        await session.close()

    return res
