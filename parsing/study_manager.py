from pycparser.c_parser import CParser

from parsing.file_manager import FileManager
from parsing.ast_visitor import ASTVisitor as Visitor


class FileOutput:
    def __init__(self, filename, funcs_outputs):
        self.filename = filename
        self.funcs_outputs = funcs_outputs
    
    def set_filename(self):
        for func_output in self.funcs_outputs:
            func_output.filename = self.filename
    
    def get_result_from_names(self, names):
        filter_func = lambda func_output: func_output.name in names
        return list(filter(filter_func, self.funcs_outputs))

    def _get_funcs_name(self):
        return [func.name for func in self.funcs_outputs]

    def __str__(self):
        return f'filename: {self.filename}, funcs:{self._get_funcs_name()}'
    
    def __repr__(self):
        return f'filename: {self.filename}, funcs:{self._get_funcs_name()}'


class StudyManager:
    def __init__(self):
        self.visitor = Visitor()
        self.file_manager = FileManager()

    def _parse(self, text):
        parser = CParser()
        ast = parser.parse(text) 

        return ast

    def parse_and_visit(self, text,  visitor=None):
        if visitor is None:
            visitor = self.visitor

        ast = self._parse(text)
        return visitor.visit(ast)
    
    def get_files_output(self):
        content, names = self.file_manager.load_directory()
        results = [self.parse_and_visit(file) for file in content]
        zipped_list = self._zip_results_names(results, names)

        result = []
        for tuple_ in zipped_list:
            file_output = FileOutput(*tuple_)
            file_output.set_filename()
            result.append(file_output)

        return result
    
    def select_from_names(self, names):
        files_output = self.get_files_output()
        filtered_outputs = [output.get_result_from_names(
            names) for output in files_output]

        print(filtered_outputs[0])
        return filtered_outputs 
    
    def _zip_results_names(self, results, names):
        return list(zip(names, results))
    
    @classmethod
    def filter_non_empty_list(cls, lists):
        filtering_func = lambda list_: not list_ == []
        return list(filter(filtering_func, lists))
        
    @classmethod
    def merge_lists(cls, lists):
        return [content for list_ in lists for content in list_]
    
    @classmethod
    def extract_vectors(self, func_output_list):
        return [func_output.extract_vector() for func_output in func_output_list]