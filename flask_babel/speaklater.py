# -*- coding: utf-8 -*-
from babel.support import LazyProxy
from flask_babel._compat import text_type


class LazyString(LazyProxy):
    def __html__(self):
        return text_type(self)

    def __setstate__(self, state):
        object.__setattr__(self, '_func', state['_func'])
        object.__setattr__(self, '_args', state['_args'])
        object.__setattr__(self, '_kwargs', state['_kwargs'])
        object.__setattr__(
            self,
            '_is_cache_enabled',
            state['_is_cache_enabled']
        )
        object.__setattr__(self, '_value', state['_value'])


    def __getstate__(self):
        return {
            '_func': self._func,
            '_args': self._args,
            '_kwargs': self._kwargs,
            '_is_cache_enabled': self._is_cache_enabled,
            '_value': self._value
        }
