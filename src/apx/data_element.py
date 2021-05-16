import apx.base

class DataElement:
    def __init__(self, type_code):
        self.type_code = type_code
        self.lower_limit = None
        self.upper_limit = None
        self.array_len = None

    @property
    def has_limits(self):
        return self.lower_limit is not None
    @property
    def is_array(self):
        return self.array_len is not None

    def set_limits(self, lower_limit, upper_limit):
        if lower_limit is None or upper_limit is None:
            raise ValueError("A 'None' Argument is not allowed")
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def get_limits(self):
        return self.lower_limit, self.upper_limit

