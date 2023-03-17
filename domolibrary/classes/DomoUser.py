# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoUser.ipynb.

# %% auto 0
__all__ = ['DomoUser', 'DomoUsers', 'CreateUser_MissingRole']

# %% ../../nbs/classes/50_DomoUser.ipynb 3
from fastcore.basics import patch_to


# %% ../../nbs/classes/50_DomoUser.ipynb 4
import datetime as dt
from dataclasses import dataclass, field
from typing import Optional
import httpx

from pprint import pprint

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.Logger as lc
import domolibrary.client.DomoError as de
import domolibrary.routes.user as user_routes

# %% ../../nbs/classes/50_DomoUser.ipynb 6
@dataclass
class DomoUser:
    """a class for interacting with a Domo User"""

    id: str
    display_name: str = None
    email_address: str = None
    role_id: str = None

    publisher_domain: str = None
    subscriber_domain: str = None
    virtual_user_id: str = None

    auth: Optional[dmda.DomoAuth] = field(repr=False, default=None)

    def __post_init__(self):
        self.id = str(self.id)

    def __eq__(self, other):
        if not isinstance(other, DomoUser):
            return False
        
        return self.id == other.id

    @classmethod
    def _from_search_json(cls, auth, user_obj):
        user_dd = util_dd.DictDot(user_obj)

        return cls(
            auth=auth,
            id=str(user_dd.id or user_dd.userId),
            display_name=user_dd.displayName,
            email_address=user_dd.emailAddress,
            role_id=user_dd.roleId,
        )

    @classmethod
    def _from_virtual_json(cls, auth, user_obj):
        user_dd = util_dd.DictDot(user_obj)

        return cls(
            id=user_dd.id,
            auth=auth,
            publisher_domain=user_dd.publisherDomain,
            subscriber_domain=user_dd.subscriberDomain,
            virtual_user_id=user_dd.virtualUserId,
        )

    @classmethod
    def _from_bootstrap_json(cls, auth, user_obj):

        dd = user_obj
        if isinstance(user_obj, dict):
            dd = util_dd.DictDot(user_obj)

        return cls(id=dd.id, display_name=dd.displayName, auth=auth)

# %% ../../nbs/classes/50_DomoUser.ipynb 8
@patch_to(DomoUser)
async def reset_password(self: DomoUser, new_password: str, debug_api: bool = False):
    """reset your password, will respect password restrictions set up in the Domo UI"""

    res = await user_routes.reset_password(
        auth=self.auth, user_id=self.id, new_password=new_password, debug_api=debug_api
    )

    return res

# %% ../../nbs/classes/50_DomoUser.ipynb 9
@patch_to(DomoUser, cls_method=True)
async def request_password_reset(
    cls,
    domo_instance: str,
    email: str,
    locale: str = "en-us",
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    """request password reset email.  Note: does not require authentication."""

    return await user_routes.request_password_reset(
        domo_instance=domo_instance,
        email=email,
        locale=locale,
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/classes/50_DomoUser.ipynb 13
@dataclass
class DomoUsers:
    """a class for searching for Users"""

    logger: Optional[lc.Logger] = None

    @classmethod
    def _users_to_domo_user(cls, user_ls, auth: dmda.DomoAuth):
        return [
            DomoUser._from_search_json(auth=auth, user_obj=user_obj)
            for user_obj in user_ls
        ]

    @classmethod
    def _users_to_virtual_user(cls, user_ls, auth: dmda.DomoAuth):
        return [
            DomoUser._from_virtual_json(auth=auth, user_obj=user_obj)
            for user_obj in user_ls
        ]

    def _generate_logger(self, logger: Optional[lc.Logger] = None):
        self.logger = logger or self.logger or lc.Logger()

# %% ../../nbs/classes/50_DomoUser.ipynb 15
@patch_to(DomoUsers, cls_method=True)
async def all_users(
    cls: DomoUsers,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    debug_prn: bool = False,
    debug_log: bool = False,
    logger: Optional[lc.Logger] = None,
) -> [DomoUser]:
    """retrieves all users from Domo"""

    logger = logger or lc.Logger(app_name="all_users")

    res = await user_routes.get_all_users(auth=auth, debug_api=debug_api)

    if not res.is_success:
        return None

    users_ls = res.response

    message = f"{len(users_ls)} users retrieved from {auth.domo_instance}"

    if debug_prn:
        print(message)
    logger.log_info(message=message, debug_log=debug_log)

    return cls._users_to_domo_user(user_ls=users_ls, auth=auth)


# %% ../../nbs/classes/50_DomoUser.ipynb 18
@patch_to(DomoUsers, cls_method=True)
async def by_id(
    cls: DomoUsers,
    user_ids: list[str],  # can search for one or multiple users
    auth: dmda.DomoAuth,
    only_allow_one: bool = True,
    debug_api: bool = False,
    return_raw: bool = False,
) -> list:

    body = user_routes.generate_search_users_body_by_id(user_ids)

    try:
        res = await user_routes.search_users(
            return_raw=False,
            body=body,
            debug_api=debug_api,
            auth=auth,
        )

    except user_routes.SearchUser_NoResults as e:
        print(e)
        return None

    if return_raw:
        return res

    domo_users = cls._users_to_domo_user(user_ls=res.response, auth=auth)

    if only_allow_one:
        return domo_users[0]

    return domo_users

# %% ../../nbs/classes/50_DomoUser.ipynb 21
@patch_to(DomoUsers, cls_method=True)
def util_match_domo_users_to_emails(
    cls: DomoUsers, domo_users: list[DomoUser], user_email_ls: list[str]
) -> list:
    """pass in an array of user emails to match against an array of Domo User"""

    matches = []
    for idx, email in enumerate(user_email_ls):
        match_user = next(
            (
                domo_user
                for domo_user in domo_users
                if email.lower() == domo_user.email_address.lower()
            ),
            None,
        )
        if match_user:
            matches.append(match_user)
    return matches


@patch_to(DomoUsers, cls_method=True)
def util_match_users_obj_to_emails(
    cls: DomoUsers, user_ls: list[dict], user_email_ls: list[str]
) -> list:
    """pass in an array of user emails to match against an array of Domo User"""

    matches = []
    for idx, email in enumerate(user_email_ls):
        match_user = next(
            (
                user_obj
                for user_obj in user_ls
                if email.lower() == user_obj.get("emailAddress").lower()
            ),
            None,
        )
        if match_user:
            matches.append(match_user)
    return matches


@patch_to(DomoUsers, cls_method=True)
async def by_email(
    cls: DomoUsers,
    email_ls: list[str],
    auth: dmda.DomoAuth,
    only_allow_one: bool = True,
    debug_api: bool = False,
    debug_prn: bool = False,
    return_raw: bool = False,
) -> list:

    body = user_routes.generate_search_users_body_by_email(
        user_email_ls=email_ls)

    if debug_prn:
        pprint(body)

    res = await user_routes.search_users(
        body=body, auth=auth, return_raw=False, debug_api=debug_api
    )

    if return_raw:
        if only_allow_one:
            res.response = cls.util_match_users_obj_to_emails(
                res.response, email_ls
            )[0]
        return res

    domo_users = cls._users_to_domo_user(res.response, auth=auth)

    if only_allow_one:
        return cls.util_match_domo_users_to_emails(domo_users, email_ls)[0]

    return domo_users


# %% ../../nbs/classes/50_DomoUser.ipynb 24
@patch_to(DomoUsers, cls_method=True)
async def virtual_user_by_subscriber_instance(
    cls: DomoUsers,
    subscriber_instance_ls: str,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    return_raw: bool = False,
):
    res = await user_routes.search_virtual_user_by_subscriber_instance(
        auth=auth,
        subscriber_instance_ls=subscriber_instance_ls,
        debug_api=debug_api,
    )

    if return_raw:
        return res

    if not res.is_success:
        return None

    user_ls = res.response

    domo_users = cls._users_to_virtual_user(user_ls, auth=auth)
    return domo_users[0]


# %% ../../nbs/classes/50_DomoUser.ipynb 28
class CreateUser_MissingRole(de.DomoError):
    def __init__(self, domo_instance, email_address):
        super().__init__(domo_instance= domo_instance, message = f"error creating user {email_address} missing role_id")

@patch_to(DomoUsers, cls_method=True)
async def create_user(
    cls: DomoUsers,
    auth: dmda.DomoAuth,
    display_name,
    email_address,
    role_id,
    password: str = None,
    send_password_reset_email: bool = False,
    debug_api: bool = False,
    session = httpx.AsyncClient
):
    """class method that creates a new Domo user"""

    res = await user_routes.create_user(
        auth=auth,
        display_name=display_name,
        email_address=email_address,
        role_id=role_id,
        debug_api=debug_api,
        session = session
    )

    if res.status != 200:
        return None

    dd = util_dd.DictDot(res.response)
    u = cls(
        auth=auth,
        id=dd.id or dd.userId,
        display_name=dd.displayName,
        email_address=dd.emailAddress,
    )

    if password:
        await u.reset_password(new_password=password)

    if send_password_reset_email:
        await u.request_password_reset(
            domo_instance=auth.domo_instance, email=u.email_address
        )

    return u


# %% ../../nbs/classes/50_DomoUser.ipynb 29
@patch_to(DomoUsers, cls_method=True)
async def upsert_user(cls: DomoUsers,
                      auth: dmda.DomoAuth,
                      email_address: str,
                      display_name: str = None,
                      role_id: str = None,
                      debug_api: bool = False,
                      debug_prn: bool = False,
                      session: httpx.AsyncClient = None
                      ):

    try:
        domo_user = await cls.by_email(
            email_ls=[email_address],
            auth=auth,
            only_allow_one=True,
            debug_api=debug_api,
        )

        if domo_user:
            user_property_ls = []
            if display_name:
                user_property_ls.append(user_routes.UserProperty(
                    user_routes.UserProperty_Type.display_name, display_name))

            if role_id:
                user_property_ls.append(user_routes.UserProperty(
                    user_routes.UserProperty_Type.role_id, role_id))

            return await user_routes.update_user(
                user_id=domo_user.id,
                user_property_ls=user_property_ls,
                auth=auth,
                debug_api=debug_api
            )

    except user_routes.SearchUser_NoResults as e:
        if debug_prn:
            print(
                f'No user match -- creating new user in {auth.domo_instance}')

        if not role_id:
            raise CreateUser_MissingRole(
                domo_instance=auth.domo_instance, email_address=email_address)

        return await cls.create_user(auth=auth,
                                     display_name=display_name or f"{email_address} - via dl {dt.date.today()}",
                                     email_address=email_address,
                                     role_id=role_id,
                                     debug_api=debug_api, session=session)

    # finally:
    #     if grant_ls:
    #         grant_ls = domo_role._valid_grant_ls(grant_ls)
    #         await domo_role.set_grants(grant_ls=grant_ls)

