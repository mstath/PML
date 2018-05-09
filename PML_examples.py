if True:

    import PML

    __metaclass__ = PML.PML

    PML.VERBOSE = True

    PML.EXCEPT = True 



###############################################

# EXAMPLE 1 - SIMPLE PRECONDITION/POSTCONDITION

###############################################



class MyList:



	def __init__(self, l):

		"""

		@requires isinstance(l, list)

		@ensures len(self.l) > 0

		"""

		self.l = l



a = MyList([1,2,3])

a = MyList("hello world")

a = MyList([])



##################################################

# EXAMPLE 2 - TYPE CHECKING, ATTRIBUTES, FUNCTIONS

##################################################



class MyList:

	def __init__(self, l):

		self.l = l



	def sortalpha(self):

		"""

		@requires forall([type(self.l[i]) is StringType for i in range(1, len(self.l))])

		@ensures forall([_result[i] >= _result[i-1] for i in range(1, len(_result))])

		"""

		self.l = sorted(self.l)

		return self.l



c = MyList(["pear","banana","apple"])

c.sortalpha()

d = MyList(["pear",5,"banana","orange"])

d.sortalpha()



################################################

# EXAMPLE 3 - STATE

################################################



class MyList:

	def __init__(self, l):

		self.l = l



	def addElement(self,o):

		"""

		@ensures len(self._old.l) == (len(self.l)-1)

		"""

		return self.l.append(o)



e = MyList([1,2,3])

e.addElement(4)

len(e._old.l)

len(e.l)



################################################

# EXAMPLE 4 - INVARIANTS

################################################



class MyList:

	"""

	@invariant len(self.l) > 0

	@invariant len(self.l) <= self.max_size

	"""

	max_size = 4



	def __init__(self, l):

		self.l = l



	def addElement(self,o):

		"""

		@ensures len(self._old.l) == (len(self.l)-1)

		"""

		return self.l.append(o)



f = MyList(["spring","summer","fall","winter"])

f.addElement("monsoon")
