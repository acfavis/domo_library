# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/user.ipynb.

# %% auto 0
__all__ = ['get_all_users', 'generate_search_users_body_by_id', 'generate_search_users_body_by_email', 'process_v1_search_users',
           'SearchUser_NoResults', 'search_users', 'search_virtual_user_by_subscriber_instance', 'create_user',
           'set_user_landing_page', 'reset_password', 'request_password_reset', 'UserProperty_Type', 'UserProperty',
           'generate_patch_user_property_body', 'update_user']

# %% ../../nbs/routes/user.ipynb 3
from enum import Enum
import httpx

import utils.DictDot as dd
import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/user.ipynb 5
async def get_all_users(
    auth: dmda.DomoAuth, debug_api: bool = False
) -> rgd.ResponseGetData:

    """retrieves all users from Domo"""
    url = f"https://{ auth.domo_instance}.domo.com/api/content/v2/users"

    return await gd.get_data(url=url, method="GET", auth=auth, debug_api=debug_api)


# %% ../../nbs/routes/user.ipynb 9
def generate_search_users_body_by_id(
    user_ids: list[str],  # list of user ids to search
) -> dict:  # dict to pass to search v1_users_search_api
    """search v1_users_search_api"""

    return {
        # "showCount": true,
        # "count": false,
        "includeDeleted": False,
        "includeSupport": False,
        "filters": [
            {"field": "id", "filterType": "value",
                "values": user_ids, "operator": "EQ"}
        ],
    }


# %% ../../nbs/routes/user.ipynb 10
def generate_search_users_body_by_email(
    user_email_ls: list[
        str
    ],  # list of user emails to search.  Note:  search does not appear to be case sensitive
) -> dict:  # dict to pass to search v1_users_search_api
    """search v1_users_search_api"""

    return {
        # "showCount": true,
        # "count": false,
        "includeDeleted": False,
        "includeSupport": False,
        "limit": 200,
        "offset": 0,
        "sort": {"field": "displayName", "order": "ASC"},
        "filters": [
            {
                "filterType": "text",
                "field": "emailAddress",
                "text": " ".join(user_email_ls),
            }
        ],
    }

# %% ../../nbs/routes/user.ipynb 11
def process_v1_search_users(
    v1_user_ls: list[dict],  # list of users from v1_users_search API
) -> list[dict]:  # sanitized list of users.
    """sanitizes the response from v1_users_search API and removes unecessary attributes"""

    clean_users = []

    for obj_user in v1_user_ls:

        dd_user = dd.DictDot(obj_user)

        clean_users.append(
            {
                "id": dd_user.id,
                "displayName": dd_user.displayName,
                "roleId": dd_user.roleId,
                "userName": dd_user.userName,
                "emailAddress": dd_user.emailAddress,
            }
        )

    return clean_users

# %% ../../nbs/routes/user.ipynb 12
class SearchUser_NoResults(de.DomoError):
    def __init__(
        self, domo_instance, function_name="search_users", search_criteria=None
    ):

        search_str = f"- {search_criteria}" if search_criteria else ""

        print(search_str)

        super().__init__(
            message=f"query {search_str} returned no users", function_name=function_name
        )

# %% ../../nbs/routes/user.ipynb 13
async def search_users(
    auth: dmda.DomoAuth, body: dict, debug_api: bool = False, return_raw: bool = False
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/search"

    res = await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body=body,
        debug_api=debug_api,
    )

    if return_raw:
        return res

    if not res.is_success:
        return res

    if res.is_success and len(res.response.get("users")) == 0:
        raise SearchUser_NoResults(domo_instance=auth.domo_instance)

    res.response = process_v1_search_users(res.response.get("users"))
    return res

# %% ../../nbs/routes/user.ipynb 17
async def search_virtual_user_by_subscriber_instance(
    auth: dmda.DomoAuth,  # domo auth object
    subscriber_instance_ls: list[str],  # list of subscriber domo instances
    debug_api: bool = False,  # debug API requests
) -> rgd.ResponseGetData:  # list of virtual domo users
    """retrieve virtual users for subscriber instances tied to one publisher"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/proxy_user/domain/"

    body = {
        "domains": [
            f"{subscriber_instance}.domo.com"
            for subscriber_instance in subscriber_instance_ls
        ]
    }

    return await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body=body,
        debug_api=debug_api,
    )

# %% ../../nbs/routes/user.ipynb 21
async def create_user(
    auth: dmda.DomoAuth,
    display_name: str,
    email_address: str,
    role_id: int,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users"

    body = {"displayName": display_name, "detail": {
        "email": email_address}, "roleId": role_id}

    return await gd.get_data(
        url=url, method="POST", body=body,
        auth=auth, debug_api=debug_api, session=session
    )


# %% ../../nbs/routes/user.ipynb 22
async def set_user_landing_page(
    auth: dmda.DomoAuth, user_id: str, page_id: str, debug_api: bool = False
):

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/landings/target/DESKTOP/entity/PAGE/id/{page_id}/{user_id}"

    return await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        # body = body,
        debug_api=debug_api,
    )


# %% ../../nbs/routes/user.ipynb 23
async def reset_password(
    auth: dmda.DomoAuth,
    user_id: str,
    new_password: str,
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/password"

    body = {"domoUserId": user_id, "password": new_password}

    return await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=body,
        debug_api=debug_api,
    )


# %% ../../nbs/routes/user.ipynb 24
async def request_password_reset(
    domo_instance: str, 
    email: str, locale="en-us", debug_api: bool = False,
    session : httpx.AsyncClient = None
):
    url = f"https://{domo_instance}.domo.com/api/domoweb/auth/sendReset"

    params = {"email": email, "local": locale}

    return await gd.get_data(
        url=url, method="GET", params=params, auth=None, debug_api=debug_api
    )


# %% ../../nbs/routes/user.ipynb 26
class UserProperty_Type(Enum):
    display_name = "displayName"
    email_address = "emailAddress"
    phone_number = "phoneNumber"
    title = "title"
    department = "department"
    web_landing_page = "webLandingPage"
    web_mobile_landing_page = "webMobileLandingPage"
    role_id = "roleId"
    employee_id = "employeeId"
    employee_number = "employeeNumber"
    hire_date = "hireDate"
    reports_to = "reportsTo"


class UserProperty:
    property_type: UserProperty_Type
    values: str

    def __init__(self, property_type: UserProperty_Type, values):
        self.property_type = property_type
        self.values = self._valid_value(values)

    @staticmethod
    def _valid_value(values):
        return values if isinstance(values, list) else [values]

    def to_json(self):
        return {
            "key": self.property_type.value,
            "values": self._valid_value(self.values),
        }

# %% ../../nbs/routes/user.ipynb 27
def generate_patch_user_property_body(user_property_ls: [UserProperty]):
    return {
        "attributes": [user_property.to_json() for user_property in user_property_ls]
    }

# %% ../../nbs/routes/user.ipynb 30
async def update_user(
    user_id: str,
    user_property_ls: [UserProperty],
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/{user_id}"

    body = (
        generate_patch_user_property_body(user_property_ls)
        if isinstance(user_property_ls[0], UserProperty)
        else user_property_ls
    )

    return await gd.get_data(
        url=url,
        method="Patch",
        auth=auth,
        body=body,
        debug_api=debug_api,
        session=session,
    )
