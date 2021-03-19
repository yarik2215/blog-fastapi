import json
from .services import ConfigReaderBase, ConfigData

class JsonConfigReader(ConfigReaderBase):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
    
    def read_config(self) -> ConfigData:
        with open(self.file_path, 'r') as file:
            return ConfigData(**json.load(file))
