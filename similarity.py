import numpy as np

class SimilarityType:
	Cosine = 1
	Jaccard = 2
	Euclidean = 3
	Lift = 4

class Similarity:


	def __init__(self, vector_carray, norm_carray):
		'''
		Create a similarity store based on vectors stored in two bcolz datastores.
		Input index is into source_file, result indexes will be from the target_file.

		Args:
			source_file (string): path to the bcolz datastore containing query vectors
			target_file (string): path to the bcolz datastore containing response vectors
		'''

		self.vector_carray = vector_carray
		self.norm_carray = norm_carray


	def similarities(self, index, n=100, sim_type=SimilarityType.Cosine):
		'''
		Return a list of objects similar to the given one, along with their scores.
		Tuples containing index and similarity score are returned, restricted to the top n.
		Input index is into source_file, result indexes will be from the target_file.

		Args:
			index (int): the index of the object from the source vector store to get similarities for
		'''

		source_vector = self.vector_carray[index]
		source_norm = self.norm_carray[index]

		# calc dots
		dots = self.vector_carray.dot(source_vector)

		if(sim_type == SimilarityType.Cosine):
			# cosine similarity
			similarities = self.cosine(dots, source_norm)
		elif(sim_type == SimilarityType.Jaccard):
			similarities = self.jaccard(dots, source_norm)

		# sorted
		index_similarities_sorted = np.argsort(similarities)[::-1][:n]


		return zip(index_similarities_sorted, similarities[index_similarities_sorted])

	def cosine(self, dots, source_norm):
		# divide by norms
		similarities = dots.divide(source_norm)

		similarities = similarities.divide(self.norm_carray)

		similarities = similarities.tondarray()
		similarities[np.isnan(similarities)] = 0

		return similarities

	def jaccard(self, dots, source_norm):
		dots = dots.tondarray()

		# create denominator
		# self.norm_carray^2 + source_norm^2 - similarities
		norms = self.norm_carray.tondarray()

		denominator = (norms ** 2 + source_norm ** 2) - dots

		# divide by norms
		similarities = dots / denominator

		return similarities
