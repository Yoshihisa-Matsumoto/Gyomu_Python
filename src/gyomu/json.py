#import jsonpickle
import jsons
from typing import Type, TypeVar
from marshmallow import Schema

T = TypeVar('T')


class Json:
    @staticmethod
    def to_json(target_object, schema: Schema = None) -> str:
        if schema is not None:
            return schema.dumps(target_object)
        return jsons.dumps(target_object)

    @staticmethod
    def deserialize(json_string: str, class_type: Type[T], schema: Schema = None) -> T:
        if schema is not None:
            dictionary = schema.loads(json_data=json_string)
            if not isinstance(dictionary, list):
                return class_type(**dictionary)
            else:
                lstObject = list()
                for item in dictionary:
                    lstObject.append(class_type(**item))
                return lstObject

        return jsons.loads(json_string, class_type)

    @staticmethod
    def save_file(target_object, file_name: str, schema: Schema = None):
        with open(file_name, 'w') as myfile:
            myfile.write(Json.to_json(target_object, schema))

    @staticmethod
    def deserialize_file(file_name: str, class_type: Type[T], schema: Schema = None) -> T:
        with open(file_name, 'r') as myfile:
            return Json.deserialize(myfile.read(), class_type, schema)

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
