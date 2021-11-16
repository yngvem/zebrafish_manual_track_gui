from json import JSONEncoder
import pickle


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return {'_python_object': pickle.dumps(obj)}


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct
