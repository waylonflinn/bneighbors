# bneighbors
Find exact nearest neighbors in relatively high dimensional spaces. Supports
in-memory and out-of-core data sets (via [bcolz](https://github.com/Blosc/bcolz)
and [bvec](https://github.com/waylonflinn/bvec)).

Gives realtime performance in 20-100 dimensional feature spaces, over hundreds of
thousands of items.

Includes the following similarity measures

* cosine
* jaccard
* generalized


The generalized similarity measure is based on an alternate normalization of
cosine similarity, and includes both cosine similarity and lift as special cases.


## todo
* efficient calculation of a relevant subset of
[Bregman Divergences](https://en.wikipedia.org/wiki/Bregman_divergence)
* subsetting of feature vectors for inclusion in results with boolean vectors (carrays)
