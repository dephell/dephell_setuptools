# built-in
from configparser import ConfigParser
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Union

# external
try:
    from setuptools.config import ConfigMetadataHandler, ConfigOptionsHandler
except ImportError:
    # In setuptools v61.0.0, everything was moved to setuptools.config.setupcfg.
    # see https://github.com/pypa/setuptools/commit/49b7a60050836868ecd63dc38ad0729626a356f3
    from setuptools.config.setupcfg import ConfigMetadataHandler, ConfigOptionsHandler

# app
from ._base import BaseReader
from ._cached_property import cached_property
from ._constants import FIELDS


class CfgReader(BaseReader):
    def __init__(self, path: Union[str, Path]):
        self.path = self._normalize_path(path, default_name='setup.cfg')

    @cached_property
    def content(self) -> Dict[str, Any]:
        path = self.path
        if path.name == 'setup.py':
            path = path.parent / 'setup.cfg'
            if not path.exists():
                raise FileNotFoundError(str(path))

        parser = ConfigParser()
        parser.read(str(path))

        options = deepcopy(parser._sections)  # type: ignore
        for section, content in options.items():
            for k, v in content.items():
                options[section][k] = ('', v)

        container = type('container', (), dict.fromkeys(FIELDS))()
        ConfigOptionsHandler(container, options).parse()
        ConfigMetadataHandler(container, options).parse()

        return self._clean(vars(container))
