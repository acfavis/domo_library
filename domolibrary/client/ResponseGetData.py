# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/client/99_ResponseGetData.ipynb.

# %% auto 0
__all__ = ['API_Response', 'STREAM_FILE_PATH', 'ResponseGetData']

# %% ../../nbs/client/99_ResponseGetData.ipynb 2
# pylint: disable=no-member
from dataclasses import dataclass, field
from typing import Optional

import json
import orjson


import asyncio
import requests
import aiohttp

from fastcore.utils import patch_to, patch

# %% ../../nbs/client/99_ResponseGetData.ipynb 4
API_Response = any


@dataclass
class ResponseGetData:
    """preferred response class for all API Requests"""

    status: int
    response: API_Response
    is_success: bool
    auth: dict = field(repr = False, default=None)

    def set_response(self, response):
        self.response = response

# %% ../../nbs/client/99_ResponseGetData.ipynb 8
@patch_to(ResponseGetData, cls_method=True)
def _from_requests_response(
    cls, res: requests.Response  # requests response object
) -> ResponseGetData:
    """returns ResponseGetData"""

    # JSON responses
    if res.ok and "application/json" in res.headers.get("Content-Type", {}):
        return cls(status=res.status_code, response=res.json(), is_success=True)

    # default text responses
    elif res.ok:
        return cls(status=res.status_code, response=res.text, is_success=True)

    # errors
    return cls(status=res.status_code, response=res.reason, is_success=False)

# %% ../../nbs/client/99_ResponseGetData.ipynb 12
@patch_to(ResponseGetData, cls_method=True)
def _from_httpx_response(
    cls, res: requests.Response,  # requests response object
    auth : Optional[any] = None,
    debug_api : bool = False
) -> ResponseGetData:
    """returns ResponseGetData"""

    # JSON responses
    ok = True if res.status_code <= 299 and res.status_code >= 200 else False
    
    if ok and "application/json" in res.headers.get("Content-Type", {}):
        return cls(status=res.status_code, response=res.json(), is_success=True, auth = auth)

    # default text responses
    elif ok:
        return cls(status=res.status_code, response=res.text, is_success=True, auth = auth)

    # errors
    return cls(status=res.status_code, response=res.reason_phrase, is_success=False, auth=auth)


# %% ../../nbs/client/99_ResponseGetData.ipynb 15
STREAM_FILE_PATH = '__large-file.json'

async def _write_stream(res: aiohttp.ClientResponse,
                        file_name: str = STREAM_FILE_PATH,
                        stream_chunks=10):
    
    print(type(res), type(res.content), stream_chunks)

    index = 0
    with open(file_name, 'wb') as fd:
        async for chunk in res.content.iter_chunked(1024):
            index +=1
            print(f"writing chunk - {index}")
            fd.write(chunk)

            print(res.content.at_eof())
        
    print('done writing stream')
    
    return None


async def _read_stream(file_name : str = STREAM_FILE_PATH):
    with open(STREAM_FILE_PATH, "rb") as f:
        return f.read()


# %% ../../nbs/client/99_ResponseGetData.ipynb 16
@patch(cls_method=True)
async def _from_aiohttp_response(
    cls: ResponseGetData, 
    res: aiohttp.ClientResponse,  # requests response object
    auth : Optional[any] = None,
    process_stream: bool = False,
    stream_chunks : int = 10,
    debug_api : bool = False
) -> ResponseGetData:

    """async method returns ResponseGetData"""
    if debug_api:
        print( f"ResponseGetData: res.ok = {res.ok} , res.status = {res.status}" )
    

    try:
        data = None

        if process_stream:
            await _write_stream(res = res, stream_chunks = stream_chunks)
            data =await _read_stream()
        
        else:        
            data = await res.text()
    
        if debug_api:
            print('converting to text complete')
    
    except asyncio.TimeoutError as e:
        print(f"ResponseGetDataError: {str(e)} , trying content.read")

        data = await res.content.read()

    if res.ok and "application/json" in res.headers.get("Content-Type", {}):
        return cls(status=res.status, response= orjson.loads(data), is_success=True, auth = auth)

    elif res.ok:
        return cls(status=res.status, response= data, is_success=True, auth = auth)

    # response is error
    else:
        return cls(status=res.status, response=res.reason, is_success=False, auth = auth)

# %% ../../nbs/client/99_ResponseGetData.ipynb 20
@patch(cls_method=True)
async def _from_looper(cls: ResponseGetData,
                       res: ResponseGetData,  # requests response object
                       array: list
                       ) -> ResponseGetData:

    """async method returns ResponseGetData"""

    if res.is_success:
        res.response = array
        return res

    # response is error
    else:
        return res

