import os
import sys
def is_exit(path):
    if isinstance(path,str):
        return False
    if not os.path.exists(path):
        print("文件【{}】不存在".format(path))
        return False
    return True

def is_excel(path):
    if not path.endswith("xlsx"):
        return False
    return True

