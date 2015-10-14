import numpy as np


class Similarity:


	def __init__(self, source_carray, target_carray):
		'''
		Create a similarity store based on vectors stored in two bcolz datastores.
		Input index is into source_file, result indexes will be from the target_file.

		Args:
			source_file (string): path to the bcolz datastore containing query vectors
			target_file (string): path to the bcolz datastore containing response vectors
		'''

		self.source_carray = source_carray
		self.target_carray = target_carray


	def similarities(self, index, n=100):
		'''
		Return a list of objects similar to the given one, along with their scores.
		Tuples containing index and similarity score are returned, restricted to the top n.
		Input index is into source_file, result indexes will be from the target_file.

		Args:
			index (int): the index of the object from the source vector store to get similarities for
		'''

		source_vector = self.source_carray[index]

		# calc dots
		similarities = self.target_carray.dot(source_vector)

		# sorted 
		index_similarities_sorted = np.argsort(similarities)[::-1][:n]


		return zip(index_similarities_sorted, similarities[index_similarities_sorted])
