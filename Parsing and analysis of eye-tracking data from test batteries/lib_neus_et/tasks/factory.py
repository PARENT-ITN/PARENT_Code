from .generic import Generic
from .dummy import Dummy

def TaskFactory(name):

    """
    Returns correct Task class given the name.
    """

    # TODO: use a dictionary instread? 

    if name == 'Dummy':

        return Dummy
    
    elif name == 'Generic':

        return Generic

    raise NotImplementedError(f'Task name "{name}" not recognized.')
