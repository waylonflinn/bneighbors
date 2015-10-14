
import bdot
import bcolz

import similarity as sim

class Neighborhood:
	'''
	"Don't you want to be my neighbor?"
		bneighbors finds nearest neighbors between two arbitrary vector spaces, 
		contained in bcolz databases, using bdot.

	'''

	def __init__(self, source_path, target_path):
		'''
			Create the Neighborhood, for finding nearest neighbors.

			Args:
			source_path (string): path to a bcolz database with two carray columns: 'id' and 'vector'
			target_path (string): path to a bcolz database, must be a proper subset of source

		'''

		self.target_path = target_path

		# open bcolz datastores
		self.source_vectors = bdot.carray(rootdir=source_path + "/vector")
		self.target_vectors = bdot.carray(rootdir=target_path + "/vector")
		self.source_table = bcolz.ctable(rootdir=source_path)
		self.target_table = bcolz.ctable(rootdir=target_path)

		#print("Created similarity object from BCOLZ files: source {0}; target: {1}".format(source_path, target_path))

		# create similarity object
		self.similarity = sim.Similarity(self.source_vectors, self.target_vectors)

		# create domain <-> index maps

		# dictionary taking ids to indeces (source)
		self.id_index_map = self._create_id_index_map(self.source_table)

		self.index_id_map = self._create_index_id_map(self.target_table)

	@staticmethod
	def _create_id_index_map(source_table):
		'''
		create a dictionary taking ids to indeces (source)
		'''

		i = 0
		id_index_map = {}
		for block in bcolz.iterblocks(source_table['id']):
			for item in block:
				id_index_map[str(item)] = i
				i += 1

		return id_index_map

	@staticmethod
	def _create_index_id_map(target_table):
		'''
		create a dictionary taking an index to an id (target)
		'''

		i = 0
		index_id_map = {}
		for block in bcolz.iterblocks(target_table['id']):
			for item in block:
				index_id_map[i] = str(item)
				i += 1

		return index_id_map


	def neighbors(self, source_id, n=100):
		'''
			Find the nearest neighbors of the given source_id
		'''

		if source_id not in self.id_index_map:
			return []

		source_index = self.id_index_map[source_id]

		sorted_target_indeces = self.similarity.similarities(source_index, n=n)

		# convert indeces to domain names
		sorted_target_ids = ( (self.index_id_map[index], score) for (index, score) in sorted_target_indeces )

		return sorted_target_ids


	def location(self, source_id):
		'''
			Return the vector (numpy.ndarray) for the given source_id

			source_id: external identifier for the vector
		'''

		if source_id not in self.id_index_map:
			return []

		source_index = self.id_index_map[source_id]

		return self.source_vectors[source_index]


	def add_target(self, source_id):
		'''
		Add a new entry to the target table.

		Args:
			source_id: the external identifier for the entry (domain, primary key, etc)

		Returns:
			the index of the new entry in the table

		this method needs to work like a transaction. nothing should be appended to the
		target ctable while this thing runs.
		'''

		if not source_id in self.id_index_map:
			# not in source
			return -1

		# this solution won't scale
		if source_id in self.index_id_map.values():
			# already a target
			return -1

		source_index = self.id_index_map[source_id]


		# lock start
		target_index = len(self.target_table)

		# the slice hack is a workaround for a bug in append
		self.target_table.append(self.source_table[source_index:source_index+1])

		self.index_id_map[target_index] = source_id

		# lock end

		self.target_table.flush()

		# repoen target vectors
		self.target_vectors = bdot.carray(rootdir=self.target_path + "/vector")

		# this breaks encapsulation, and should recreate the similarity object instead
		self.similarity.target_carray = self.target_vectors

		return target_index

