import numpy as np

class SimilarityType:
	Cosine = 1
	Jaccard = 2
	Euclidean = 3
	Lift = 4
	Generalized = 5

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


	def similarities(self, index, n=100, sim_type=SimilarityType.Cosine, p=None):
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
		elif(sim_type == SimilarityType.Generalized):
			if(p == None):
				raise ValueError("Must supply p when using Generalized similarity.")

			similarities = self.generalized(dots, source_norm, p)


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

		norms = self.norm_carray.tondarray()

		# create denominator
		# self.norm_carray^2 + source_norm^2 - similarities
		denominator = (norms ** 2 + source_norm ** 2) - dots

		# divide by norms
		similarities = dots / denominator

		return similarities

	def generalized(self, dots, source_norm, p=2.0):
		"""
			This implements a generalized similarity measure of which cosine
			and lift are special cases. It introduces a parameter which
			modulates the affect of popularity.

			Arguments:
				dots (carray): array of dot products
				source_norm (float64): value of norm of the source vector
				p (float64): popularity parameter. Cosine = 2.0, Lift = 1.0
					larger values of the parameter cause more popular items
					to be more heavily weighted.
					popularity here is expressed by the magnitude of the vector
					in the vector. this always holds for raw preference vectors
					and also generally hold for machine learned results derived
					from preference vectors.
		"""
		# divide by norms
		similarities = dots.divide(source_norm)

		similarities = similarities.tondarray()
		norms = self.norm_carray.tondarray()

		if(p == 2):
			denominator = norms * source_norm
		else:
			denominator = (norms * source_norm) ** (2.0/p)

		similarities = dots / denominator

		similarities[np.isnan(similarities)] = 0

		return similarities
