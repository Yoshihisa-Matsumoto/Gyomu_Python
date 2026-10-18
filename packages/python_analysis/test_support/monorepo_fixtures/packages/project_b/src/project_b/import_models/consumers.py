from project_b.import_models.classes import ImportTestClass
from project_b.import_models.functions import import_test_function
from project_b.import_models.type_aliases import ImportTestAlias
from project_b.import_models.variables import IMPORT_TEST_VALUE

test = IMPORT_TEST_VALUE
cls = ImportTestClass()
import_test_function("abc")
alias: ImportTestAlias = "test"
