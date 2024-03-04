from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Algorithm(Enum):
    AGGLOMERATIVE_CLUSTERING = 'AGGLOMERATIVE'
    SPECTRAL_CLUSTERING = 'SPECTRAL'

    @classmethod
    def get_default(cls) -> 'Algorithm':
        return cls.AGGLOMERATIVE_CLUSTERING


class Metric(Enum):
    AVERAGE = 'AVG'
    MAXIMUM = 'MAX'
    MINIMUM = 'MIN'
    INTERSECTION = 'INTERSECTION'

    @classmethod
    def get_default(cls) -> 'Metric':
        return cls.AVERAGE


class Preprocessing(Enum):
    NONE = None
    CDF = 'CDF'

    @classmethod
    def get_default(cls) -> 'Preprocessing':
        return cls.CDF

    def to_cli_flag(self) -> str:
        mapper = {
            Preprocessing.NONE: '--cluster-pp-none',
            Preprocessing.CDF: '--cluster-pp-cdf',
        }

        return mapper[self]


class InterClusterSimilarity(Enum):
    MINIMUM = 'MIN'
    MAXIMUM = 'MAX'
    AVERAGE = 'AVERAGE'

    @classmethod
    def get_default(cls) -> 'InterClusterSimilarity':
        return cls.AVERAGE


@dataclass
class JPlagConfiguration:
    algorithm: Algorithm = Algorithm.get_default()
    metric: Metric = Metric.get_default()
    preprocessing: Preprocessing = Preprocessing.get_default()
    # Agglomerative clustering options
    threshold: float = 0.2
    inter_cluster_similarity: InterClusterSimilarity = InterClusterSimilarity.get_default()
    # Spectral clustering options
    bandwidth: float = 20.0
    noise: float = 0.0025
    min_runs: int = 5
    max_runs: int = 50
    k_means_iterations: int = 200

    def to_file_path(self) -> Path:
        elements = [f'{self.algorithm.value}-{self.metric.value}-{self.preprocessing.value}']

        match self.algorithm:
            case Algorithm.AGGLOMERATIVE_CLUSTERING:
                args = [self.threshold, self.inter_cluster_similarity]
            case Algorithm.SPECTRAL_CLUSTERING:
                args = [self.bandwidth, self.noise, self.min_runs, self.max_runs, self.k_means_iterations]
            case _:
                raise NotImplementedError(f'Unknown algorithm: {self.algorithm}')

        elements.extend(map(str, args))

        return Path(*elements)
