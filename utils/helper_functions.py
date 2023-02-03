from typing import Optional, Mapping, Any, Union

JSONType = Mapping[str, Any]







def success(operation: str, msg: str, data: Optional[JSONType] = None) -> JSONType:
    """
    This function returns a formatted dictionary for the successful cases.
    Args:
        operation (str): Operation successfully completed
        msg (str): Sucessful Message
        data (Optional[JSONType], optional): Data to be sent. Defaults to None.
    Returns:
        JSONType: Formatted Dictionary
    """
    return {
        "operation": operation,
        "success": True,
        "message": msg,
        "data": data,
    }



def failure(operation: str, msg: str) -> Mapping[str, Union[str, bool]]:
    """
    This function returns a formatted dictionary for the failure cases, or exceptions.
    Args:
        operation (str): Operation that failed
        msg (str): Failure Message
    Returns:
        Mapping[str, Union[str, bool]]: Formatted Dictionary
    """
    return {
        "operation": operation,
        "success": False,
        "message": msg,
    }