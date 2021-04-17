import jsonpickle
import jsons
from typing import Type, TypeVar

T = TypeVar('T')


class Json:
    @staticmethod
    def to_json(target_object) -> str:
        try:
            json_str = jsons.dumps(target_object)
            target_object2 = Json.deserialize(json_str, type(target_object))
            if str(target_object) == str(target_object2):
                return json_str
            else:
                return jsonpickle.encode(target_object)
        except Exception:
            return jsonpickle.encode(target_object)

    @staticmethod
    def deserialize(json_string: str, class_type: Type[T]) -> T:
        if json_string.startswith('{\"py/'):
            return jsonpickle.decode(json_string)
        else:
            return jsons.loads(json_string, class_type)

    @staticmethod
    def save_file(target_object, file_name: str):
        with open(file_name, 'w') as myfile:
            myfile.write(Json.to_json(target_object))

    @staticmethod
    def deserialize_file(file_name: str, class_type: Type[T]) -> T:
        with open(file_name, 'r') as myfile:
            return Json.deserialize(myfile.read(), class_type)

    # @staticmethod
    # def to_json_pickle(target_object)->str:
    #     return jsonpickle.encode(target_object)
    #
    # @staticmethod
    # def deserialize_pickle(json_string: str):
    #     return jsonpickle.decode(json_string)
    #
    # @staticmethod
    # def save_file_pickle(target_object, file_name: str):
    #     with open(file_name, 'w') as myfile:
    #         myfile.write(jsonpickle.encode(target_object, indent=4))
    #
    # @staticmethod
    # def deserialize_file_pickle(file_name: str) :
    #     with open(file_name, 'r') as myfile:
    #         return Json.deserialize_pickle(myfile.read())
