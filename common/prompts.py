import json

class Prompts:
    def __init__(self, file_path='config.json'):
        self.file_path = "./prompts_config.json"
        self.config = self.read_config()

    def read_config(self):
        """读取JSON格式的配置文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                return config_data
        except FileNotFoundError:
            print(f"Error: Config file '{self.file_path}' not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{self.file_path}'.")
            return {}

    def get_value(self, key):
        """获取配置文件中指定键的值"""
        try:
            value = self.config[key]
            return value
        except KeyError:
            print(f"Error: Key '{key}' not found in the configuration file.")


