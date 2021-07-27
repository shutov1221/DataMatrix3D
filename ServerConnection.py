from smb.SMBConnection import SMBConnection
import os
import shutil
import stat
import make_dm


def _remove_readonly(fn, path_, excinfo):
    # Handle read-only files and directories
    if fn is os.rmdir:
        os.chmod(path_, stat.S_IWRITE)
        os.rmdir(path_)
    elif fn is os.remove:
        os.lchmod(path_, stat.S_IWRITE)
        os.remove(path_)


def force_remove_file_or_symlink(path_):
    try:
        os.remove(path_)
    except OSError:
        os.lchmod(path_, stat.S_IWRITE)
        os.remove(path_)


def is_regular_dir(path_):
    try:
        mode = os.lstat(path_).st_mode
    except os.error:
        mode = 0
    return stat.S_ISDIR(mode)


def clear_dir(path_):
    if is_regular_dir(path_):
        # Given path is a directory, clear its content
        for name in os.listdir(path_):
            fullpath = os.path.join(path_, name)
            if is_regular_dir(fullpath):
                shutil.rmtree(fullpath, onerror=_remove_readonly)
            else:
                force_remove_file_or_symlink(fullpath)
    else:
        # Given path is a file or a symlink.
        # Raise an exception here to avoid accidentally clearing the content
        # of a symbolic linked directory.
        raise OSError("Cannot call clear_dir() on a symbolic link")


def read_connection_settings():

    with open(r'C:\Users\User\AppData\Roaming\AlignerImporter\settings.txt', 'r') as f:
        sttngs = f.read().splitlines()
    return sttngs


class SSConnection(object):

    def __init__(self, user_id, password, client_machine_name, server_name, server_ip):
        self.user_id = user_id
        self.password = password
        self.client_machine_name = client_machine_name
        self.server_name = server_name
        self.server_ip = server_ip

    def connect(self):
        conn = SMBConnection(self.user_id, self.password, self.server_ip, self.server_name, use_ntlm_v2=True)
        conn.connect(self.server_ip, 139)
        return conn


class SSRepository:
    def __init__(self, connect, path, share_folder):
        self.connect = connect
        self.path = path
        self.share_folder = share_folder
        self.files_counter = 0
        self.folder_names = self.get_folder_names('')

    def get_folder_names(self, path_to_repos):
        folder_names = []
        shares = self.connect.listPath(self.path, self.share_folder + '/' + path_to_repos)
        for share in shares:
            folder_names.append(share.filename)
        return folder_names

    def find_case(self, case_name):
        if case_name not in self.folder_names:
            return False
        return True

    def get_case_files(self, case_name):
        case_files = []
        if self.find_case(case_name):
            shares = self.connect.listPath(self.path, self.share_folder + '/' + case_name)
            for share in shares:
                case_files.append(share.filename)
        return case_files

    def get_case_stl_files(self, case_name):
        case_files = []
        if self.find_case(case_name):
            shares = self.connect.listPath(self.path, self.share_folder + '/' + case_name)
            for share in shares:
                file = share.filename
                if '.stl' in file and 'VS_SET' in file and 'TrimmingLine' not in file:
                    case_files.append(share.filename)
        return case_files


class SSReplacer:
    def __init__(self, repository, temp_path):
        self.repository = repository
        self.temp_path = temp_path
        self.file_names = None

    def replace_file(self, case_name):
        if case_name not in self.repository.folder_names:
            print('Кейс ' + case_name + ' не найден!')
            return False

        clear_dir(self.temp_path)
        self.__import_files(case_name)
        self.__connect_dmtrx(case_name)
        self.__export_files(case_name)
        clear_dir(self.temp_path)
        return True

    def __connect_dmtrx(self, case_name):
        for file_name in self.file_names:
            jaw = make_dm.LoadJaw(self.temp_path + '\\' + file_name)
            jawWithDmtrx = make_dm.GetJawWithDmtrx(jaw, self.__get_id(case_name, file_name))
            jawWithDmtrx.export(self.temp_path + '\\' + file_name)

    def __get_id(self, case_name, file_name):
        index = file_name.index('Subsetup')
        index += 8
        id = case_name
        count = index
        symbol = file_name[count]
        while symbol != '_':
            symbol = file_name[count]
            if symbol.isnumeric():
                id += symbol
            count += 1

        if 'Maxillar' in file_name:
            id += 'U'
        else:
            id += 'L'

        return id

    def __import_files(self, case_name):
        self.file_names = self.repository.get_case_stl_files(case_name)
        for file_name in self.file_names:
            self.__import_file(case_name, file_name)

    def __import_file(self, case_name, filename):
        if filename != '' and self.temp_path != '':
            with open(self.temp_path + '\\' + filename, 'wb') as fp:
                self.repository.connect.retrieveFile(self.repository.path,
                                                     self.repository.share_folder + '\\' + case_name + '\\' + filename, fp)

    def __export_files(self, case_name):
        for file_name in self.file_names:
            self.__export_file(case_name, file_name)

    def __export_file(self, case_name, replacement_file):
        if replacement_file != '':
            with open(self.temp_path + '\\' + replacement_file, 'rb') as fp:
                self.repository.connect.storeFile(self.repository.path,
                                                  self.repository.share_folder + '\\' + case_name + '\\' + replacement_file,
                                                  fp)

