from typing import List, Optional, Union

from server.models.user import User
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from odmantic import ObjectId
from bson.objectid import ObjectId as BsonId
from fastapi_jwt_auth import AuthJWT
from server.models.user import User
from server.settings import engine
from odmantic import Model
from odmantic.query import QueryExpression, SortExpression, match
from odmantic.engine import AIOCursor
from odmantic.field import FieldProxy


async def get_authorized_user(Authorize: AuthJWT = Depends(), dummy = Depends(HTTPBearer())) -> User:
    Authorize.jwt_required()
    user_id = BsonId(Authorize.get_jwt_subject())
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(400, detail="No user found")
    user.update_request_time()
    await engine.save(user)
    return user


async def get_admin_user(user_id: ObjectId = Depends(get_authorized_user)) -> User:
    user = await engine.find_one(User, User.id == user_id)
    if not user.super_user:
        raise HTTPException(403)
    return user


async def allow_only_admin(Authorize: AuthJWT = Depends(), dummy = Depends(HTTPBearer())) -> None:
    Authorize.jwt_required()
    raw_jwt = Authorize.get_raw_jwt()
    if not raw_jwt.get('is_admin'):
        raise HTTPException(403)


class Selector:
    '''
    This class used for getting list of items with some query parameters
    
    Parameters:
        q (str): Used for text search by specific field
        skip (int): Start from item with index skip in database queryset
        limit (int): Limit quantity of qyeryset objects
        sort (str): Sorting parameter, should be a name of string and "-" at front 
            if want to sort in descending order, example: "-field_name"
    '''

    _lookup_fields = None
    _model = None

    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 10, sort: Optional[str] = None) -> None:
        self.q: str = q
        self.skip: int = skip if skip > 0 else 0
        self.limit: int = limit if limit > 0 else 10
        self.sort: str = sort

    async def get_objects(self, *queries: QueryExpression, sort: Optional[str] = None) -> AIOCursor:
        '''
        Returns query result - list of items with limit and skip,
        and add self.count - quantity of items in database 
        '''
        if sort:
            self.sort = sort
        queries = list(queries)
        sort = self._build_sort_expression()
        self.count: int = await engine.count(self._model, *queries)
        if self.q is not None:
            for field in self._lookup_fields:
                queries.append(field.match(self.q))

        res = await engine.find(
            self._model,
            *queries,
            skip=self.skip,
            limit=self.limit,
            sort=sort,
        )
        return res

    def _build_sort_expression(self) -> Union[SortExpression, None]:
        if self.sort is None:
            return None
        sort = self.sort.strip().strip('_')
        field = self._model.__dict__.get(sort.strip('-'))
        if field is None:
            return None
        if sort[0] == '-':
            return field.desc()
        else:
            return field.asc()


def get_selector(model: Model, *lookup_fields: FieldProxy) -> Selector:
    '''
    Used as class factory to create classs constructor initialized for 
    use with Depend for specific endpoint.

    Parameters:
        model (Model): Model from which you want to fetch data
        *lookup_fields (FieldProxy): The fields of odmantic.Model in wich you want search by q parameter 

        >>> @app.get('/')
        >>> async def some_ep(selector: Selector = Depends(get_selector(Model, Model.title, Model.text, ...))):
    '''
    class SelectorInterface(Selector):
        _model = model
        _lookup_fields = lookup_fields
    return SelectorInterface