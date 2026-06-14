from typing import Any, Generic, TypeVar

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import logger
from app.core.exceptions import NotFoundException

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Базовый репозиторий с типичной логикой для работы с базой данных.
    Предоставляет стандартные CRUD операции и дополнительные методы.
    """

    def __init__(self, model: type[T]):
        self.model = model

    # ==================== БАЗОВЫЕ CRUD ОПЕРАЦИИ ====================

    async def get_by_id(
        self, session: AsyncSession, primary_key: int, raise_if_not_found: bool = True
    ) -> T | None:
        """
        Получить объект по primary_key.

        Args:
            session: Сессия базы данных
            primary_key: Первичный ключ
            raise_if_not_found: Выбросить исключение если не найден

        Returns:
            Объект модели или None
        """
        logger.info(f"Getting {self.model.__name__} by primary_key: {primary_key}")
        obj = await session.get(self.model, primary_key)
        if obj is None and raise_if_not_found:
            logger.warning(f"{self.model.__name__} with primary_key {primary_key} not found")
            raise NotFoundException()
        logger.debug(
            f"Successfully retrieved {self.model.__name__} with primary_key: {primary_key}"
        )
        return obj

    async def get_by_id_with_relations(
        self,
        session: AsyncSession,
        primary_key: int,
        relations: list[str] = None,
        raise_if_not_found: bool = True,
    ) -> T | None:
        """
        Получить объект по primary_key с загрузкой связанных данных.

        Args:
            session: Сессия базы данных
            primary_key: Первичный ключ
            relations: Список имен отношений для загрузки
            raise_if_not_found: Выбросить исключение если не найден

        Returns:
            Объект модели или None
        """
        stmt = select(self.model).where(self.model.primary_key == primary_key)

        if relations:
            for relation in relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))

        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        if obj is None and raise_if_not_found:
            raise NotFoundException()
        return obj

    async def create(self, session: AsyncSession, **kwargs) -> T:
        """
        Создать новый объект.

        Args:
            session: Сессия базы данных
            **kwargs: Поля для создания объекта

        Returns:
            Созданный объект
        """
        logger.info(f"Creating new {self.model.__name__} with data: {list(kwargs.keys())}")
        obj = self.model(**kwargs)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        logger.info(
            f"Successfully created {self.model.__name__} with id: {obj.id}"
        )
        return obj

    async def update(self, session: AsyncSession, primary_key: int, **kwargs) -> T | None:
        """
        Обновить объект по primary_key.

        Args:
            session: Сессия базы данных
            primary_key: Первичный ключ
            **kwargs: Поля для обновления

        Returns:
            Обновленный объект или None если не найден
        """
        logger.info(
            f"Updating {self.model.__name__} with primary_key: {primary_key}, fields: {list(kwargs.keys())}"
        )
        obj = await session.get(self.model, primary_key)
        if obj is None:
            logger.warning(
                f"{self.model.__name__} with primary_key {primary_key} not found for update"
            )
            return None

        for field, value in kwargs.items():
            if hasattr(obj, field) and value is not None:
                setattr(obj, field, value)

        await session.flush()
        await session.refresh(obj)
        logger.info(f"Successfully updated {self.model.__name__} with primary_key: {primary_key}")
        return obj

    async def delete(self, session: AsyncSession, primary_key: int) -> bool:
        """
        Удалить объект по primary_key.

        Args:
            session: Сессия базы данных
            primary_key: Первичный ключ

        Returns:
            True если объект был удален, False если не найден
        """
        logger.info(f"Deleting {self.model.__name__} with primary_key: {primary_key}")
        obj = await session.get(self.model, primary_key)
        if obj is None:
            logger.warning(
                f"{self.model.__name__} with primary_key {primary_key} not found for deletion"
            )
            return False

        await session.delete(obj)
        logger.info(f"Successfully deleted {self.model.__name__} with primary_key: {primary_key}")
        return True

    async def delete_many(self, session: AsyncSession, primary_keys: list[int]) -> int:
        """
        Удалить несколько объектов по списку primary_key.

        Args:
            session: Сессия базы данных
            primary_keys: Список первичных ключей

        Returns:
            Количество удаленных объектов
        """
        stmt = delete(self.model).where(self.model.primary_key.in_(primary_keys))
        result = await session.execute(stmt)
        return result.rowcount

    # ==================== МЕТОДЫ ПОИСКА И ФИЛЬТРАЦИИ ====================
    async def find_by_field(
        self,
        session: AsyncSession,
        field_name: str,
        value: Any,
        raise_if_not_found: bool = False,
    ) -> T | None:
        """
        Найти объект по значению поля.

        Args:
            session: Сессия базы данных
            field_name: Имя поля
            value: Значение для поиска
            raise_if_not_found: Выбросить исключение если не найден

        Returns:
            Найденный объект или None
        """
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        if obj is None and raise_if_not_found:
            raise NotFoundException()
        return obj

    async def find_many_by_field(
        self, session: AsyncSession, field_name: str, value: Any
    ) -> list[T]:
        """
        Найти все объекты по значению поля.

        Args:
            session: Сессия базы данных
            field_name: Имя поля
            value: Значение для поиска

        Returns:
            Список найденных объектов
        """
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_conditions(
        self,
        session: AsyncSession,
        conditions: dict[str, Any],
        raise_if_not_found: bool = False,
    ) -> T | None:
        """
        Найти объект по нескольким условиям.

        Args:
            session: Сессия базы данных
            conditions: Словарь условий {поле: значение}
            raise_if_not_found: Выбросить исключение если не найден

        Returns:
            Найденный объект или None
        """
        stmt = select(self.model)
        for field_name, value in conditions.items():
            field = getattr(self.model, field_name)
            stmt = stmt.where(field == value)

        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        if obj is None and raise_if_not_found:
            raise NotFoundException()
        return obj

    async def find_many_by_conditions(
        self, session: AsyncSession, conditions: dict[str, any]
    ) -> list[T]:
        """
        Найти все объекты по нескольким условиям.
        Поддерживает как одиночное значение, так и список значений.
        """
        stmt = select(self.model)

        for field_name, value in conditions.items():
            field = getattr(self.model, field_name)

            if isinstance(value, (list, tuple, set)):  # поддержка списка значений
                if len(value) == 1:
                    stmt = stmt.where(field == list(value)[0])
                else:
                    stmt = stmt.where(field.in_(value))
            else:
                stmt = stmt.where(field == value)

        result = await session.execute(stmt)
        return list(result.scalars().all())
        # ==================== ПАГИНАЦИЯ И СОРТИРОВКА ====================

    async def get_paginated(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_desc: bool = False,
        filters: dict[str, Any] | None = None,
        relations: list[str] | None = None,
    ) -> tuple[list[T], int]:
        """
        Получить пагинированный список объектов.

        Args:
            session: Сессия базы данных
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            order_by: Поле для сортировки
            order_desc: Сортировка по убыванию
            filters: Фильтры для поиска
            relations: Список отношений для загрузки

        Returns:
            Кортеж (список объектов, общее количество)
        """
        logger.info(
            f"Getting paginated {self.model.__name__} list: skip={skip}, limit={limit}, filters={filters}, relations={relations}"
        )
        # Основной запрос
        stmt = select(self.model)

        # Загрузка отношений
        if relations:
            for relation in relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))

        # Применение фильтров
        if filters:
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                if isinstance(value, list):
                    stmt = stmt.where(field.in_(value))
                else:
                    stmt = stmt.where(field == value)

        # Подсчет общего количества
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Сортировка
        if order_by:
            field = getattr(self.model, order_by)
            if order_desc:
                stmt = stmt.order_by(field.desc())
            else:
                stmt = stmt.order_by(field.asc())

        # Пагинация
        stmt = stmt.offset(skip).limit(limit)

        # Выполнение запроса
        result = await session.execute(stmt)
        objects = list(result.scalars().all())

        logger.info(
            f"Retrieved {len(objects)} {self.model.__name__} objects out of {total_count} total"
        )
        return objects, total_count

    async def count(self, session: AsyncSession, filters: dict[str, Any] | None = None) -> int:
        """
        Подсчитать количество объектов с учетом фильтров.

        Args:
            session: Сессия базы данных
            filters: Фильтры для подсчета

        Returns:
            Количество объектов
        """
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                if isinstance(value, list):
                    stmt = stmt.where(field.in_(value))
                else:
                    stmt = stmt.where(field == value)

        result = await session.execute(stmt)
        return result.scalar_one()

    # ==================== МАССОВЫЕ ОПЕРАЦИИ ====================

    async def create_many(
        self, session: AsyncSession, objects_data: list[dict[str, Any]]
    ) -> list[T]:
        """
        Создать несколько объектов.

        Args:
            session: Сессия базы данных
            objects_data: Список словарей с данными для создания

        Returns:
            Список созданных объектов
        """
        objects = [self.model(**data) for data in objects_data]
        session.add_all(objects)
        await session.flush()

        for obj in objects:
            await session.refresh(obj)

        return objects

    async def update_many(
        self, session: AsyncSession, conditions: dict[str, Any], updates: dict[str, Any]
    ) -> int:
        """
        Обновить несколько объектов по условиям.

        Args:
            session: Сессия базы данных
            conditions: Условия для поиска объектов
            updates: Поля для обновления

        Returns:
            Количество обновленных объектов
        """
        stmt = update(self.model)

        # Применение условий
        for field_name, value in conditions.items():
            field = getattr(self.model, field_name)
            stmt = stmt.where(field == value)

        # Применение обновлений
        stmt = stmt.values(**updates)

        result = await session.execute(stmt)
        return result.rowcount

    async def exists(self, session: AsyncSession, conditions: dict[str, Any]) -> bool:
        """
        Проверить существование объекта по условиям.

        Args:
            session: Сессия базы данных
            conditions: Условия для проверки

        Returns:
            True если объект существует, False иначе
        """
        stmt = select(func.count()).select_from(self.model)

        for field_name, value in conditions.items():
            field = getattr(self.model, field_name)
            stmt = stmt.where(field == value)

        result = await session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================

    async def get_all(
        self,
        session: AsyncSession,
        relations: list[str] | None = None,
        order_by: str | None = None,
        order_desc: bool = False,
    ) -> list[T]:
        """
        Получить все объекты.

        Args:
            session: Сессия базы данных
            relations: Список отношений для загрузки
            order_by: Поле для сортировки
            order_desc: Сортировка по убыванию

        Returns:
            Список всех объектов
        """
        stmt = select(self.model)

        if relations:
            for relation in relations:
                stmt = stmt.options(selectinload(getattr(self.model, relation)))

        if order_by:
            field = getattr(self.model, order_by)
            if order_desc:
                stmt = stmt.order_by(field.desc())
            else:
                stmt = stmt.order_by(field.asc())

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self,
        session: AsyncSession,
        search_term: str,
        search_fields: list[str],
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[T], int]:
        """
        Поиск объектов по текстовому запросу в указанных полях.

        Args:
            session: Сессия базы данных
            search_term: Поисковый запрос
            search_fields: Список полей для поиска
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Кортеж (список найденных объектов, общее количество)
        """
        stmt = select(self.model)

        # Создание условий поиска
        search_conditions = []
        for field_name in search_fields:
            field = getattr(self.model, field_name)
            search_conditions.append(field.ilike(f"%{search_term}%"))

        if search_conditions:
            stmt = stmt.where(or_(*search_conditions))

        # Подсчет общего количества
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Пагинация
        stmt = stmt.offset(skip).limit(limit)

        result = await session.execute(stmt)
        objects = list(result.scalars().all())

        return objects, total_count
