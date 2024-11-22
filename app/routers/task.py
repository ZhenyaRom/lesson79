from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks_all = db.scalars(select(Task)).all()
    return tasks_all


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task_search = db.scalars(select(Task).where(Task.id == task_id)).all()
    if task_search:
        return task_search
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, task_create: CreateTask):
    user_is = db.scalars(select(User).where(User.id == user_id)).all()
    if user_is:
        task_title_repeat = db.scalars(select(Task).where(Task.title == task_create.title)).all()
        if task_title_repeat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title is busy")
        db.execute(insert(Task).values(title=task_create.title,
                                       content=task_create.content,
                                       priority=task_create.priority,
                                       user_id=user_id,
                                       slug=slugify(task_create.title)))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, task_update: UpdateTask):
    task_old = db.scalars(select(Task).where(Task.id == task_id)).all()
    if task_old:
        task_title_repeat = db.scalars(select(Task).where(Task.title == task_update.title)).all()
        if task_title_repeat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title is busy")

        db.execute(update(Task).where(Task.id == task_id).values(title=task_update.title,
                                                                 content=task_update.content,
                                                                 priority=task_update.priority,
                                                                 slug=slugify(task_update.title)))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task update is successful!'}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task_delete = db.scalars(select(Task).where(Task.id == task_id)).all()
    if task_delete:
        db.execute(delete(Task).where(Task.id == task_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task delete is successful!'}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")
