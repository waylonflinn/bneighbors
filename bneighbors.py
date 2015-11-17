
import bvec
import bcolz

import similarity as sim

class Neighborhood:
	'''
	"Don't you want to be my neighbor?"
		bneighbors finds nearest neighbors between two arbitrary vector spaces,
		contained in bcolz databases, using bvec.

	'''

	def __init__(self, source_path):
		'''
			Create the Neighborhood, for finding nearest neighbors.

			Args:
			source_path (string): path to a bcolz database with three carray
			columns: 'id', 'vector' and 'norm'

		'''

		self.source_path = source_path

		# open bcolz datastores
		self.vectors = bvec.carray(rootdir=source_path + "/vector")
		self.norms = bvec.carray(rootdir=source_path + "/norm")
		self.source_table = bcolz.ctable(rootdir=source_path)

		#print("Created similarity object from BCOLZ files: source {0}; target: {1}".format(source_path, target_path))

		# create similarity object
		self.similarity = sim.Similarity(self.vectors, self.norms)

		# create domain <-> index maps

		# dictionary taking ids to indeces (source)
		self.id_index_map = self._create_id_index_map(self.source_table)

		self.index_id_map = self._create_index_id_map(self.source_table)

	@staticmethod
	def _create_id_index_map(ctable):
		'''
		create a dictionary taking ids to indeces (source)
		'''

		i = 0
		id_index_map = {}
		for block in bcolz.iterblocks(ctable['id']):
			for item in block:
				id_index_map[str(item)] = i
				i += 1

		return id_index_map

	@staticmethod
	def _create_index_id_map(ctable):
		'''
		create a dictionary taking an index to an id (target)
		'''

		i = 0
		index_id_map = {}
		for block in bcolz.iterblocks(ctable['id']):
			for item in block:
				index_id_map[i] = str(item)
				i += 1

		return index_id_map


	def neighbors(self, source_id, n=100, sim_type=sim.SimilarityType.Cosine):
		'''
			Find the nearest neighbors of the given source_id
		'''

		if source_id not in self.id_index_map:
			return []

		source_index = self.id_index_map[source_id]

		sorted_target_indeces = self.similarity.similarities(source_index, n=n, sim_type=sim_type)

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

		return self.vectors[source_index]
