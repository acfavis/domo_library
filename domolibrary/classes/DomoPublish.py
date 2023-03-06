# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoPublish.ipynb.

# %% auto 0
__all__ = ['DomoPublication_Subscription', 'DomoPublications', 'DomoPublication_Content', 'DomoPublication_UnexpectedContentType',
           'DomoPublication']

# %% ../../nbs/classes/50_DomoPublish.ipynb 2
from fastcore.basics import patch_to

# %% ../../nbs/classes/50_DomoPublish.ipynb 3
from dataclasses import dataclass, field

from typing import Optional

import datetime as dt
import asyncio
import httpx

# import importlib
# import json
# import uuid
# import time

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.publish as publish_routes

# import Library.DomoClasses.DomoDataset as dmda
# import Library.DomoClasses.DomoLineage as dmdl

# %% ../../nbs/classes/50_DomoPublish.ipynb 5
@dataclass
class DomoPublication_Subscription:
    subscription_id: str
    publication_id: str
    domain: str
    created_dt: Optional[dt.datetime] = None

    @classmethod
    def _from_json(cls, json):

        dd = json
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(json)

        return cls(
            subscription_id=dd.id,
            publication_id=dd.publicationId,
            domain=dd.domain,
            created_dt=dt.datetime.fromtimestamp(dd.created / 1000)
            if dd.created
            else None,
        )




# %% ../../nbs/classes/50_DomoPublish.ipynb 7
class DomoPublications:
    auth : dmda.DomoAuth

# %% ../../nbs/classes/50_DomoPublish.ipynb 8
@dataclass
class DomoPublication_Content:
    content_id: str
    entity_type: str
    entity_id: str
    entity_domain: str
    is_v2: bool
    is_direct_content: bool

    @classmethod
    def _from_json(cls, obj: dict):

        dd = obj
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(obj)

        dmpc = cls(
            content_id=dd.id,
            entity_type=dd.content.type,
            entity_id=dd.content.domoObjectId,
            entity_domain=dd.content.domain,
            is_v2=dd.isV2,
            is_direct_content=dd.useDirectContent,
        )

        return dmpc

    def to_api_json(self):
        temp_dict = {
            "domain": self.entity_domain,
            "domoObjectId": self.entity_id,
            # "customerId": self.entity_domain,
            "type": self.entity_type,
        }
        return temp_dict


# %% ../../nbs/classes/50_DomoPublish.ipynb 10
class DomoPublication_UnexpectedContentType(Exception):
    def __init__(self, publication_id, content_type, domo_instance):
        super().__init__(f"DomoPublication_Instantiation: Unexpected content type {content_type} in publication {publication_id} in {domo_instance}")

# %% ../../nbs/classes/50_DomoPublish.ipynb 11
@dataclass
class DomoPublication:
    id: str
    name: str
    description: str
    is_v2: bool
    created_dt: dt.datetime

    auth: dmda.DomoAuth = field(default=None, repr=False)

    subscription_authorizations: [DomoPublication_Subscription] = field(
        default_factory=list
    )
    content: [DomoPublication_Content] = field(default_factory=list)

    content_page_id_ls: [str] = field(default_factory=list)
    content_dataset_id_ls: [str] = field(default_factory=list)

    # lineage: dmdl.DomoLineage = None

    # def __post_init__(self):
    #     self.lineage = dmdl.DomoLineage(id=self.id,
    #                                     parent=self)

    @classmethod
    def _from_json(cls, obj, auth: dmda.DomoAuth = None):

        dd = util_dd.DictDot(obj)

        domo_pub = cls(
            id=dd.id,
            name=dd.name,
            description=dd.description,
            created_dt=dt.datetime.fromtimestamp(dd.created / 1000)
            if dd.created
            else None,
            is_v2=dd.isV2,
            auth=auth,
        )

        if dd.subscriptionAuthorizations and len(dd.subscriptionAuthorizations) > 0:
            domo_pub.subscription_authorizations = [
                DomoPublication_Subscription._from_json(sub)
                for sub in dd.subscriptionAuthorizations
            ]

        # publish only supports sharing pages and datasets
        if dd.children and len(dd.children) > 0:
            for child in dd.children:

                dmpc = DomoPublication_Content._from_json(child)
                domo_pub.content.append(dmpc)

                if dmpc.entity_type == "PAGE":
                    domo_pub.content_page_id_ls.append(dmpc.entity_id)

                elif dmpc.entity_type == "DATASET":
                    domo_pub.content_dataset_id_ls.append(dmpc.entity_id)

                else:
                    raise DomoPublication_UnexpectedContentType(
                        publication_id=domo_pub.id, 
                        content_type=dmpc.entity_type, 
                        domo_instance=auth.domo_instance)

        return domo_pub


# %% ../../nbs/classes/50_DomoPublish.ipynb 21
@patch_to(DomoPublications, cls_method=True)
async def search_publications(cls: DomoPublications,
                              auth = dmda.DomoAuth,
                              search_term: str = None,
                              session: httpx.AsyncClient = None,
                              debug_api: bool = False,
                              return_raw: bool = False):

    res = await publish_routes.search_publications(auth=auth)

    if return_raw:
        return res

    if not res.is_success or (res.is_success and len(res.response) == 0):
        return None

    return [DomoPublication._from_json(sub_obj)for sub_obj in res.response]

