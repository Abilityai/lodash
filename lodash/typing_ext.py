from inspect import isclass
from typing import TypeVar, Generic, TypeGuard, Any, get_origin, get_args

def is_method(instance: Any, value: str) -> TypeGuard[str]:
    return hasattr(instance, value) and callable(getattr(instance, value))


def isnt_method(*args, **kwargs) -> TypeGuard[str]:
    return not is_method(*args, **kwargs)


def is_instance(i1, type1) -> bool:
    return is_subclass(i1.__class__, type1)

def type_to_str(type1: Any) -> str:
    if type1 is None:
        return "null"
    elif type1 == dict:
        return 'json'
    elif type1 == list:
        return 'array'
    elif type1 == str:
        return 'string'
    elif type1 == float:
        return 'float'
    elif type1 == int:
        return 'int'
    elif type1 == bool:
        return 'bool'
    else:
        return str(type1)



def is_subclass(type1: Any, type2: Any) -> bool:
    if (not isclass(type1) and not get_origin(type1)) or (not isclass(type2) and not get_origin(type2)):
        return False

    if type1 == type2:
        return True

    origin1 = get_origin(type1)
    origin2 = get_origin(type2)

    if origin1 and origin2:
        if origin1 == origin2 or issubclass(origin1, origin2):
            args1 = get_args(type1)
            args2 = get_args(type2)

            if not args2:
                return True

            return all(is_subclass(arg1, arg2) for arg1, arg2 in zip(args1, args2))

        return False
    elif origin1 and not origin2:
        if origin1 == type2:
            return True

        if issubclass(origin1, type2):
            return True


    if not origin1 and not origin2:
        return issubclass(type1, type2)

    return False


if __name__ == '__main__':
    T = TypeVar('T')

    def assertion(method, *args, result=True):
        res = method(*args)
        assert res == result, f"String split incortly input: {repr(args)}, got: {repr(res)}, expected: {result}"

    class A1:
        pass

    class A2(A1):
        pass

    class B1(Generic[T]):
        pass

    class B2(B1, Generic[T]):
        pass

    assertion(is_subclass, A1, A2, result=False)
    assertion(is_subclass, A2, A1, result=True)
    assertion(is_subclass, A1, A1, result=True)
    assertion(is_subclass, B1, A1, result=False)
    assertion(is_subclass, B1, B1, result=True)
    assertion(is_subclass, B1[A1], B1[A1], result=True)
    assertion(is_subclass, B1[A1], A1, result=False)
    assertion(is_subclass, B1[A1], B1, result=True)
    assertion(is_subclass, B2[A1], B1, result=True)
    assertion(is_subclass, B2[A1], B1[A2], result=False)
    assertion(is_subclass, B1[A1], B2[A2], result=False)
    assertion(is_subclass, B1[A1], A2, result=False)
    assertion(is_subclass, B1[A1], A2, result=False)
    assertion(is_subclass, B2, B1, result=True)
    assertion(is_subclass, B2[A1], B1[A1], result=True)
    assertion(is_subclass, B2, B1[A1], result=False)
    assertion(is_subclass, B2[A2], B1[A1], result=True)
    assertion(is_subclass, A1, None, result=False)
    assertion(is_subclass, None, A1, result=False)
    assertion(is_subclass, None, B1[A1], result=False)

    print("Assertions passed")
