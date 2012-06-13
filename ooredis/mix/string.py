# coding: utf-8

__all__ = ['String']

__metaclass__ = type

import redis.exceptions as redispy_exception

from ooredis.mix.key import Key
from ooredis.const import REDIS_TYPE
from ooredis.mix.helper import format_key

class String(Key):
    """
    为储存单个值的 Key 对象提供 set，get 和 getset操作。
    """

    def __repr__(self):
        return format_key(self, self.name, self.get())

    def set(self, python_value, preserve=False, expire=None):
        """
        为 Key 对象指定值。

        Args:
            python_value: 为 Key 对象指定的值。
            preserve: 指示是否不覆盖原本储存的值。
            expire: 设置 Key 对象的过期时间，以秒为单位。

        Time:
            O(1)

        Returns:
            None

        Raises:
            TypeError: 当 key 非空但 Key 对象不是指定类型时抛出。
            ValueError: 根据 preserve 参数的情况抛出。
        """
        # set 命令可以无视类型进行设置的命令， 为了保证类型的限制
        # ooredis 里对一个非 string 类型进行 set 将引发 TypeError 异常。
        if self.exists and self._represent != REDIS_TYPE['string']:
                raise TypeError

        if self.exists and preserve:
            raise ValueError
       
        redis_value = self._type_case.to_redis(python_value)
        if expire:
            self._client.setex(self.name, redis_value, expire)
        else:
            self._client.set(self.name, redis_value)

    def setnx(self, python_value):
        """
        将 Key 对象的值设为 python_value ，当且仅当 Key 不存在。

        Args:
            python_value

        Time:
            O(1)

        Returns:
            bool: 如果设置成功，那么返回 True ，否则返回 False 。

        Raises:
            TypeError: 当 Key 对象非空且不是 Redis 的字符串类型时抛出。
        """
        # setnx 命令可以无视类型进行设置的命令， 为了保证类型的限制
        # ooredis 里对一个非 string 类型进行 setnx 将引发 TypeError 异常。
        if self.exists and self._represent != REDIS_TYPE['string']:
            raise TypeError

        redis_value = self._type_case.to_redis(python_value)
        return self._client.setnx(self.name, redis_value)

    def setex(self, python_value, ttl_in_second):
        """
        将 Key 对象的值设为 python_value ，
        并将 Key 对象的生存时间设为 ttl_in_second 。

        Args:
            python_value
            ttl_in_second: 生存时间，以秒为单位。

        Time:
            O(1)

        Returns:
            None

        Raises:
            TypeError: 当 Key 对象非空且不是 Redis 的字符串类型时抛出。
        """
        # setex 命令可以无视类型进行设置的命令， 为了保证类型的限制
        # ooredis 里对一个非 string 类型进行 setex 将引发 TypeError 异常。
        if self.exists and self._represent != REDIS_TYPE['string']:
            raise TypeError

        redis_value = self._type_case.to_redis(python_value)

        return self._client.setex(self.name, redis_value, ttl_in_second)

    def get(self):
        """
        返回 Key 对象的值。

        Time:
            O(1)

        Returns:
            python_value： Key 对象的值。
            None: key 不存在时返回。

        Raises:
            TypeError: 当 key 非空但 Key 对象不是指定类型时抛出。
        """
        try:
            redis_value = self._client.get(self.name)

            python_value = self._type_case.to_python(redis_value)
            return python_value
        except redispy_exception.ResponseError:
            raise TypeError

    def getset(self, python_value):
        """ 
        修改 Key 对象的值，并返回 Key 对象之前储存的值。

        Args:
            python_value: Key 对象的新值。

        Time:
            O(1)

        Returns:
            None: 当 key 不存时(没有前值)返回。
            python_value:  Key 对象之前的值。

        Raises:
            TypeError: 当 key 非空但 Key 对象不是指定类型时抛出。
        """
        try:
            new_redis_value = self._type_case.to_redis(python_value)

            old_redis_value = self._client.getset(self.name, new_redis_value)

            python_value = self._type_case.to_python(old_redis_value)
            return python_value
        except redispy_exception.ResponseError:
            raise TypeError
