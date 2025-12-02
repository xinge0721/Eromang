import json
from tools import logger
class MYJson:
    # 合并两个JSON文件
    @staticmethod
    def merge(filepath1:dict, filepath2:dict) -> dict:
        dpath.util.merge(filepath1, filepath2)
        return filepath1
    # 删除JSON文件中的某个键
    @staticmethod
    def delete(filepath:dict, key:str) -> dict:
        dpath.util.delete(filepath, key)
        return filepath
    # 修改JSON文件中的某个键
    @staticmethod
    def modify(filepath:dict, key:str, value:str) -> dict:
        dpath.util.set(filepath, key, value)
        return filepath
    # 读取JSON文件
    @staticmethod
    def read(filepath:dict) -> dict:
        return filepath
    # 写入JSON文件
    @staticmethod
    def write(filepath:dict, data:dict) -> dict:
        dpath.util.set(filepath, data)
        return filepath
    # 清空JSON文件
    @staticmethod
    def clear(filepath:dict) -> dict:
        dpath.util.clear(filepath)
        return filepath