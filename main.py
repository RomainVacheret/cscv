import matplotlib.pyplot as plt

from pprint import pprint

from clustering_.algorithms import AlgorithmManager, AlgorithmElement
from clustering_.display_manager import DisplayManager

from parsing.vector import Vector
from parsing.study_manager import StudyManager
from parsing.ast_visitor import FunctionOutput


def get_selected_funcs(funcs_names):
    study_manager = StudyManager()
    study_manager.file_manager.set_default_path('./parsing/resources/files')
    selected_funcs = study_manager.select_from_names(funcs_names)

    return selected_funcs


def filter_funcs(funcs):
    non_empty_lists = StudyManager.filter_non_empty_list(funcs)
    merged_list = StudyManager.merge_lists(non_empty_lists)

    return merged_list


def init_data(funcs, vector_summary=False, display_vectors=True):
    # From data upload to labeled data
    selected_funcs = get_selected_funcs(funcs)
    merged_list = filter_funcs(selected_funcs)
    # FunctionOutput.label_elements(merged_list)

    display_manager = DisplayManager(None, None)

    # Export the content of the vectors
    if vector_summary:
        text = FunctionOutput.summarize_elements(merged_list)
        display_manager.save_as_file(text, 'vector-summary.txt')
    
    if display_vectors:
        vectors = [fnc_outp.vector for fnc_outp in merged_list]
        text = '\n'.join(f'D{idx}:\n {vector}' for idx, vector in enumerate(vectors))
        display_manager.save_as_file(text, 'vectors.txt')

    # Conversion to list of ints
    vectors, contexts = FunctionOutput.split_context_list(merged_list)
    vectors_as_list = Vector.vector_list_to_list_of_list(vectors)

    return contexts, vectors_as_list


def compare_algorithms(funcs, save_as_file=False):
    labels, vectors = init_data(funcs)

    algorithm_manager = AlgorithmManager()
    agglo_kwargs = {'n_clusters': None, 'distance_threshold': 5}
    kmeans_kwargs = {'random_state': 0}

    results = algorithm_manager.compare_algorithms(
        labels, 
        vectors, 
        agglo_kwargs, 
        kmeans_kwargs
    )
    
    display_manager = DisplayManager(None, labels)
    result_as_string = display_manager.build_summary(results)
    print(result_as_string) 

    if save_as_file:
        display_manager.save_as_file(result_as_string) 
    
def foo():
    study_manager = StudyManager()
    study_manager.file_manager.set_default_path('./parsing/resources/x')
    selected_funcs = study_manager.select_from_names(['tri_a_bulle'])
    merged_list = filter_funcs(selected_funcs)
    # FunctionOutput.label_elements(merged_list)
    display_manager = DisplayManager(None, None)

    vectors = [fnc_outp.vector for fnc_outp in merged_list]
    text = '\n'.join(f'D{idx}:\n {vector}' for idx, vector in enumerate(vectors))
    display_manager.save_as_file(text, 'vectors2.txt')

    # Export the content of the vectors
    text = FunctionOutput.summarize_elements(merged_list)

    print(text)

def _display_distance_threshold(results):
    for algo in results:

        length = len(algo['result'])
        plt.plot(range(1, length + 1), algo['result'], label=f'{algo["linkage"]} linkage')

    plt.xlabel('distance_threshold')
    plt.ylabel('nombre de clusters')
    plt.legend()
    plt.show()

def compare_distance_threshold(funcs):
    labels, vectors = init_data(funcs)
    algorithm_manager = AlgorithmManager()

    results = algorithm_manager.compare_distance_threshold(labels, vectors)

    pprint(results) 
    _display_distance_threshold(results)


def _display_cluster_count(clusters):
    clusters.insert(0, 1)
    length = len(clusters)

    plt.plot(range(1, length + 1), clusters)
    plt.xlabel('nombre de données étudiées')
    plt.ylabel('nombre de clusters')
    plt.show()

def _plot_cluster_count():
    length = 15

    plt.plot(range(1, length + 1), [1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6], label='ward')
    plt.plot(range(1, length + 1), [1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5], label='complete')
    plt.xlabel('nombre de données étudiées')
    plt.ylabel('nombre de clusters')
    plt.legend()
    plt.show()

def monitor_cluster_evolution(funcs):
    labels, vectors = init_data(funcs)
    kwargs = {'n_clusters': None, 'distance_threshold': 5, 'linkage': 'ward'}
    algorithm_manager = AlgorithmManager()
    display_manager = DisplayManager(None, None)
    text, clusters = algorithm_manager.monitor_cluster_evolution(labels, vectors, kwargs)

    print(text)
    print(clusters) 
    _display_cluster_count(clusters)
    display_manager.save_as_file(text, f'monitor-{kwargs["linkage"]}.txt')


if __name__ == '__main__':
    # compare_algorithms(['trier_piles', 'trier_piles_2'], False)
    # compare_distance_threshold(['trier_piles', 'trier_piles_2'])
    # foo()
    # monitor_cluster_evolution(['trier_piles', 'trier_piles_2'])
    _plot_cluster_count()