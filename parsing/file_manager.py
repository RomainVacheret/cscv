import os


class FileManager:
    PATH = './resources/files'
    
    def read_file(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        text = '\n'.join(self._exclude_headers(lines))
        return text

    def load_directory(self, path=None):
        if path is None:
            path = FileManager.PATH

        c_files = self._list_files(path)

        files_content, files_name = [], []
        for filename in c_files:
            file_content = self.read_file(FileManager.get_full_path(filename))
            file_name = filename

            files_content.append(file_content)
            files_name.append(file_name)

        return files_content, files_name

    def _exclude_headers(self, lines):
        return list(filter(lambda line: not line.startswith('#'), lines))
    
    def _assert_directory_exists(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError
        
    def _is_c_file(self, file):
        return file and file.split('.')[-1] == 'c'
        
    def _list_files(self, filename, path=None):
        if path is None:
            path = FileManager.PATH

        self._assert_directory_exists(path)

        with os.scandir(path) as dir_content:
            files = [entry.name for entry in dir_content] 
            c_files = filter(self._is_c_file, files)
        
        return list(c_files)

    @classmethod
    def set_default_path(cls, path):
        cls.PATH = path
    
    @classmethod
    def get_full_path(cls, filename):
        return os.path.join(cls.PATH, filename)