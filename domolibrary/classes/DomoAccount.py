# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoAccount.ipynb.

# %% auto 0
__all__ = ['DomoAccount_Config', 'DomoAccount_Config_AbstractCredential', 'DomoAccount_Config_DatasetCopy',
           'DomoAccount_Config_Governance', 'DomoAccount_Config_HighBandwidthConnector', 'DomoAccount_Config_AwsAthena',
           'AccountConfig', 'DomoAccount', 'DomoAccount_UpdateName_Error', 'DomoAccount_CreateAccount_Error',
           'DomoAccount_DeleteAccount_Error']

# %% ../../nbs/classes/50_DomoAccount.ipynb 3
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractclassmethod, abstractmethod

import datetime as dt
import re


import httpx

from fastcore.basics import patch_to

import domolibrary.utils.convert as cd
import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.account as account_routes


# %% ../../nbs/classes/50_DomoAccount.ipynb 5
class DomoAccount_Config(ABC):
    """DomoAccount Config abstract base class"""

    data_provider_type: str

    @classmethod
    @abstractmethod
    def _from_json(cls, obj):
        """convert accounts API response into a class object"""
        pass

    @abstractmethod
    def to_json(self):
        """convert class object into a format the accounts API expects"""
        pass

# %% ../../nbs/classes/50_DomoAccount.ipynb 6
@dataclass
class DomoAccount_Config_AbstractCredential(DomoAccount_Config):
    data_provider_type = "abstract-credential-store"
    credentials: dict

    @classmethod
    def _from_json(cls, obj):

        dd = util_dd.DictDot(obj)

        return cls(
            credentials=dd.credentials,
        )

    def to_json(self):
        return {"credentials": self.credentials}

# %% ../../nbs/classes/50_DomoAccount.ipynb 7
@dataclass
class DomoAccount_Config_DatasetCopy(DomoAccount_Config):
    domo_instance: str
    access_token: str = field(repr=False)

    data_provider_type = "dataset-copy"

    @classmethod
    def _from_json(cls, obj):

        dd = util_dd.DictDot(obj)

        return cls(access_token=dd.accessToken, domo_instance=dd.instance)

    def to_json(self):
        return {"accessToken": self.access_token, "instance": self.domo_instance}

# %% ../../nbs/classes/50_DomoAccount.ipynb 8
@dataclass
class DomoAccount_Config_Governance(DomoAccount_Config):
    domo_instance: str
    access_token: str = field(repr=False)

    data_provider_type = "domo-governance-d14c2fef-49a8-4898-8ddd-f64998005600"

    @classmethod
    def _from_json(cls, obj):

        dd = util_dd.DictDot(obj)

        return cls(access_token=dd.apikey, domo_instance=dd.customer)

    def to_json(self):
        return {"apikey": self.access_token, "customer": self.domo_instance}

# %% ../../nbs/classes/50_DomoAccount.ipynb 9
@dataclass
class DomoAccount_Config_HighBandwidthConnector(DomoAccount_Config):
    aws_access_key: str
    aws_secret_key: str = field(repr=False)
    s3_staging_dir: str
    region: str = "us-west-2"

    data_provider_type = "amazon-athena-high-bandwidth"

    @classmethod
    def _from_json(cls, obj):

        dd = util_dd.DictDot(obj)

        return cls(
            aws_access_key=dd.awsAccessKey,
            aws_secret_key=dd.awsSecretKey,
            s3_staging_dir=dd.s3StagingDir,
            region=dd.region,
        )

    def to_json(self):
        return {
            "awsAccessKey": self.aws_access_key,
            "awsSecretKey": self.aws_secret_key,
            "s3StagingDir": self.s3_staging_dir,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount.ipynb 10
@dataclass
class DomoAccount_Config_AwsAthena(DomoAccount_Config):
    aws_access_key: str
    aws_secret_key: str = field(repr=False)
    s3_staging_dir: str
    region: str = "us-west-2"
    workgroup: str
    data_provider_type = "aws-athena"

    @classmethod
    def _from_json(cls, obj):

        dd = util_dd.DictDot(obj)

        return cls(
            aws_access_key=dd.awsAccessKey,
            aws_secret_key=dd.awsSecretKey,
            s3_staging_dir=dd.s3StagingDir,
            region=dd.region,
            workgroup = dd.workgroup
        )

    def to_json(self):
        return {
            "awsAccessKey": self.aws_access_key,
            "awsSecretKey": self.aws_secret_key,
            "s3StagingDir": self.s3_staging_dir,
            "region": self.region,
            "workgroup" : self.workgroup
        }


# %% ../../nbs/classes/50_DomoAccount.ipynb 11
class AccountConfig(Enum):
    """
    Enum provides appropriate spelling for data_provider_type and config object.
    The name of the enum should correspond with the data_provider_type with hyphens replaced with underscores.
    """

    amazon_athena_high_bandwidth = DomoAccount_Config_HighBandwidthConnector

    abstract_credential_store = DomoAccount_Config_AbstractCredential

    dataset_copy = DomoAccount_Config_DatasetCopy

    domo_governance_d14c2fef_49a8_4898_8ddd_f64998005600 = DomoAccount_Config_Governance

    aws_athena = DomoAccount_Config_AwsAthena


# %% ../../nbs/classes/50_DomoAccount.ipynb 13
@dataclass
class DomoAccount:
    name: str
    data_provider_type: str

    id: int = None
    created_dt: dt.datetime = None
    modified_dt: dt.datetime = None
    auth: dmda.DomoAuth = field(repr=False, default=None)

    config: DomoAccount_Config = None

    @classmethod
    def _from_json(cls, obj: dict, auth: dmda.DomoAuth = None):
        """converts data_v1_accounts API response into an accounts class object"""

        dd = util_dd.DictDot(obj)

        return cls(
            id=dd.id,
            name=dd.displayName,
            data_provider_type=dd.dataProviderType,
            created_dt=cd.convert_epoch_millisecond_to_datetime(dd.createdAt),
            modified_dt=cd.convert_epoch_millisecond_to_datetime(dd.modifiedAt),
            auth=auth,
        )

    async def _get_config(
        self, session=None, debug_api: bool = None, return_raw: bool = False
    ):

        res_config = await account_routes.get_account_config(
            auth=self.auth,
            account_id=self.id,
            data_provider_type=self.data_provider_type,
            session=session,
            debug_api=debug_api,
        )

        if return_raw:
            return res_config

        enum_clean = re.sub("-", "_", self.data_provider_type)

        if not enum_clean in AccountConfig.__members__:
            return None

        self.config = AccountConfig[enum_clean].value._from_json(res_config.response)

        return self.config

# %% ../../nbs/classes/50_DomoAccount.ipynb 14
@patch_to(DomoAccount, cls_method=True)
async def get_from_id(
    cls,
    auth: dmda.DomoAuth,
    account_id: int,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_api: bool = False,
):

    res = await account_routes.get_account_from_id(
        auth=auth, account_id=account_id, session=session, debug_api=debug_api
    )
    if return_raw:
        return res

    if not res.is_success:
        return None

    obj = res.response
    acc = cls._from_json(obj, auth)

    await acc._get_config(session=session, debug_api=debug_api)

    return acc

# %% ../../nbs/classes/50_DomoAccount.ipynb 18
@patch_to(DomoAccount)
async def update_config(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    config: DomoAccount_Config = None,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):

    auth = auth or self.auth

    config = config or self.config

    res = await account_routes.update_account_config(
        auth=auth,
        account_id=self.id,
        data_provider_type=self.data_provider_type,
        config_body=config.to_json(),
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res

    await self._get_config(session=session, debug_api=debug_api)

    return self

# %% ../../nbs/classes/50_DomoAccount.ipynb 21
class DomoAccount_UpdateName_Error(de.DomoError):
    def __init__(self,
                 domo_instance,
                 status, message,
                 entity_id,
                 function_name="update_name",
                 ):

        super().__init__(function_name=function_name, entity_id=entity_id,
                         domo_instance=domo_instance, status=status, message=message)


@patch_to(DomoAccount)
async def update_name(
    self: DomoAccount,
    account_name: str = None,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):

    auth = auth or self.auth

    # print(auth, self.id, self.data_provider_type, self.config.to_json())

    res = await account_routes.update_account_name(
        auth=auth,
        account_id=self.id,
        account_name=account_name or self.name,
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise DomoAccount_UpdateName_Error(entity_id=self.id,
                                           domo_instance=auth.domo_instance,
                                           status=res.status,
                                           message=res.response,)

    self = await self.get_from_id(auth=auth, account_id=self.id)

    return self


# %% ../../nbs/classes/50_DomoAccount.ipynb 25
class DomoAccount_CreateAccount_Error(de.DomoError):
    def __init__(self,
                 entity_id,
                 domo_instance,
                 status,
                 message,
                 function_name="create_account",
                 ):

        super().__init__(function_name=function_name,
                         entity_id=entity_id,
                         domo_instance=domo_instance,
                         status=status, message=message)


# %% ../../nbs/classes/50_DomoAccount.ipynb 26
@patch_to(DomoAccount, cls_method=True)
def generate_create_body(cls, account_name, config):
    return {
        "displayName": account_name,
        "dataProviderType": config.data_provider_type,
        "name": config.data_provider_type,
        "configurations": config.to_json(),
    }


@patch_to(DomoAccount, cls_method=True)
async def create_account(
    cls: DomoAccount,
    account_name: str,
    config: DomoAccount_Config,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):

    body = cls.generate_create_body(account_name=account_name, config=config)

    res = await account_routes.create_account(
        auth=auth, config_body=body, debug_api=debug_api, session=session
    )

    if not res.is_success:
        raise DomoAccount_CreateAccount_Error(
            entity_id=account_name,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
        )

    return await cls.get_from_id(auth=auth, account_id=res.response.get("id"))


# %% ../../nbs/classes/50_DomoAccount.ipynb 27
class DomoAccount_DeleteAccount_Error(de.DomoError):
    def __init__(self,
                entity_id,
                 domo_instance,
                 status, message,
                 function_name="delete_account",
                 ):

        super().__init__(function_name=function_name, entity_id = entity_id,
                         domo_instance=domo_instance, 
                         status=status, 
                         message=message)


@patch_to(DomoAccount)
async def delete_account(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):

    auth = auth or self.auth

    res = await account_routes.delete_account(
        auth=auth, account_id=self.id, debug_api=debug_api, session=session
    )

    if not res.is_success:
        
        raise DomoAccount_DeleteAccount_Error(
            entity_id=self.id,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
        )

    return True
