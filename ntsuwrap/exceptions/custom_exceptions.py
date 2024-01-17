class EmptyResponseError(Exception):
    '''Raise if API call returns empty list at the top level'''
    pass

class PartialResponseError(Exception):  #Or maybe KeyError/ValueError?
    '''Raise if nested dictionary or list are empty'''
    pass