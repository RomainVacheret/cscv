import numpy as np
import statistics
import math

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans

from clustering_.display_manager import SummaryElement


class UnexecutedAlgorithm(Exception):
    pass


class AlgorithmElement:
    def __init__(self, func, labels, vectors, kwargs=None, title=None):
        self.func = func
        self.labels = labels
        self.vectors = vectors
        self.kwargs = kwargs or {}
        self.title = title or ''

        self.clusters_ = None
    
    def to_summary_element(self):
        if self.clusters_ is None:
            raise UnexecutedAlgorithm()
            
        data = (self.labels, self.clusters_)
        return SummaryElement(data, self.title, str(self.kwargs))


class AlgorithmManager:
    AGGLOMERATIVE_ALGORITHMS = ['ward', 'complete', 'average', 'single']

    def to_numpy_array(self, data):
        return np.asarray(data)

    def agglo_clustering(self, data, **kwargs):
        data = self.to_numpy_array(data)
        clustering = AgglomerativeClustering(**kwargs).fit(X=data)
        return clustering.labels_

    def kmeans_clustering(self, data, **kwargs):
        data = self.to_numpy_array(data)
        kmeans = KMeans(**kwargs).fit(data)
        return kmeans.labels_
    
    def start_algorithm(self, algorithm_element):
        result = algorithm_element.func(algorithm_element.vectors, **algorithm_element.kwargs)
        algorithm_element.clusters_ = result

        return algorithm_element.to_summary_element()
    
    def compare_algorithms(self, labels, vectors, agglo_kwargs=None, kmeans_kwargs=None):
        if agglo_kwargs is None:
            agglo_kwargs = {}
        
        if kmeans_kwargs is None:
            kmeans_kwargs = {'random_state': 0}

        agglo_algorithm_elements = self._generate_agglomerative_algorithm_elements(
            labels, vectors, agglo_kwargs)

        agglomerative_results = [self.start_algorithm(algo) for algo in agglo_algorithm_elements] 
        average_length = self._get_average_clusters_number(agglomerative_results)

        if 'n_clusters' not in kmeans_kwargs:
            kmeans_kwargs['n_clusters'] = average_length

        kmeans_algorithm_element = self._generate_kmeans_algorithm_elements(labels, vectors, kmeans_kwargs)
        results = [*agglomerative_results, self.start_algorithm(kmeans_algorithm_element)]

        return results
    
    def compare_distance_threshold(self, labels, vectors):
        kwargs = {'n_clusters': None}
        results = []
        
        for algorithm in AlgorithmManager.AGGLOMERATIVE_ALGORITHMS:
            algorithms = []
            kwargs['linkage'] = algorithm
            for threshold in range(1, 16):
                title = f'Agglomerative algorithm with Complete linkage with {threshold} as distance threshold'
                kwargs['distance_threshold'] = threshold
                algorithm_element = AlgorithmElement(
                    self.agglo_clustering,
                    labels,
                    vectors,
                    kwargs.copy(),
                    title
                )

                algorithms.append(algorithm_element)
            
            algorithms_results = [self.start_algorithm(algo) for algo in algorithms]
            clusters_lengths = [len(set(algo.get_clusters())) for algo in algorithms_results]
            results.append({'linkage': algorithm, 'result': clusters_lengths})

        return results
    
    def monitor_cluster_evolution(self, labels, vectors, used_kwargs):
        length = len(vectors)
        results = []
        clusters = []

        for idx in range(1, length):
            data = vectors[:idx + 1]
            result = self.agglo_clustering(data, **used_kwargs)

            clusters.append(len(set(result)))
            results.append(f'Ajout de D{idx} :\n{result}')
        
        text = '\n'.join(results)
        final_text = f'{used_kwargs}\n{text}'

        return final_text, clusters

    
    def _get_average_clusters_number(self, algorithm_elements):
        lengths = [len(set(algo.get_clusters())) for algo in algorithm_elements]
        return math.floor(statistics.mean(lengths))

    def _generate_agglomerative_algorithm_elements(self, labels, vectors, agglo_kwargs):
        algorithm_elements = []

        for algorithm in AlgorithmManager.AGGLOMERATIVE_ALGORITHMS:
            agglo_kwargs['linkage'] = algorithm
            title = f'Agglomerative algorithm with {algorithm.capitalize()} linkage'
            algorithm_element = AlgorithmElement(
                self.agglo_clustering,
                labels,
                vectors,
                agglo_kwargs.copy(),
                title
            )

            algorithm_elements.append(algorithm_element)

        return algorithm_elements

    def _generate_kmeans_algorithm_elements(self, labels, vectors, kmeans_kwargs):
        return AlgorithmElement(
            self.kmeans_clustering,
            labels,
            vectors,
            kmeans_kwargs.copy(),
            'Kmeans algorithm'
        )