from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models.user import User
from app.schemas import CreateUser, UpdateUser
from app.schemas import CreateTask, UpdateTask
from app.models.task import Task
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify


router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users_all = db.scalars(select(User)).all()
    return users_all


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user_search = db.scalars(select(User).where(User.id == user_id)).all()
    if not user_search:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user_search


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], user_create: CreateUser):
    users_all = db.scalars(select(User)).all()
    if not users_all:
        db.execute(insert(User).values(username=user_create.username, firstname=user_create.firstname,
                                       lastname=user_create.lastname, age=user_create.age,
                                       slug=slugify(user_create.username)))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}

    user_repeat = db.scalars(select(User).where(User.username == user_create.username)).all()
    if not user_repeat:
        db.execute(insert(User). values(username=user_create.username, firstname=user_create.firstname,
                                        lastname=user_create.lastname, age=user_create.age,
                                        slug=slugify(user_create.username)))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username is busy")


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, user_update: UpdateUser):
    user_old = db.scalars(select(User).where(User.id == user_id)).all()
    if user_old:
        db.execute(update(User).where(User.id == user_id).values(firstname=user_update.firstname,
                                                                 lastname=user_update.lastname,
                                                                 age=user_update.age))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user_delete = db.scalars(select(User).where(User.id == user_id)).all()
    if user_delete:
        db.execute(delete(User).where(User.id == user_id))
        db.execute(delete(Task).where(Task.user_id == user_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User delete is successful!'}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user_search = db.scalars(select(User).where(User.id == user_id)).all()
    if user_search:
        user_s_task = db.scalars(select(Task).where(Task.user_id == user_id)).all()
        return user_s_task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
