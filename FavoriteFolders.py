import sublime
import sublime_plugin
import os
import shutil

def remove_first_slash(path):
    path_first_chr = path[0]
    return (path , path[1:])[path_first_chr=="/"]

def collect_folders(files, path, search_path):
    paths = {}

    def collect_current_folder():
        current_folder_relative = path.replace(search_path, '')
        current_folder_relative = (current_folder_relative, 'root')[len(current_folder_relative)==0]
        paths[remove_first_slash(current_folder_relative)] = path

    def collect_files_with_path():
        for file in files:
            absolute_path = os.path.join(path,file)
            relative_path = absolute_path.replace(search_path, '')
            paths[remove_first_slash(relative_path)] = absolute_path

    collect_current_folder()
    collect_files_with_path()
    return paths

def walk(search_path):
    paths = dict()
    for path, dirs, files in os.walk(search_path):
        paths = dict(paths.items() + collect_folders(files, path, search_path).items())
    return paths

plugin_settings = sublime.load_settings('FavoriteFolders.sublime-settings')

class FavoriteFoldersCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.view = sublime.active_window().active_view()
        self.project_settings = self.view.settings().get('FavoriteFolders', {})
        self.show_favorites_folders()

    def get_setting(self,name):
        value = self.project_settings.get(name)
        return (plugin_settings.get(name), value)[value != None]

    def get_bookmarked_folders(self):
        return self.get_setting("folders")

    def show_favorites_folders(self):
        bookmarked_folders = self.get_bookmarked_folders()
        options = []
        for folder in bookmarked_folders:
            options.append([folder[1], folder[2]])

        def take_action(index):
            self.show_folder_contents_list(bookmarked_folders[index][0])

        self.window.show_quick_panel(options, take_action, sublime.MONOSPACE_FONT)

    def show_folder_contents_list(self, abs_folder_path):
        dir_paths = []
        paths = walk(abs_folder_path)

        for t, path in paths.items():
            dir_paths.insert(0, [t])

        dir_paths = sorted(dir_paths)

        def resolve_action(index):
            relative_path = dir_paths[index][0]
            absolute_path = paths[relative_path]
            self.show_options(absolute_path, relative_path, abs_folder_path)

        self.window.show_quick_panel(dir_paths, resolve_action, sublime.MONOSPACE_FONT)

    def show_options(self, absolute_path, relative_path, origin_path):
        options = []

        is_dir = os.path.isdir(absolute_path)

        if is_dir:
            options.append(['* New File    | '+relative_path])
            options.append(['* New Folder  | '+relative_path])
        else:
            options.append(['* Open        | '+relative_path])
        
        options.append(['* Delete      | '+relative_path])
        options.append(['* Rename/Move | '+relative_path])
        options.append(['* Back to List'])

        def take_action(index):
            file_operation = FileOperation(self, absolute_path, relative_path)
            if is_dir:
                if (index == 0):
                    file_operation.new_file()
                elif (index == 1):
                    file_operation.new_dir()
                elif (index == 2):
                    file_operation.delete()
                elif (index == 3):
                    file_operation.rename()
                elif (index == 4):
                    self.show_folder_contents_list(origin_path)
            else:
                if (index == 0):
                    self.window.open_file(absolute_path)
                elif (index == 1):
                    file_operation.delete()
                elif (index == 2):
                    file_operation.rename()
                elif (index == 3):
                    self.show_folder_contents_list(origin_path)

        self.window.show_quick_panel(
            options,
            take_action,
            sublime.MONOSPACE_FONT
        )

class FileOperation:
    def __init__(self, sublime_obj, absolute_path, favorite_relative_path):
        self.sublime_obj = sublime_obj
        self.absolute_path = absolute_path
        self.favorite_relative_path = favorite_relative_path

    def get_relative_path(self):
        path = self.favorite_relative_path
        return (path+"/", "")[path=="root"]

    def new_file(self):
        def new_file_action(file_name):
            full_path = os.path.join(self.absolute_path, file_name)

            if os.path.lexists(full_path):
                sublime.error_message('File already exists:\n%s' % full_path)
                return
            else:
                open(full_path, 'w')
                self.sublime_obj.window.open_file(full_path)

        self.sublime_obj.window.show_input_panel(
            '<Sprint Tema>/'+self.get_relative_path(),
            '', new_file_action, None, None
        )

    def delete(self):
        if os.path.isdir(self.absolute_path):
            shutil.rmtree(self.absolute_path)
            sublime.status_message("Folder deleted")
        else:
            os.remove(self.absolute_path)
            sublime.status_message("File deleted")

    def rename(self):
        def rename_file_action(old_filename, new_filename):
            sublime.status_message("File renamed to %s" % (new_filename))
            shutil.move(old_filename, new_filename)

        self.sublime_obj.window.show_input_panel(
            "Rename:",
            self.absolute_path,
            lambda user_input: rename_file_action(self.absolute_path, user_input), 
            None, None
        )

    def new_dir(self):
        def new_dir_action(file_name): 
            full_path = os.path.join(self.absolute_path, file_name)

            if os.path.lexists(full_path):
                sublime.error_message('Directory already exists:\n%s' % full_path)
                return
            else:
                os.mkdir(full_path)

        self.sublime_obj.window.show_input_panel(
            "New directory name:",
            '',
            new_dir_action,
            None, None
        )