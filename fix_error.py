"""
错误修复脚本 - 清理缓存并重启应用
"""
import os
import shutil

def clear_cache():
    """清除Python缓存和浏览器缓存建议"""

    print("="*50)
    print("清除缓存并重启应用")
    print("="*50)

    # 清除Python缓存
    cache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dirs.append(os.path.join(root, '__pycache__'))

    if cache_dirs:
        print("\n清除Python缓存...")
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
                print(f"  已删除: {cache_dir}")
            except Exception as e:
                print(f"  删除失败 {cache_dir}: {e}")
    else:
        print("\n没有找到Python缓存文件")

    # 清除.pyc文件
    print("\n查找并清除.pyc文件...")
    pyc_count = 0
    for root, dirs, files in os.walk('./app'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    pyc_count += 1
                    print(f"  已删除: {pyc_path}")
                except Exception as e:
                    print(f"  删除失败 {pyc_path}: {e}")

    if pyc_count == 0:
        print("  没有找到.pyc文件")

    print("\n" + "="*50)
    print("缓存清理完成！")
    print("="*50)

    print("\n下一步操作：")
    print("1. 在浏览器中按 Ctrl+Shift+Delete 清除浏览器缓存")
    print("2. 或者按 Ctrl+F5 硬刷新页面")
    print("3. 重新启动应用：python run.py")

if __name__ == '__main__':
    clear_cache()
