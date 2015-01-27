import os

import vim
import clighter_helper
import clang_service
import highlight
import refactor


if vim.vars['clighter_libclang_file']:
    clang_service.ClangService.set_libclang_file(
        vim.vars['clighter_libclang_file'])

__clang_service = clang_service.ClangService()

# def bfs(c, top, bottom, queue):
# if c.location.line >= top and c.location.line <= bottom:
#__draw_token(c)

# queue.put(c.get_children())

# while not queue.empty():
# curs = queue.get()
# for cur in curs:
# if cur.location.line >= top and cur.location.line <= bottom:
#__draw_token(cur)

# queue.put(cur.get_children())


# def dfs(cursor):
#    print cursor.location, cursor.spelling
#    for c in cursor.get_children():
#        dfs(c)

def clear_symbol_ref():
    highlight.clear_symbol_ref()


def clear_highlight():
    highlight.clear_highlight()


def highlight_window():
    highlight.highlight_window(__clang_service)


def refactor_rename():
    refactor.rename(__clang_service)


def on_FileType():
    if clighter_helper.is_vim_buffer_allowed(vim.current.buffer):
        register_buffer(vim.current.buffer.name)
        __clang_service.switch(vim.current.buffer.name)
    else:
        unregister_buffer(vim.current.buffer.name)
        clear_highlight()


def register_buffer(bufname):
    __clang_service.register([bufname])


def register_allowed_buffers():
    list = []
    for buf in vim.buffers:
        if clighter_helper.is_vim_buffer_allowed(buf):
            list.append(buf.name)

    __clang_service.register(list)


def unregister_buffer(bufname):
    __clang_service.unregister([bufname])


def execfile_with_safe_import(filename, locals_for_file={}):
    import __builtin__
    from types import ModuleType

    class NonExistantModule(ModuleType):
        def __getattr__(self, key):
            return None
        __all__ = [] # support wildcard imports

    def tryimport(name, globals={}, locals={}, fromlist=[], level=-1):
        try:
            return realimport(name, globals, locals, fromlist, level)
        except ImportError:
            return NonExistantModule(name)

    realimport, __builtin__.__import__ = __builtin__.__import__, tryimport

    try:
        execfile(filename, locals_for_file)
    finally:
        __builtin__.__import__ = realimport


def locateYcmExtraConfig():
    currentPath = vim.current.buffer.name
    currentDir = os.path.dirname(currentPath)
    while currentDir != '/':
        if '.ycm_extra_conf.py' in os.listdir(currentDir):
            return os.path.join(currentDir, '.ycm_extra_conf.py')
        currentDir = os.path.abspath(os.path.join(currentDir, os.pardir))
    if '.ycm_extra_conf.py' in os.listdir(currentDir):
        return os.path.join(currentDir, '.ycm_extra_conf.py')
    else:
        if os.path.isfile(os.path.expanduser('~/.ycm_extra_conf.py')):
            return os.path.expanduser('~/.ycm_extra_conf.py')
        else:
            return None

def clang_start_service():
    configlocals = {}
    path_to_ycm_conf = locateYcmExtraConfig()
    if path_to_ycm_conf is not None:
        execfile_with_safe_import(path_to_ycm_conf, configlocals)
        compilation_flags_from_ycm = configlocals['flags']
    else:
        compilation_flags_from_ycm = []
    return __clang_service.start(list(vim.vars["ClighterCompileArgs"])+compilation_flags_from_ycm)


def clang_stop_service():
    return __clang_service.stop()


def clang_set_compile_args(args):
    __clang_service.compile_args = list(args) # list() is need to copy


def clang_switch_to_current():
    __clang_service.switch(vim.current.buffer.name)
    vim.current.window.vars["hl_tick"] = -1


def update_buffer_if_allow():
    if clighter_helper.is_vim_buffer_allowed(vim.current.buffer):
        __clang_service.update_buffers(
            [(vim.current.buffer.name,
              '\n'.join(vim.current.buffer),
              vim.bindeval("b:changedtick"))])
