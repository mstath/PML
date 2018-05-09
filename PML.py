# PML - Python Modeling Language

from types import *             # for type checking
from inspect import getcallargs # for getting method parameters
from copy import deepcopy       # for copying _old

VERBOSE = False             # enable 'debug' printing
EXCEPT = False              # halt execution for spec violations

# PML exception classes

class PMLInvariantViolation(BaseException): pass
class PMLRequiresViolation(BaseException): pass
class PMLEnsuresViolation(BaseException): pass
class PMLSpecificationError(BaseException): pass

# _PML__invariants = metaclass method for checking invariants
# self = calling object
# invars = list of invariant expressions

def _PML__invariants(self,invars):

    for exp in invars:

        try:
            assert eval(exp)
        except AssertionError:
            if EXCEPT:
                raise PMLInvariantViolation,exp
            else:
                print 'PMLInvariantViolation:',exp
        except:
            raise PMLSpecificationError,exp

# _PML__requires = meta-class method for checking pre-conditions
# self = calling object
# params = dictionary of arguments and values from object's called method
# reqs = list of pre-condition expressions

def _PML__requires(self,params,reqs):

    for exp in reqs:
        try:
            assert eval(exp,None,params)
        except AssertionError:
            if EXCEPT:
                raise PMLRequiresViolation,exp
            else:
                print 'PMLRequiresViolation:',exp
        except:
            raise PMLSpecificationError,exp

# _PML__ensures = meta-class method for checking post-conditions
# self = calling object
# params = dictionary of arguments and values from object's called method
# ensures = list of post-condition expressions

def _PML__ensures(self,params,ensures):

    for exp in ensures:
        try:
            assert eval(exp,None,params)
        except AssertionError:
            if EXCEPT:
                raise PMLEnsuresViolation,exp
            else:
                print 'PMLEnsuresViolation:',exp
        except:
            raise PMLSpecificationError,exp

# PML_wrap_method = function which wraps methods when metaclass initiates
# method = class method to be wrapped

def PML_wrap_method(cls,method):

    # parse specs
    specs = PML_parse_specs(method.__doc__)

    # definition of replacing method
    def wrapped(*args,**kwargs):

        # set 'self' from first argument (calling object)
        self = args[0]

        # set names and object IDs for VERBOSE mode
        cls_name = cls.__name__
        objID = id(self)
        meth_name = method.__name__

        if VERBOSE:
            print 'Class: %s\tObjectID: %s\tMethod: %s' % (cls_name,objID,meth_name)

        # get arguments and values from object's called method
        params = getcallargs(method,*args,**kwargs)

        # evaluate objects pre-conditions (first argument is calling object)
        _PML__requires(self,params,specs[0])

        # save copy of old values
        setattr(self,'_old',deepcopy(self))

        # execute original method and get return value (None if void)
        _result = method(*args,**kwargs)

        # add _result to dictionary of parameters
        params['_result'] = _result

        # evaluate objects post-conditions (first argument is calling object)
        _PML__ensures(self,params,specs[1])

        # evaluate invariants (first argument is calling object)
        _PML__invariants(self,cls._invars)

        # return value from original method call
        return _result

    # copy original methods doc to wrapped method
    setattr(wrapped,'__doc__',method.__doc__)

    # return wrapped method
    return wrapped

# PML_parse_specs = function which parses specs from doc-strings and
#   returns a tuple containing invariant, pre, and post-condidition specs
# doc = methods doc-string

def PML_parse_specs(doc):

    # lists for collecting specs
    invars = []
    reqs = []
    ensures = []

    if doc:
        # strip white space and put in temp list
        temp = []
        for line in doc.splitlines():
            temp.append(line.strip())

        # split doc into list and iterate
        for line in temp:
            # strip key-words and append expressions to lists

            if '@invariant' in line:
                invars.append(line.lstrip('@invariant'))
            elif '@requires' in line:
                reqs.append(line.lstrip('@requires'))
            elif '@ensures' in line:
                ensures.append(line.lstrip('@ensures'))

    return reqs,ensures,invars # return specs as tuple

# Helper function used in 'Contracts for Python'

def forall(a, fn = bool):
    """Checks that all elements in a sequence are true.

    Returns True(1) if all elements are true.  Return False(0) otherwise.

    Examples:
    >>> forall([True, True, True])
    1
    >>> forall( () )
    1
    >>> forall([True, True, False, True])
    0
    """
    for i in a:
        if not fn(i):
            return False
    return True

# PML metaclass definition

class PML(type):

    # __init__ called when classes get defined
    # cls = class object
    # name = name of class (string)
    # bases = base-classes of cls (tuple)
    # attrs = attributes of cls (dictionary)

    def __init__(cls,name,bases,attrs):

        # add invariants values to class
        setattr(cls,'_invars',PML_parse_specs(cls.__doc__)[2])
        
        # add PML methods to class
        setattr(cls,'__invariants',_PML__invariants)
        setattr(cls,'__requires',_PML__requires)
        setattr(cls,'__ensures',_PML__ensures)

        # itterate through attributes and wrap those which are methods
        for name,attr in attrs.items():
            if callable(attr):
                setattr(cls,name,PML_wrap_method(cls,attr))

        # init class
        super(PML,cls).__init__(name,bases,attrs)

