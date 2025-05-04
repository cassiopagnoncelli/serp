from os import environ
from io import StringIO
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

from lib.core.env import *
from lib.core.storage import Storage

storage_env = Environment(loader = FileSystemLoader('.'), autoescape=False)
storage_template = storage_env.get_template("config/storage.yml")
storage_rendered = storage_template.render(environ)
storage_config = YAML(typ = "safe").load(StringIO(storage_rendered))

storage = Storage(storage_config[APP_ENV])
