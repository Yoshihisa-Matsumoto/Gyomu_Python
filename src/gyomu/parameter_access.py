from gyomu.user import User
from gyomu.json import Json
from gyomu.base64 import Base64Encode
from gyomu.aes_encryption import AesEncryption

from socket import gethostname
from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuParamMaster
import threading
import sys
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import date
from typing import Type, TypeVar

T = TypeVar('T')


class ParameterAccess:
    __USER_ROOTKEY: str = "rootKey$"
    __AES_KEY: str = ""
    __ADMIN_AES_KEY: str = ""

    @classmethod
    def __get_key(cls, key: str, user: User = None) -> str:
        if user is not None and key == cls.__USER_ROOTKEY:
            key = gethostname() + "_" + user.userid + "_" + key
        elif user is not None:
            key = user.userid + "_" + key
        return key

    @classmethod
    def __get_aes_key(cls) -> str:
        if cls.__AES_KEY != "":
            return cls.__AES_KEY
        key_val = cls.get_base64_encoded_value("gyomu_aes_key")
        if key_val == "":
            raise ValueError("AES Key Not Setup. Please ask Developer")
        cls.__AES_KEY = key_val
        return cls.__AES_KEY

    @classmethod
    def __load_parameter(cls, key: str, session: Session = None) -> list[GyomuParamMaster]:
        if session is None:
            session = DbConnectionFactory.get_gyomu_db_session()

        with session:
            return session.query(GyomuParamMaster).filter(GyomuParamMaster.item_key == key).all()

    @classmethod
    def __key_exists(cls, key: str, session: Session = None) -> bool:
        param_values = cls.__load_parameter(key, session)
        return param_values is not None and len(param_values) > 0

    @classmethod
    def __set_string_value(cls, key: str, string_value: str, user: User = None):
        key = cls.__get_key(key, user)
        target_object: GyomuParamMaster
        with DbConnectionFactory.get_gyomu_db_session() as session:
            if cls.__key_exists(key, session):
                target_object = session.query(GyomuParamMaster).filter(GyomuParamMaster.item_key == key).first()
                if string_value == "":
                    if target_object is not None:
                        session.delete(target_object)
                else:
                    target_object.item_value = string_value
            elif string_value != "":
                target_object = GyomuParamMaster()
                target_object.item_key = key
                target_object.item_value = string_value
                target_object.item_fromdate = ""
                session.add(target_object)
            session.commit()

    __lock = threading.Lock()

    @classmethod
    def __get_string_value(cls, key: str, user: User = None, target_date: date = date.min) -> str:
        key = cls.__get_key(key, user)
        param_values: list[GyomuParamMaster]
        with cls.__lock:
            cnt_error: int = 0
            while cnt_error < 3:
                try:
                    param_values = cls.__load_parameter(key)
                    break
                except:
                    cnt_error += 1
                    if cnt_error >= 3:
                        raise sys.exc_info()[0]

        if param_values is None:
            return ""

        value: GyomuParamMaster = param_values[0]

        if target_date is not None:
            date_yyyymmdd: str = target_date.strftime('%Y%m%d')
            param_values.sort(key=lambda x: x.item_fromdate, reverse=True)
            for param_value in param_values:
                from_date = param_value.item_fromdate
                if from_date is None or from_date == "":
                    continue
                from_date = from_date.strip()
                if from_date is None or from_date == "":
                    value = param_value
                elif from_date == date_yyyymmdd:
                    value = param_value
                    break
                elif date_yyyymmdd > from_date:
                    value = param_value
                else:
                    break

        if value is None:
            return ""
        return value.item_value

    @classmethod
    def get_string_value(cls, key: str, user: User = None, target_date: date = date.min) -> str:
        return cls.__get_string_value(key, user, target_date)

    @classmethod
    def get_int_value(cls, key: str, user: User = None, target_date: date = date.min) -> int:
        str_value = cls.__get_string_value(key, user, target_date)
        if str_value is None or str_value == "":
            return 0
        return int(str_value)

    @classmethod
    def get_bool_value(cls, key: str, user: User = None, target_date: date = date.min) -> bool:
        str_value = cls.__get_string_value(key, user, target_date)
        return str_value == "True"

    @classmethod
    def get_decimal_value(cls, key: str, user: User = None, target_date: date = date.min) -> Decimal:
        str_value = cls.__get_string_value(key, user, target_date)
        if str_value is None or str_value == "":
            return Decimal(0)
        return Decimal(str_value)

    @classmethod
    def get_json_serialized_value(cls, key: str, class_type: Type[T], user: User = None,
                                  target_date: date = date.min) -> T:
        str_value = cls.__get_string_value(key, user, target_date)
        if str_value is None or str_value == "":
            return None
        return Json.deserialize(str_value, class_type)

    @classmethod
    def get_base64_encoded_value(cls, key: str, user: User = None, target_date: date = date.min):
        str_value = cls.__get_string_value(key, user, target_date)
        if str_value is None or str_value == "":
            return ""
        return Base64Encode.decode_string(str_value)

    @classmethod
    def get_aes_encryption_value(cls, key: str, user: User = None, target_date: date = date.min):
        aes_key: str = cls.__get_aes_key()
        encrypted_value = cls.__get_string_value(key, user, target_date)
        if encrypted_value == "":
            return ""
        return AesEncryption.aes_decrypt(encrypted_value, aes_key)

    @classmethod
    def set_string_value(cls, key: str, string_value: str, user: User = None):
        cls.__set_string_value(key, string_value, user)

    @classmethod
    def set_bool_value(cls, key: str, bool_value: bool, user: User = None):
        cls.__set_string_value(key, "True" if bool_value == True else "False", user)

    @classmethod
    def set_int_value(cls, key: str, int_value: int, user: User = None):
        cls.__set_string_value(key, str(int_value), user)

    @classmethod
    def set_decimal_value(cls, key: str, decimal_value: Decimal, user: User = None):
        cls.__set_string_value(key, str(decimal_value), user)

    @classmethod
    def set_json_serialized_value(cls, key: str, object, user: User = None):
        json_value: str = ""
        if object is not None:
            json_value = Json.to_json(object)
        cls.__set_string_value(key, json_value, user)

    @classmethod
    def set_base64_encoded_value(cls, key: str, string_value: str, user: User = None):
        base64_value: str = ""
        if string_value != "":
            base64_value = Base64Encode.encode_string(string_value)
        cls.__set_string_value(key, base64_value, user)

    @classmethod
    def set_aes_encrypted_value(cls, key: str, string_value: str, user: User = None):
        aes_encrypted: str = ""
        aes_key: str = cls.__get_aes_key()
        if string_value != "":
            aes_encrypted = AesEncryption.aes_encrypt(aes_key, string_value)
        cls.__set_string_value(key, aes_encrypted, user)
