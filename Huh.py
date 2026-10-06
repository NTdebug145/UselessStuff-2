import os
import sys
import time
import string

# ===== 配置 =====
SCAN_INTERVAL = 5          # 每轮扫描间隔（秒）
LINUX_ROOTS   = ["/"]      # Linux 起始目录，可按需改成 ["/mnt", "/media"] 或 ["/home/user/data"]
LINUX_SKIP    = {"/proc", "/sys", "/dev", "/run", "/snap", "/tmp"}  # Linux 下跳过
# ================


def get_roots():
    """返回本轮要遍历的根目录列表"""
    if sys.platform.startswith("win"):
        # Windows: 枚举所有存在的盘符 (A:\ ~ Z:\)
        roots = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                roots.append(drive)
        return roots
    else:
        # Linux: 使用配置里的起始目录
        return [r for r in LINUX_ROOTS if os.path.exists(r)]


def _should_skip(path):
    """Linux 下判断是否要跳过该目录（避免扫 /proc、/sys 卡死）"""
    if sys.platform.startswith("win"):
        return False
    p = os.path.abspath(path)
    for s in LINUX_SKIP:
        if p == s or p.startswith(s + os.sep):
            return True
    return False


def walk_print(root):
    """递归打印 root 下所有文件夹和子文件夹"""
    # onerror 保证没有权限的目录不会让程序崩溃
    for dirpath, dirnames, _ in os.walk(root, onerror=lambda e: None):
        # 过滤掉要跳过的子目录
        dirnames[:] = [d for d in dirnames
                       if not _should_skip(os.path.join(dirpath, d))]
        if _should_skip(dirpath):
            continue
        try:
            print(dirpath, flush=True)
        except (UnicodeEncodeError, OSError):
            pass  # 某些特殊字符路径无法打印，忽略


def main():
    while True:
        roots = get_roots()
        for root in roots:
            print(f"===== 扫描: {root} =====", flush=True)
            walk_print(root)
        print("===== 一轮扫描结束 =====", flush=True)
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已停止。")