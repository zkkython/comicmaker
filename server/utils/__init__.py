# utils 包初始化文件
# 重新导出 server/utils.py 中的函数，以保持向后兼容

import sys
import os

# 获取 server 目录路径
server_dir = os.path.dirname(os.path.dirname(__file__))
utils_py_path = os.path.join(server_dir, "utils.py")

# 导入 utils.py 模块
if os.path.exists(utils_py_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("utils_module", utils_py_path)
    utils_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_module)
    
    # 重新导出所有函数和变量
    __all__ = [
        'DATA_ROOT',
        'ensure_dir',
        'get_data_path',
        'load_json',
        'save_json',
        'generate_id',
        'list_dirs',
        'delete_dir'
    ]
    
    # 导出所有公共函数和变量
    DATA_ROOT = utils_module.DATA_ROOT
    ensure_dir = utils_module.ensure_dir
    get_data_path = utils_module.get_data_path
    load_json = utils_module.load_json
    save_json = utils_module.save_json
    generate_id = utils_module.generate_id
    list_dirs = utils_module.list_dirs
    delete_dir = utils_module.delete_dir
