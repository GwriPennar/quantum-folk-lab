# Mathematical Model

For two-family partitioning each tune has one binary variable `x_i`. Related pairs should stay together and dissimilar pairs should separate.

The different-family indicator is `x_i + x_j - 2 x_i x_j`. The same-family indicator is `1 - x_i - x_j + 2 x_i x_j`.

For edge weight `w`, related pairs add `w * different`. Dissimilar pairs add `(1 - w) * same` when the similarity is below a threshold. A balance penalty can add `lambda * (sum_i x_i - target)^2` to discourage trivial all-in-one assignments.

Labels are symmetric: assignments `0011` and `1100` describe the same partition. Exact search may fix the first bit to zero for reporting without changing the optimum.
