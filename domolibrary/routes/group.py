# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/group.ipynb.

# %% auto 0
__all__ = ['generate_body_create_group', 'CreateGroup_Error', 'create_group', 'generate_body_update_group_membership']

# %% ../../nbs/routes/group.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/group.ipynb 3
def generate_body_create_group(group_name: str,
                               group_type: str = 'open',
                               description: str = '') -> dict:
    """ Generates the body to create group for content_v2_group API"""
    body = {"name": group_name, 
            "type": group_type,
            "description": description}

    return body

# %% ../../nbs/routes/group.ipynb 6
class CreateGroup_Error(de.DomoError):
    def __init__(self, status, message, domo_instance, function_name = "create_group"):
        super().__init__(function_name = function_name, status = status, message = message , domo_instance = domo_instance)

async def create_group(auth: dmda.DomoAuth,
                       group_name: str,
                       group_type: str = 'open',
                       description: str = '',
                       debug_api: bool = False,
                       session: httpx.AsyncClient = None
                       ) -> rgd.ResponseGetData:
    # body : {"name": "GROUP_NAME", "type": "open", "description": ""}

    body = generate_body_create_group(
        group_name=group_name, group_type=group_type, description=description)

    url = f'https://{auth.domo_instance}.domo.com/api/content/v2/groups/'

    res= await gd.get_data(
        auth=auth,
        url=url,
        method='POST',
        body=body,
        debug_api=debug_api,
        session = session
    )

    if not res.is_success:
        raise CreateGroup_Error(
            status = res.status, 
            message = res.response,
            domo_instance = auth.domo_instance, 
            function_name="create_group")

    return res


# %% ../../nbs/routes/group.ipynb 11
def generate_body_update_group_membership(group_id: str,
                                          add_user_arr: list[str] = None,
                                          remove_user_arr: list[str] = None,
                                          add_owner_user_arr: list[str] = None,
                                          remove_owner_user_arr: list[str] = None) -> list[dict]:
    body = {"groupId": int(group_id)}
    if add_owner_user_arr:
        body.update({"addOwners": [{"type": "USER", "id": str(
            userId)} for userId in add_owner_user_arr]})

    if remove_owner_user_arr:
        body.update({"removeOwners": [{"type": "USER", "id": str(
            userId)} for userId in remove_owner_user_arr]})

    if remove_user_arr:
        body.update({"removeMembers": [
                    {"type": "USER", "id": str(userId)} for userId in remove_user_arr]})
    if add_user_arr:
        body.update(
            {"addMembers": [{"type": "USER", "id": str(userId)} for userId in add_user_arr]})

    return [body]
