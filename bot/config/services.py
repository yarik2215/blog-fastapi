from typing import Optional
from pydantic import BaseModel

class ConfigData(BaseModel):
    api_url: str
    number_of_users: int
    max_posts_per_user: int
    max_likes_per_user: int


class ConfigReaderBase:
    def read_config(self) -> ConfigData:
        NotImplemented


class Config:
    def __init__(self, config_reader: ConfigReaderBase) -> None:
        self.config_reader = config_reader
        self._config_data = None

    def get_config(self) -> ConfigData:
        if self._config_data is None:
            _config_data = self.config_reader.read_config()
        return _config_data.copy()
