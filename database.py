import base64
import json
from typing import Dict
import redis
import os
import ast

class RedisObject(object):
    '''
    A base object backed by redis.
    Genrally, use RedisDict or RedisList rather than this directly.
    '''

    def __init__(self, id = None):
        '''Create or load a RedisObject.'''

        self.redis = redis.Redis(host = 'localhost', decode_responses = True)

        if id:
            self.id = id
        else:
            self.id = base64.urlsafe_b64encode(os.urandom(9)).decode('utf-8')

        if ':' not in self.id:
            self.id = self.__class__.__name__ + ':' + self.id

    def __del__(self):
        '''Let the connection go'''
        del self.redis


    def __bool__(self):
        '''Test if an object currently exists'''

        return self.redis.exists(self.id)

    def __eq__(self, other):
        '''Tests if two redis objects are equal (they have the same key)'''

        return self.id == other.id

    def __str__(self):
        '''Return this object as a string for testing purposes.'''

        return self.id

    def delete(self):
        '''Delete this object from redis'''

        self.redis.delete(self.id)

    @staticmethod
    def decode_value(type, value):
        '''Decode a value if it is non-None, otherwise, decode with no arguments.'''

        if value == None:
            return type()
        else:
            if type == list:
                return ast.literal_eval(value) # grab all words
            return type(value)

    @staticmethod
    def encode_value(value):
        '''Encode a value using json.dumps, with default = str'''
        return str(value)



class RedisDict(RedisObject):
    '''An equivalent to dict where all keys/values are stored in Redis.'''

    def __init__(self, id = None, fields = {}, defaults = None):
        '''
        Create a new RedisObject
        id: If specified, use this as the redis ID, otherwise generate a random ID.
        fields: A map of field name to construtor used to read values from redis.
            Objects will be written with json.dumps with default = str, so override __str__ for custom objects.
            This should generally be set by the subobject's constructor.
        defaults: A map of field name to values to store when constructing the object.
        '''

        RedisObject.__init__(self, id)

        self.fields = fields

        if defaults:
            for key, val in defaults.items():
                self[key] = val


    @classmethod
    def as_child(cls, parent, tag, item_type=None):
        '''Alternative callable constructor that instead defines this as a child object'''
        if item_type:
            def helper(_ = None):
                return cls(parent.id + ':' + tag, item_type)
        else:
            def helper(_=None):
                return cls(parent.id + ':' + tag)
        return helper

    def __getitem__(self, key):
        '''
        Load a field from this redis object.
        Keys that were not specified in self.fields will raise an exception.
        Keys that have not been set (either in defaults or __setitem__) will return the default for their type (if set)
        '''

        if key == 'id':
            return self.id

        if not key in self.fields:
            raise KeyError('{} not found in {}'.format(key, self))

        return RedisObject.decode_value(self.fields[key], self.redis.hget(self.id, key))

    def __setitem__(self, key, val):
        '''
        Store a value in this redis object.
        Keys that were not specified in self.fields will raise an exception.
        Keys will be stored with json.dumps with a default of str, so override __str__ for custom objects.
        '''

        if not key in self.fields:
            raise KeyError('{} not found in {}'.format(key, self))

        self.redis.hset(self.id, key, RedisObject.encode_value(val))

    def __iter__(self):
        '''Return (key, val) pairs for all values stored in this RedisDict.'''

        yield ('id', self.id.rsplit(':', 1)[-1])

        for key in self.fields:
            yield (key, self[key])


class RedisList(RedisObject):
    '''An equivalent to list where all items are stored in Redis.'''

    def __init__(self, id = None, item_type = str, items = None):
        '''
        Create a new RedisList
        id: If specified, use this as the redis ID, otherwise generate a random ID.
        item_type: The constructor to use when reading items from redis.
        values: Default values to store during construction.
        '''

        RedisObject.__init__(self, id)

        self.item_type = item_type

        if items:
            for item in items:
                self.append(item)

    @classmethod
    def as_child(cls, parent, tag, item_type):
        '''Alternative callable constructor that instead defines this as a child object'''

        def helper(_ = None):
            return cls(parent.id + ':' + tag, item_type)

        return helper

    def __getitem__(self, index):
        '''
        Load an item by index where index is either an int or a slice
        Warning: this is O(n))
        '''

        if isinstance(index, slice):
            if slice.step != 1:
                raise NotImplementedError('Cannot specify a step to a RedisObject slice')

            return [
                RedisObject.decode_value(self.item_type, el)
                for el in self.redis.lrange(self.id, slice.start, slice.end)
            ]
        else:
            return RedisObject.decode_value(self.item_type, self.redis.lindex(self.id, index))

    def __setitem__(self, index, val):
        '''Update an item by index
        Warning: this is O(n)
        '''

        self.redis.lset(self.id, index, RedisObject.encode_value(val))

    def __len__(self):
        '''Return the size of the list.'''

        return self.redis.llen(self.id)

    def __delitem__(self, index):
        '''Delete an item from a RedisList by index. (warning: this is O(n))'''

        self.redis.lset(self.id, index, '__DELETED__')
        self.redis.lrem(self.id, 1, '__DELETED__')

    def __iter__(self):
        '''Iterate over all items in this list.'''

        for el in self.redis.lrange(self.id, 0, -1):
            yield RedisObject.decode_value(self.item_type, el)

    def lpop(self):
        '''Remove and return a value from the left (low) end of the list.'''

        return RedisObject.decode_value(self.item_type, self.redis.lpop(self.id))

    def rpop(self):
        '''Remove a value from the right (high) end of the list.'''

        return RedisObject.decode_value(self.item_type, self.redis.rpop(self.id))

    def lpush(self, val):
        '''Add an item to the left (low) end of the list.'''

        self.redis.lpush(self.id, RedisObject.encode_value(val))

    def rpush(self, val):
        '''Add an item to the right (high) end of the list.'''

        self.redis.rpush(self.id, RedisObject.encode_value(val))

    def append(self, val):
        self.rpush(val)

    def toJson(self):
        json.dumps(self.__iter__)



class RedisToplist(RedisObject):
    '''An equivalent to sorted list stored in redis'''

    def __init__(self, id = None):
        '''
        Create a new RedisToplist
        id: If specified, use this as the redis ID, otherwise generate a random ID.
        '''

        RedisObject.__init__(self, id)


    def __getitem__(self, key):
        '''
        Load the rank from this redis object.
        '''

        return RedisObject.decode_value(int, self.redis.zrevrank(self.id, key))

    def __setitem__(self, key, val):
        '''Update an item by index
        Warning: this is O(n)
        '''

        self.redis.zadd(self.id, {key: val})

    def getTop(self):
        ''' Get id and name of topmost player as tuple '''
        return RedisObject.decode_value(tuple, self.redis.zrevrange(self.id, 0, 0, withscores=True)[0])

    def getRank(self, player):
        ''' Get Rank of player'''
        return self[player]+1

    def count(self):
        '''Return the size of the list.'''

        return self.redis.zcard(self.id)

class Waypoint(RedisDict):
    def __init__(self, id=None, lon=0, lat=0):
        RedisDict.__init__(self, id=id, fields={
        'lon': float,
        'lat': float,
    }, defaults={
        'lon': lon,
        'lat': lat,
    })

class Url(RedisDict):
    def __init__(self, id=None, url=""):
        RedisDict.__init__(self, id=id, fields={
        'url': str,
        'status': bool,
    }, defaults= {
        'url': url,
        'status': False,
    })
    

class Job(RedisDict):
    def __init__(self, id=None):
        RedisDict.__init__(self,
                                    id=id,
                                    fields={
                                        'wps': RedisList.as_child(self, 'wps', Waypoint),
                                        'status': str,
                                        'finished': bool,
                                        'urls': RedisList.as_child(self, 'urls', Url),
                                    })
        self['status'] = "prepared"

