import random
from abc import abstractmethod, ABC
from typing import Optional, List, Any, Tuple

from domain.entitites import AliveEntity
from domain.objects import Movement, Coordinates, HerbivoreFood, Setup
from contrib.utils import logger


class EnvironmentException(Exception):
    pass


class NotVacantPlaceException(EnvironmentException):
    """ This place is already occupied """


class UnsupportedMovement(EnvironmentException):
    """ This movement is not supported """


class ObjectNotExistsInEnvironment(EnvironmentException):
    """ Alas """


class SetupEnvironmentError(EnvironmentException):
    """ No space left in environment """


class Environment:
    """ Environment that represent world around living objects and key rules """

    def __init__(self, setup: Setup):
        self.setup = setup

        self.width: int = setup.window.width
        self.height: int = setup.window.height
        self.replenish_food: bool = setup.food.replenish_food
        self.food_nutrition: int = setup.food.herbivore_food_nutrition
        self.herbivore_food_amount = setup.food.herbivore_food_amount
        self.matrix: List[List] = self._create_blank_matrix()
        self.herbivores: List[AliveEntity] = []

    @property
    def has_space_left(self) -> bool:
        for row in self.matrix:
            for place in row:
                if place == 0:
                    return True
        return False

    @property
    def game_over(self) -> bool:
        # TODO: оптимизировать, хранить кеш сущностей в списке или словаре
        for y, row in enumerate(self.matrix):
            for x, entity in enumerate(row):
                if isinstance(entity, AliveEntity):
                    return False
        return True

    def setup_herbivores(self, herbivores: List[AliveEntity]) -> None:
        self.herbivores = herbivores

    def setup_initial_state(self) -> None:
        self.matrix = self._create_blank_matrix()

        if len(self.herbivores) < 1:
            raise SetupEnvironmentError("No herbivores were set")

        for herbivore in self.herbivores:
            self._set_object_randomly(herbivore)

        for _ in range(self.herbivore_food_amount):
            self._set_object_randomly(HerbivoreFood(nutrition=self.food_nutrition))

    def step_living_regime(self) -> Tuple[List[List], bool]:
        next_state: List[List] = self._get_next_state()
        return next_state, self.game_over

    def get_living_object_observation(self, living_obj: AliveEntity) -> List[List]:
        # TODO: возможно оптимизировать, хранить кеш сущностей в словаре и их координаты, забирать все оттуда
        living_object_coordinates: Optional[Coordinates] = self._get_object_coordinates(living_obj)
        return self._get_observation(living_object_coordinates)

    def _get_next_state(self) -> List[List]:
        moved_entity_cash: List[AliveEntity] = []

        for y, row in enumerate(self.matrix):
            for x, entity in enumerate(row):
                if isinstance(entity, AliveEntity):

                    if entity.health == 0:
                        self._erase_object(Coordinates(x, y))
                        logger.debug(f'Object {entity} died! Lived for: {entity.lived_for}')
                        continue

                    if entity in moved_entity_cash:
                        continue

                    if self.setup.herbivore.birth_after:
                        if child := entity.give_birth():
                            self._set_obj_near(near=Coordinates(x, y), obj=child)
                            moved_entity_cash.append(child)

                    observation: List[List] = self._get_observation(Coordinates(x, y))
                    movement: Movement = entity.get_move(observation=observation)  # ask each entity about next move
                    self._make_move(movement, entity)
                    moved_entity_cash.append(entity)

        return self.matrix

    def _create_blank_matrix(self):
        return [
            [0 if i not in (0, self.width - 1) and j not in (0, self.height - 1) else None for j in range(self.height)]
            for i in range(self.width)
        ]

    def _make_move(self, movement: Movement, obj: AliveEntity) -> None:
        from_: Optional[Coordinates] = self._get_object_coordinates(obj)
        if not from_:
            raise ObjectNotExistsInEnvironment(f'Object {obj} is missing in environment')

        if movement == Movement.STAY:
            return
        elif movement == Movement.UP:
            desired_coordinates = Coordinates(from_.x, from_.y - 1)
        elif movement == Movement.DOWN:
            desired_coordinates = Coordinates(from_.x, from_.y + 1)
        elif movement == Movement.LEFT:
            desired_coordinates = Coordinates(from_.x - 1, from_.y)
        elif movement == Movement.RIGHT:
            desired_coordinates = Coordinates(from_.x + 1, from_.y)
        elif movement == Movement.UP_LEFT:
            desired_coordinates = Coordinates(from_.x - 1, from_.y - 1)
        elif movement == Movement.UP_RIGHT:
            desired_coordinates = Coordinates(from_.x + 1, from_.y - 1)
        elif movement == Movement.DOWN_LEFT:
            desired_coordinates = Coordinates(from_.x - 1, from_.y + 1)
        elif movement == Movement.DOWN_RIGHT:
            desired_coordinates = Coordinates(from_.x + 1, from_.y + 1)
        else:
            raise UnsupportedMovement(f'This movement is not supported: {movement}')

        if self.matrix[desired_coordinates.y][desired_coordinates.x] == 0:
            self.matrix[desired_coordinates.y][desired_coordinates.x] = obj
            self.matrix[from_.y][from_.x] = 0
        elif isinstance(self.matrix[desired_coordinates.y][desired_coordinates.x], HerbivoreFood):
            obj.eat(self.matrix[desired_coordinates.y][desired_coordinates.x])
            self.matrix[desired_coordinates.y][desired_coordinates.x] = obj
            self.matrix[from_.y][from_.x] = 0
            if self.replenish_food:
                self._set_object_randomly(HerbivoreFood(self.food_nutrition))

    def _respawn_object(self, where: Coordinates, obj) -> None:
        if self.matrix[where.y][where.x] == 0:
            self.matrix[where.y][where.x] = obj
            logger.debug(f'Object {obj} was respawned at {where}')
        else:
            raise NotVacantPlaceException('Desired position != 0')

    def _erase_object(self, where: Coordinates) -> None:
        self.matrix[where.y][where.x] = 0

    def _is_empty_coordinates(self, where: Coordinates) -> bool:
        return True if self.matrix[where.y][where.x] == 0 else False

    def _get_object_coordinates(self, obj) -> Optional[Coordinates]:
        for y, row in enumerate(self.matrix):
            for x, element in enumerate(row):
                if element == obj:
                    return Coordinates(x, y)

    def _get_observation(self, point_of_observation: Coordinates) -> List[List]:
        return [
            row[point_of_observation.x - 1:point_of_observation.x + 2]
            for row in self.matrix[point_of_observation.y - 1:point_of_observation.y + 2]
        ]

    def _get_random_coordinates(self) -> Coordinates:
        return Coordinates(
            random.randint(1, self.width) - 1,
            random.randint(1, self.height) - 1,
        )

    def _set_object_randomly(self, obj: Any) -> None:
        if not self.has_space_left:
            raise SetupEnvironmentError('No space left in environment')

        in_process = True

        while in_process:
            random_coordinates: Coordinates = self._get_random_coordinates()
            if self._is_empty_coordinates(random_coordinates):
                self._respawn_object(random_coordinates, obj)
                in_process = False

    def _set_obj_near(self, near: Coordinates, obj: Any) -> None:
        coordinates_around: List[Coordinates] = [
            Coordinates(near.x + x, near.y + y) for y in range(-1, 2) for x in range(-1, 2)
        ]

        for coordinate in coordinates_around:
            if self._is_empty_coordinates(coordinate):
                self._respawn_object(coordinate, obj)
                return

        self._set_object_randomly(obj)
        logger.warning('Cannot respawn near to the parent, respawning randomly')

    def __repr__(self):
        return f'Matrix {self.width}x{self.height} {id(self)}'
