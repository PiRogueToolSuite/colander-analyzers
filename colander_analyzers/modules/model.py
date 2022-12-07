import json
import uuid
from dataclasses import dataclass, field


class ColanderJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ColanderObject):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


@dataclass
class ColanderObject:
    id: str = field(default_factory=lambda :str(uuid.uuid4()))
    correlation_id: str = ''
    attributes: list[dict] = field(default_factory=list)
    description: str = ''

    def add_attribute(self, key, value):
        self.attributes[key] = value


class ColanderRegistry:
    def __init__(self):
        self.correlation_id = str(uuid.uuid4())
        self.__registry = {}

    def a(self, obj: ColanderObject):
        obj.correlation_id = self.correlation_id
        self.__registry[obj.id] = obj

    def all(self):
        return list(self.__registry.values())


@dataclass
class Observable(ColanderObject):
    type: str = ''
    value: str = ''
    obj_type: str = 'observable'


@dataclass
class Relation(ColanderObject):
    name: str = ''
    obj_from: str = ''
    obj_to: str = ''
    obj_type: str = 'relation'


if __name__ == '__main__':
    a = []
    a.append(Observable(
        id='id_1',
        type='type_1',
        value='value_1',
    ))
    a.append(Observable(
        id='id_2',
        type='type_2',
        value='value_2',
    ))
    a.append(Relation(
        id='id_1',
        name='name_1',
        obj_from='obj_f_1',
        obj_to='obj_t_1',
    ))
    a.append(Relation(
        id='id_2',
        name='name_2',
        obj_from='obj_f_2',
        obj_to='obj_t_2',
        attributes=[
            {'foo': 'bar'},
            {'inde': 4},
        ]
    ))

    print(json.dumps(a, cls=ColanderJsonEncoder))
