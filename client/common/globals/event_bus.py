"""
全局事件总线
用于模块间通信
"""

from typing import Callable, Dict, List


class EventBus:
    """事件总线单例"""

    _instance = None
    _subscribers: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def subscribe(self, event_name: str, callback: Callable):
        """订阅事件"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, data=None):
        """发布事件"""
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(data)

    def unsubscribe(self, event_name: str, callback: Callable):
        """取消订阅"""
        if event_name in self._subscribers:
            self._subscribers[event_name].remove(callback)


# 全局事件总线实例
event_bus = EventBus()
