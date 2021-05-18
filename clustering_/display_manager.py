import os
import datetime


class SummaryElement:
    def __init__(self, data, title=None, used_kwargs=None):
        self.data = data # tuple(str, str) -> tuple(labels, clusters_id)
        self.title = title = title or ''
        self.used_kwargs = used_kwargs or ''
    
    def get_labels(self):
        return self.data[0]

    def get_clusters(self):
        return self.data[1]


class SummaryBuilder:
    DELIMITER = '+-----------------------+--------+' 

    def __init__(self):
        self.strings = []
    
    def with_title(self, title):
        self.strings.append(title)

        return self
    
    def with_kwargs(self, used_kwargs):
        self.strings.append(str(used_kwargs))

        return self
    
    def with_data(self, labels, clusters_id):
        strings = []

        strings.append(SummaryBuilder.DELIMITER)
        strings.append('|Label                  |Cluster |')
        strings.append(SummaryBuilder.DELIMITER)
        
        for label, cluster_id in zip(labels, clusters_id):
            # TODO DELETE
            label = (label[0][-5:], label[1])
            combined_label = self._join(' ', label)[:20]

            label_string = self._get_spaced_string(23, combined_label)
            id_string = self._get_spaced_string(8, cluster_id)

            strings.append(f'|{label_string}|{id_string}|')

        strings.append(SummaryBuilder.DELIMITER)
    
        self.strings.append(self._join('\n', strings)) 

        return self
    
    def from_summary_element(self, element):
        self.with_title(element.title) \
            .with_kwargs(element.used_kwargs) \
            .with_data(*element.data) 

        return self
    
    def build(self):
        return self._join('\n', self.strings)
    
    def _join(self, char, data):
        return f'{char}'.join(data)
    
    def _get_space_count(self, max_val, element):
        space_count = max_val - len(str(element))
        return space_count if space_count < max_val and space_count >= 0 else max_val
    
    def _get_spaced_string(self, max_val, element):
        space_count = self._get_space_count(max_val, element)
        return f'{element}{" " * space_count}'


class DisplayManager:
    PATH = 'clustering_/results/'

    # TODO delete parameters
    def __init__(self, clusters_id, labels):
        self.clusters_id = clusters_id
        self.labels = labels
        self.zipped_data = list()

        self.summary_builder = SummaryBuilder()
    
    def build_summary(self, summary_elements):
        summary_builder = SummaryBuilder()
        
        for summary_element in summary_elements:
            summary_builder.from_summary_element(summary_element)
        
        return summary_builder.build()
    
    def to_summary_element(self, data, title=None, used_kwargs=None):
        return SummaryElement(data, title, used_kwargs)
    
    def save_as_file(self, text, filename=None):
        if filename is None:
            filename = f'result-{self._get_date_as_string()}.txt'

        self._assert_result_folder_exists()
        with open(os.path.join(DisplayManager.PATH, filename), 'w') as file:
            file.write(text)
        
    def _get_date_as_string(self):
        date = datetime.datetime.now()
        return f'{date.day}_{date.month}_{date.year}-{date.hour}_{date.minute}'
        
    def _get_data_one_by_one(self):
        for label, cluster_id in zip(self.labels, self.clusters_id):
            yield label[:10], cluster_id
    
    def _assert_result_folder_exists(self):
        if not os.path.exists(DisplayManager.PATH):
            os.mkdir(DisplayManager.PATH)