from collections import defaultdict

seqs = (tuple, list, set, frozenset)

class ConfigDict(defaultdict):
    def __init__(self, initial=None):
        super(ConfigDict, self).__init__(ConfigDict)
        initial = initial or {}
        for key, value in initial.iteritems():
            self.__setitem__(key, value)

    def __setitem__(self, key, value):
        def transform(primitive):
            if isinstance(primitive, dict):
                return ConfigDict(primitive)
            elif isinstance(primitive, seqs):
                seq = type(primitive)
                return seq(transform(v) for v in primitive)
            else:
                return primitive
        super(ConfigDict, self).__setitem__(key, transform(value))

    def __getitem__(self, key):
        return super(ConfigDict, self).__getitem__(key)

    def copy(self):
        return ConfigDict(self)

    def patch(self, overrides):
        overrides = overrides or {}
        for key, value in overrides.iteritems():
            current = self.get(key)
            if isinstance(value, dict) and isinstance(current, dict):
                current.patch(value)
            else:
                self[key] = value

    __setattr__ = __setitem__
    __getattr__ = __getitem__


class AutoPropDescriptor(object):
    def __init__(self, default_prop):
        self.default_prop = default_prop
        self.name = default_prop.__name__
        self.assigned = '_' + self.name

    def __get_assigned__(self, instance):
        return getattr(instance, self.assigned, None)

    def __set_assigned__(self, instance, value):
        return setattr(instance, self.assigned, value)

    def __get__(self, instance, owner):
        value = self.__get_assigned__(instance)
        return value or self.default_prop(instance)

    def __set__(self, instance, value):
        self.__set_assigned__(instance, value)


class AutoPropMetaClass(type):

    def __new__(mcs, cname, cbases, cattrs):
        autoprops = {name: member
                        for name, member in cattrs.iteritems()
                        if getattr(member, 'autoprop', False)}
        for name, member in autoprops.iteritems():
            cattrs[name] = AutoPropDescriptor(member)
        return super(AutoPropMetaClass, mcs).__new__(
                mcs, cname, cbases, cattrs)


class AutoProp(object):

    __metaclass__ = AutoPropMetaClass

    @staticmethod
    def default(f):
        f.autoprop = True
        return f
