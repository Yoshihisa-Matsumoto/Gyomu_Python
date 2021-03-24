from gyomu import *
import gyomu.status_code

#from sqlalchemy.orm import sessionmaker

__version__ = "0.0.1.dev"

gyomu.status_code.StatusCode.static_initalize()
gyomu.status_code.StatusCode.SUCCEED_STATUS = gyomu.status_code.StatusCode()


