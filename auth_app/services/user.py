from datetime import datetime
from random import randint
from typing import Type
import logging
import sqlalchemy.orm
from flask import abort
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import engine, Base
from database.db_models import User, History, Roles, UsersRoles, OauthUsers
from database.session_decorator import get_session
from services.utils import get_device_type

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.engine = engine

    @get_session()
    def register_user(
            self,
            password: str,
            login: str,
            first_name: str,
            last_name: str,
            session: sqlalchemy.orm.Session = None
    ) -> dict[str, str]:
        """Зарегистрировать пользователя."""
        logger.debug("Регистрация пользователя")
        try:
            session.query(User).filter(User.login == login).one()
            logger.info("Пользователь %s уже существует", login)
        except NoResultFound:
            password_hash = generate_password_hash(password)
            new_user = User(
                login=login,
                password=password_hash,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(new_user)
            session.commit()
            logger.info("Создан пользователь %s", login)
            new_user = session.query(User).filter(User.login == login).one()
            new_user = self._transform_query_to_dict(new_user)
            return new_user
        else:
            abort(400)

    @get_session()
    def login_user(
            self,
            login: str,
            password: str,
            user_agent: str,
            session: sqlalchemy.orm.Session = None
    ) -> dict[str, str]:
        """Получить пользователя по логину
        :param login: логин (e-mail пользователя)"""
        logger.debug("Вход пользователя %s в учетную запись", login)
        try:
            user = session.query(User).filter(User.login == login).one()
            logger.info("Пользователь %s найден", login)
        except NoResultFound:
            abort(404)
        else:
            if check_password_hash(user.password, password):
                user_info = History(
                    user_id=user.id,
                    user_agent=user_agent,
                    auth_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                    user_device_type=get_device_type(user_agent)
                )
                session.add(user_info)
                session.commit()
                logger.info("В историю внесена информация о входе пользователя %s", login)
                user = self._transform_query_to_dict(user)
                return user
            abort(401)

    @get_session()
    def change_password(
            self,
            user_id: str,
            old_password: str,
            new_password: str,
            session: sqlalchemy.orm.Session = None,
    ) -> dict[str, str]:
        logger.debug("Меняем пароль для пользователя с ид %s", user_id)
        try:
            user = session.query(User).filter(User.id == user_id).one()
            logger.info("Пользователь найден в бд")
        except NoResultFound:
            abort(404)
        else:
            if user and check_password_hash(user.password, old_password):
                user.password = generate_password_hash(new_password)
                session.commit()
                logger.info("Пароль пользователя изменен")
                user = session.query(User).filter(User.id == user_id).one()
                return user
            abort(401)

    @get_session()
    def change_login(
            self,
            user_id: str,
            password: str,
            new_login: str,
            session: sqlalchemy.orm.Session = None,
    ) -> dict[str, str]:
        logger.debug("Меняем e-mail для пользователя с ид %s", user_id)
        try:
            user = session.query(User).filter(User.id == user_id).one()
            logger.info("Пользователь найден в бд")
        except NoResultFound:
            abort(404)
        else:
            if user and check_password_hash(user.password, password):
                user.login = new_login
                session.commit()
                logger.info("Логин пользователя изменен")
                user = session.query(User).filter(User.id == user_id).one()
                return user
            abort(401)

    @get_session()
    def get_login_history(
            self,
            user_id: str,
            page: int = 1,
            page_size: int = 20,
            session: sqlalchemy.orm.Session = None,
    ) -> dict[str, str]:
        logger.debug("Получаем историю по пользователю с ид %s", user_id)
        query = session.query(History).filter(History.user_id == user_id).order_by(History.auth_date)
        # query = query.func.count().over()
        # query = session.query([History, func.count().over()])
        skip = (page - 1) * page_size
        query = query.slice(skip, skip + page_size).all()
        result = dict()
        for row in query:
            result[str(row.auth_date)] = row.user_agent
        return result

    @get_session()
    def get_user_by_id(
            self,
            user_id: str,
            session: sqlalchemy.orm.Session = None,
    ) -> dict[str, str]:
        logger.debug("Получаем полную информацию по пользователю по ид %s", user_id)
        try:
            user = session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            abort(404)
        else:
            return self._transform_query_to_dict(user)

    @get_session()
    def get_roles_names_for_user(self, user_id: str, session: sqlalchemy.orm.Session = None):
        logger.debug("Получаем роли по пользователю")
        roles = session.query(
            Roles.role,
        ).join(
            UsersRoles,
            Roles.id == UsersRoles.role_id,
        ).where(
            UsersRoles.user_id == user_id,
        ).all()
        roles = [role.role for role in roles]
        return roles

    @staticmethod
    def _transform_query_to_dict(row: Type[Base]) -> dict[str, str]:
        query_as_dict = {}
        for column in row.__table__.columns:
            if column.name != 'password':
                query_as_dict[column.name] = getattr(row, column.name)
        return query_as_dict

    @get_session()
    def create_superuser(
        self,
        password: str,
        login: str,
        first_name: str,
        last_name: str,
        session: sqlalchemy.orm.Session = None,
    ):
        logger.debug("Создаем админа")
        try:
            session.query(User).filter(User.login == login).one()
            logger.debug("Админ уже существует")
        except NoResultFound:
            password_hash = generate_password_hash(password)
            admin = User(
                login=login,
                password=password_hash,
                first_name=first_name,
                last_name=last_name,
                is_admin=True
            )
            session.add(admin)
            session.commit()
            logger.debug("Админ создан")
            new_user = session.query(User).filter(User.login == login).one()
            new_user = self._transform_query_to_dict(new_user)
            return new_user
        else:
            abort(400)

    @get_session()
    def add_login_to_history(
            self,
            user_id: str,
            user_agent: str,
            session: sqlalchemy.orm.Session = None,
    ) -> None:
        session.add(
            History(
                user_id=user_id,
                user_agent=user_agent,
                auth_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                user_device_type=get_device_type(user_agent)
            ),
        )
        session.commit()

    @get_session()
    def register_user_oauth(
        self,
        user_agent: str,
        email: str,
        oauth_id: str,
        oauth_first_name: str,
        oauth_last_name: str,
        session: sqlalchemy.orm.Session = None,
    ) -> dict[str, str]:
        """Юзер добавляется в Users и в OauthUsers, добавляется запись в историю логинов."""
        try:
            user = session.query(User).filter(User.login == email).one()
        except NoResultFound:
            session.add(
                User(
                    password=generate_password_hash(str(randint(1, 10000))),
                    login=email,
                    first_name=oauth_first_name,
                    last_name=oauth_last_name,
                ),
            )
            session.commit()
            user = session.query(User).filter(User.login == email).one()

        try:
            session.query(OauthUsers).filter(
                OauthUsers.oauth_id == oauth_id,
                OauthUsers.oauth_email == email,
            ).one()
        except NoResultFound:
            session.add(
                OauthUsers(
                    user_id=user.id,
                    oauth_id=oauth_id,
                    oauth_email=email,
                ),
            )
            session.commit()

        self.add_login_to_history(user_id=user.id, user_agent=user_agent)

        user = self._transform_query_to_dict(user)
        user['roles'] = self.get_roles_names_for_user(user['id'])
        return user


user_service = UserService()
