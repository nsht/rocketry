
import os
import sys
from typing import Any, Callable, Optional
import warnings
try:
    from typing import Literal
except ImportError: # pragma: no cover
    from typing_extensions import Literal

from rocketry.core.parameters import BaseArgument, Parameters
from rocketry.core.utils import filter_keyword_args

class NotSet:
    def __repr__(self):
        return 'NOTSET'

NOTSET = NotSet()

class SimpleArg(BaseArgument):
    """A simple argument.

    Parameters
    ----------
    value : Any
        Value of the argument.

    """
    def __init__(self, value:Any):
        self._value = value

    def get_value(self, task=None, **kwargs) -> Any:
        return self._value

class Arg(BaseArgument):
    """A simple argument got from the session

    Parameters
    ----------
    value : Any
        Value of the argument.

    """
    def __init__(self, key:Any, default=NOTSET):
        self.key = key
        self.default = default

    def get_value(self, task=None, session=None, **kwargs) -> Any:
        if session is None:
            session = task.session
        try:
            return session.parameters._get(self.key, task=task, session=session, **kwargs)
        except KeyError:
            if self.default is NOTSET:
                raise
            return self.default

    def __str__(self):
        return self.key

    def __repr__(self):
        return f'session.parameters[{repr(self.key)}]'

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.key == other.key
        else:
            return False

class Session(BaseArgument):
    "An argument that represents the session"

    def get_value(self, task=None, session=None, **kwargs) -> Any:
        if session is not None:
            return session
        else:
            return task.session

    def __repr__(self):
        return f'session'

class Task(BaseArgument):
    "An argument that represents a task"

    def __init__(self, name=None):
        self.name = name

    def get_value(self, task=None, **kwargs) -> Any:
        if self.name is None:
            return task
        else:
            return task.session[self.name]

    def __repr__(self):
        return f'Task({repr(self.name) if self.name is not None else ""})'

class Return(BaseArgument):
    """A return argument

    Return is an argument which value represents
    the return of a task.

    Parameters
    ----------
    name : str
        Name of the task which return value the argument 
        represents.

    Examples
    --------

    .. code-block:: python

        from rocketry.arguments import Return
        from rocketry.tasks import FuncTask

        # Create a task with a return
        @FuncTask()
        def my_task_1():
            ...
            return data

        @FuncTask(parameters={"myarg": Return('my_task_1')})
        def my_task_2(myarg):
            ...
    """

    def __init__(self, task_name, default=NOTSET):
        self.task_name = task_name
        self.default = default

    def get_value(self, task=None, session=None, **kwargs) -> Any:
        if session is None:
            session = task.session
        try:
            input_task = session[self.task_name]
        except KeyError:
            raise ValueError(f"Task {repr(self.task_name)} does not exists. Cannot get return value")
        try:
            return session.returns[input_task]
        except KeyError:
            if self.default is NOTSET:
                raise KeyError(f"Return value not found for {repr(task)}")
            return self.default

    def __repr__(self):
        return f'Return({repr(self.task_name)}{"" if self.default is None else ", default=" + repr(self.default)})'

    def __str__(self):
        return f'Return of {self.task_name!r}'

class FuncArg(BaseArgument):
    """An argument which value is defined by the 
    return value of given function.

    Parameters
    ----------
    func : Callable
        Function that is executed and passed as value.
    *args : tuple
        Positional arguments passed to func.
    **kwargs : dict
        Keyword arguments passed to func.

    Examples
    --------

    Simple example:

    .. code-block:: python

        from rocketry.tasks import FuncTask
        from rocketry.arguments import FuncArg

        def my_func():
            ...
            return obj

        @FuncTask(parameters={"my_param": FuncArg(my_func)})
        def my_task(my_param):
            ...

    Example to set to session:

    .. doctest:: funcarg

        >>> from rocketry.arguments import FuncArg

    The ``session.parameters`` were updated.

    .. doctest:: funcarg

        >>> from rocketry import session
        >>> session.parameters
        Parameters(myarg1=FuncArg(myarg1), myarg2=FuncArg(myfunc))
    """
    def __init__(self, __func:Callable, *args, materialize:Optional[Literal['pre', 'post']]=None, **kwargs):
        self.func = __func
        self.materialize = materialize
        self.args = args
        self.kwargs = kwargs

    def get_value(self, **kwargs):
        return self(**kwargs)

    def __call__(self, **kwargs):
        param_kwargs = Parameters._from_signature(self.func)
        params = param_kwargs.materialize(**kwargs)
        return self.func(*self.args, **params, **self.kwargs)

    def stage(self, **kwargs):
        session = kwargs['session']
        materialize = self.materialize if self.materialize is not None else session.config.param_materialize

        if materialize == "pre":
            return self.get_value(**kwargs)
        else:
            return self

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}({self.func.__name__})'

class TerminationFlag(BaseArgument):

    def get_value(self, task=None, session=None, **kwargs) -> Any:
        execution = task.execution
        if execution in ("process", "main"):
            warnings.warn(f"Passing termination flag to task with 'execution_type={execution}''. Flag cannot be used.")
        return task._thread_terminate

    def __repr__(self):
        return 'TerminationFlag()'

    def __str__(self):
        return 'termination flag'

class EnvArg(BaseArgument):
    """Argument that has the value of an environment variable"""

    def __init__(self, var, default=NOTSET):
        self.var = var
        self.default = default

    def get_value(self, **kwargs) -> Any:
        try:
            return os.environ[self.var]
        except KeyError:
            if self.default is NOTSET:
                raise
            return self.default

class CliArg(BaseArgument):
    """Argument that has the value of a command line argument"""

    cli_args = sys.argv

    def __init__(self, param, default=NOTSET):
        self.param = param
        self.default = default

    def get_value(self, **kwargs) -> Any:
        return self._get_arg(self.cli_args)

    def _get_arg(self, args:list):
        arg_name = self.param
        for i, arg in enumerate(args):
            if arg == arg_name:
                break
        else:
            if self.default is NOTSET:
                raise KeyError("CLI argument not found")
            else:
                return self.default
        return args[i+1]