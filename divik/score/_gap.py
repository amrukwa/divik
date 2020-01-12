from functools import partial

import numpy as np
import pandas as pd
import scipy.spatial.distance as dist
from sklearn.base import clone

from divik._utils import Data, normalize_rows, maybe_pool
from divik._seeding import seeded
from divik.sampler import BaseSampler, UniformSampler


KMeans = 'divik.KMeans'
_BIG_PRIME = 54673


def _dispersion(data: Data, kmeans: KMeans) -> float:
    assert data.shape[0] == kmeans.labels_.size, "kmeans not fit on this data"
    if kmeans.normalize_rows:
        data = normalize_rows(data)
    clusters = pd.DataFrame(data).groupby(kmeans.labels_)
    return float(np.mean([
        np.mean(dist.pdist(cluster_members.values, kmeans.distance))
        for _, cluster_members in clusters
        if cluster_members.shape[0] != 1
    ]))


def _sampled_dispersion(seed: int, sampler: BaseSampler, kmeans: KMeans) \
        -> float:
    X = sampler.get_sample(seed)
    if kmeans.normalize_rows:
        X = normalize_rows(X)
    y = kmeans.fit_predict(X)
    clusters = pd.DataFrame(X).groupby(y)
    return float(np.mean([
        np.mean(dist.pdist(cluster_members.values, kmeans.distance))
        for _, cluster_members in clusters
        if cluster_members.shape[0] != 1
    ]))


@seeded(wrapped_requires_seed=True)
def gap(data: Data, kmeans: KMeans,
        n_jobs: int = None,
        seed: int = 0,
        n_trials: int = 100,
        return_deviation: bool = False) -> float:
    reference_ = UniformSampler(n_rows=None, n_samples=n_trials
                                ).fit(data)
    kmeans_ = clone(kmeans)
    seeds = list(seed + np.arange(n_trials) * _BIG_PRIME)
    with reference_.parallel() as r, maybe_pool(n_jobs) as pool:
        compute_disp = partial(_sampled_dispersion, sampler=r, kmeans=kmeans_)
        ref_disp = pool.map(compute_disp, seeds)
    ref_disp = np.log(ref_disp)
    data_disp = np.log(_dispersion(data, kmeans))
    gap = np.mean(ref_disp) - data_disp
    result = (gap,)
    if return_deviation:
        std = np.sqrt(1 + 1 / n_trials) * np.std(ref_disp)
        result += (std,)
    return result