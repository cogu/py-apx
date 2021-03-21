import apx.base

class DataElement:
    def __init__(self, type_code):
        self.type_code = type_code

    @property
    def has_limits(self):
        return False
    @property
    def is_array(self):
        return False        