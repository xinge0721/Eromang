import math

class mathematics:
    """
    数学工具类
    """
    def add(self, a:int, b:int) -> int:
        """
        加法
        :param a: 加数
        :param b: 加数
        :return: 和
        """
        return a + b
    def subtract(self, a:int, b:int) -> int:
        """
        减法
        :param a: 被减数
        :param b: 减数
        :return: 差
        """
        return a - b
    def multiply(self, a:int, b:int) -> int:
        """
        乘法
        :param a: 乘数
        :param b: 乘数
        :return: 积
        """
        return a * b
    def divide(self, a:int, b:int) -> float:
        """
        除法
        :param a: 被除数
        :param b: 除数
        :return: 商
        """
        return a / b
    def power(self, a:int, b:int) -> int:
        """
        幂运算
        :param a: 底数
        :param b: 指数
        :return: 幂
        """
        return a ** b
    def sqrt(self, a:int) -> float:
        """
        平方根
        :param a: 被开方数
        :return: 平方根
        """
        return math.sqrt(a)