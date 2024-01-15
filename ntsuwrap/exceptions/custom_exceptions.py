class EmptyResponseError(Exception):
    '''Raise if API call returns empty list at the top level'''
    pass

class PartialResponseError(Exception):  #Or maybe KeyError/ValueError?
    '''Raise if nested dictionary or list are empty'''
    pass

def exception_usecase(_dict: dict, key: str):
    try:
        if not _dict == {} and not _dict.get(key) == None:
            thing = _dict.get(key)
            return thing
        else:
            raise PartialResponseError
    except PartialResponseError as e:
        print(f'Something went wrong trying to access {key} at {_dict}, defaulting to None')
        log(e)
        return None