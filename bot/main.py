from random import randint
from bot.config import Config, JsonConfigReader


if __name__ == "__main__":
    config = Config(JsonConfigReader('./bot-config.json')).get_config()
    print('Starting automated bot')
    print('Config:', *str(config).split(), sep='\n  ')
    
    