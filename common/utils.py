
class DictInverter:
    @staticmethod
    def get_reverse(dictionary):
        keys = dictionary.keys()
        values = dictionary.values()
        
        if not len(values) == len(set(values)):
            raise ValueError('Dictionary must has unique values for get reverse.')
        
        return dict(zip(values, keys))