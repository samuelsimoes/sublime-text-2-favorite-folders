import sublime
import sublime_plugin
import os
import re
import shutil

ROOT_NAME = 'Root Folder'
plugin_settings = sublime.load_settings("favorite_folders.sublime-settings").get("settings")

def remove_first_slash(path):
    if len(path)==0: return path
    path_first_chr = path[0]
    return (path, path[1:])[path_first_chr=="/"]

def walk(search_path, excluded_dir_patterns):
    excluded = re.compile(excluded_dir_patterns)
    paths = {}

    def collect():
        for root, dirs, files in os.walk(search_path):
            if excluded.search(root) == None:
                relative_path = remove_first_slash(root.replace(search_path, ''))
                relative_path = (relative_path, ROOT_NAME)[len(relative_path)==0]
                paths[relative_path] = root
                collect_files(files, root)
        return paths

    def collect_files(files, root):
        for file in files:
            if excluded.search(file) == None:
                file_path = os.path.join(root, file)
                file_path_relative = remove_first_slash(file_path.replace(search_path, ''))
                paths[file_path_relative] = file_path

    return collect()

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
            bookmark_title = folder[1] if (len(folder)>=2) else folder[0]
            bookmark_desc = folder[2] if (len(folder)>=3) else ''
            options.append([bookmark_title, bookmark_desc])

        def take_action(index):
            if (index==-1):
                return
            self.show_folder_contents_list(bookmarked_folders[index][0])

        self.window.show_quick_panel(options, take_action, sublime.MONOSPACE_FONT)

    def show_folder_contents_list(self, abs_folder_path):
        dir_paths = []
        paths = walk(abs_folder_path, self.get_setting('excluded_dir_patterns'))

        for t, path in paths.items():
            dir_paths.insert(0, [t])

        dir_paths = sorted(dir_paths)

        def resolve_action(index):
            if (index==-1):
                return
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
            if (index==-1):
                return
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