import jsonpickle

class Json:
    @staticmethod
    def to_json(target_object) -> str:
        return jsonpickle.encode(target_object)

    @staticmethod
    def deserialize(json_string: str):
        return jsonpickle.decode(json_string)

    @staticmethod
    def save_file(target_object,file_name: str):
        with open(file_name,'w') as myfile:
            myfile.write(jsonpickle.encode(target_object , indent=4))

    @staticmethod
    def deserialize_file(file_name: str):
        with open(file_name, 'r') as myfile:
            return Json.deserialize(myfile.read())