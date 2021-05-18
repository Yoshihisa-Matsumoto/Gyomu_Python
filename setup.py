from setuptools import setup

setup(
    name="gyomu",
    version="0.1.5-alpha.2",
    install_requires=["click", "jsonpickle", "jsons","pycryptodome","pyzipper","sqlalchemy"],
    entry_points={
        "console_scripts": [
            "foo = package_name.module_name:func_name",
            "foo_dev = package_name.module_name:func_name [develop]"
        ],
        "gui_scripts": [
            "bar = gui_package_name.gui_module_name:gui_func_name"
        ]
    }
)