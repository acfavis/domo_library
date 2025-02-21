# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/account.ipynb.

# %% auto 0
__all__ = ['get_accounts', 'GetAccount_NoMatch', 'get_account_from_id', 'AccountConfig_InvalidDataProvider', 'get_account_config',
           'update_account_config', 'update_account_name', 'create_account', 'delete_account',
           'ShareAccount_V1_AccessLevel', 'ShareAccount_V2_AccessLevel', 'generate_share_account_payload_v1',
           'generate_share_account_payload_v2', 'share_account_v2', 'share_account_v1']

# %% ../../nbs/routes/account.ipynb 3
from typing import Union
from enum import Enum
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/account.ipynb 4
async def get_accounts(auth: dmda.DomoAuth,
                       debug_api: bool = False, 
                       session: Union[httpx.AsyncClient, httpx.AsyncClient, None] = None) -> rgd.ResponseGetData:
    """retrieve a list of all the accounts the user has read access to.  Note users with "Manage all accounts" will retrieve all account objects"""
    
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        debug_api=debug_api,
        session=session
    )

# %% ../../nbs/routes/account.ipynb 7
class GetAccount_NoMatch(de.DomoError):
    def __init__(self, account_id, domo_instance, status, function_name = 'get_account_from_id'):

        message = f"account_id {account_id} not found"
        
        super().__init__(message = message, status = status, function_name = function_name , domo_instance = domo_instance)
    
async def get_account_from_id(auth: dmda.DomoAuth, account_id: int,
                              debug_api: bool = False, session: httpx.AsyncClient = None) -> rgd.ResponseGetData:
    """retrieves metadata about an account"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        debug_api=debug_api,
        session=session
    )

    if not res.is_success and (res.response == 'Forbidden' or res.response == 'Not Found'):
        raise GetAccount_NoMatch(
            account_id=account_id, domo_instance=auth.domo_instance, status=res.status)
    
    return res




# %% ../../nbs/routes/account.ipynb 11
class AccountConfig_InvalidDataProvider(Exception):
    def __init__(self, account_id:str, data_provider_type:str, domo_instance: str):
        message = f"Account - {account_id}, could not be retrieved with data_provider_type, '{data_provider_type}' from {domo_instance}"
        super().__init__( message)

async def get_account_config(auth: dmda.DomoAuth,
                             account_id: int,
                             data_provider_type: str ,
                             debug_api: bool = False, 
                             session: Union[httpx.AsyncClient, httpx.AsyncClient, None] = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        debug_api=debug_api,
        session=session
    )

    if res.response == {}:
        raise AccountConfig_InvalidDataProvider(account_id= account_id, data_provider_type= data_provider_type, domo_instance=auth.domo_instance)
    
    return res

# %% ../../nbs/routes/account.ipynb 14
async def update_account_config(auth: dmda.DomoAuth,
                                account_id: int,
                                config_body: dict,
                                data_provider_type: str,
                                debug_api: bool = False, 
                                session: httpx.AsyncClient = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    if debug_api:
        print(url)

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        body=config_body,
        debug_api=debug_api,
        session=session
    )

# %% ../../nbs/routes/account.ipynb 15
async def update_account_name(auth: dmda.DomoAuth,
                              account_id: int,
                              account_name: str,
                              debug_api: bool = False, 
                              session: httpx.AsyncClient = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/name"
    
    if debug_api:
        print(url)

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        body=account_name,
        content_type = "text/plain",
        debug_api=debug_api,
        session=session
    )

# %% ../../nbs/routes/account.ipynb 16
async def create_account(auth:dmda.DomoAuth, config_body:dict,
                         debug_api: bool = False, session: httpx.AsyncClient = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug_api:
        print(url)

    return await gd.get_data(
        auth=auth,
        url=url,
        method='POST',
        body = config_body,
        debug_api=debug_api,
        session=session
    )

# %% ../../nbs/routes/account.ipynb 17
async def delete_account(auth:dmda.DomoAuth,
                         account_id: str,
                         debug_api: bool = False, 
                         session: httpx.AsyncClient = None) -> rgd.ResponseGetData:
    
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"

    if debug_api:
        print(url)

    return await gd.get_data(
        auth=auth,
        url=url,
        method='DELETE',
        debug_api=debug_api,
        session=session
    )

# %% ../../nbs/routes/account.ipynb 19
class ShareAccount_V1_AccessLevel(Enum):
    CAN_VIEW = 'READ'


class ShareAccount_V2_AccessLevel(Enum):
    CAN_VIEW = 'CAN_VIEW'
    CAN_EDIT = 'CAN_EDIT'
    CAN_SHARE = 'CAN_SHARE'


def generate_share_account_payload_v1(user_id: int, access_level: str):
    return {"type": "USER", "id": user_id, "permissions": [ShareAccount_V1_AccessLevel[access_level].value]}


def generate_share_account_payload_v2(user_id: int,
                                      access_level: str
                                      ):

    return {"type": "USER", "id": user_id, "accessLevel": ShareAccount_V2_AccessLevel[access_level].value}


# %% ../../nbs/routes/account.ipynb 21
async def share_account_v2(auth: dmda.DomoAuth,
                           account_id: str,
                           share_payload: dict,
                           debug_api: bool = False,
                           session: httpx.AsyncClient = None
                           ):

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        body=share_payload,
        debug_api=debug_api,
        session=session
    )


async def share_account_v1(auth: dmda.DomoAuth,
                           account_id: str,
                           share_payload: dict,
                           debug_api: bool = False,
                           session: httpx.AsyncClient = None
                           ):

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/share"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        body=share_payload,
        debug_api=debug_api,
        session=session
    )

