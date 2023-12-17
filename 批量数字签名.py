import os
import configparser
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import tkinter as tk
from tkinter import messagebox

# 设置日志记录
logging.basicConfig(
    filename='signature.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
settings = config['Settings']

# 提取配置信息
cert_path = settings['cert_path']
cert_password = settings['cert_password']
timestamp_url = settings.get('timestamp_url', '')
signing_algorithm = settings['signing_algorithm']
hash_algorithm = settings['hash_algorithm']
root_dir = settings['root_dir']
use_timestamp = settings.getboolean('use_timestamp', True)
file_extensions = tuple(ext.strip() for ext in settings['file_extensions'].split(',') if ext.strip())
thread_count = settings.getint('thread_count', fallback=0)


# 使用signtool进行签名的函数
def sign_file(file_path):
    # 构建signtool签名命令
    command = [
        'signtool', 'sign', '/f', cert_path, '/p', cert_password,
        '/fd', hash_algorithm, '/a', file_path
    ]

    # 如果需要时间戳，添加相关参数
    if use_timestamp and timestamp_url:
        command.extend(['/tr', timestamp_url, '/td', signing_algorithm])

    try:
        logging.info(f"开始对文件进行签名: {file_path}")
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logging.info(f"已成功签名: {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"无法签名 {file_path}: {e}")
        return False
    except Exception as e:
        logging.exception(f"签名时发生意外错误 {file_path}: {e}")
        return False

# 这个函数会为文件夹中的每个特定扩展名的文件调用签名命令
def sign_files_in_directory(directory, extensions):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                yield os.path.join(root, file)

# 用于弹窗提醒的函数
def show_completion_message():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo("完成", "签名已完成")
    root.destroy()

# 创建文件路径列表
files_to_sign = list(sign_files_in_directory(root_dir, file_extensions))

# 设置进度条的格式
bar_format = "{l_bar}{bar}{n_fmt}/{total_fmt} [已用时间:{elapsed}, 剩余时间:{remaining}, 签名速度:{rate_fmt}]"

# 初始化进度条
progress_bar = tqdm(total=len(files_to_sign), desc="签名中，请稍候", unit="file", bar_format=bar_format)

# 记录开始时间
start_time = time.time()

# 使用一个线程池执行签名
with ThreadPoolExecutor(max_workers=None if thread_count == 0 else thread_count) as executor:
    # 提交签名任务到线程池
    futures_to_file = {executor.submit(sign_file, file_path): file_path for file_path in files_to_sign}

    # 处理完成的任务，并更新进度条
    for future in as_completed(futures_to_file):
        _ = futures_to_file[future]
        elapsed = int(time.time() - start_time)
        progress_bar.set_postfix_str(f"总共:{progress_bar.total}")
        progress_bar.update(1)  # 在此处更新进度条

# 关闭进度条
progress_bar.close()

# 所有文件签名完成后，显示完成消息
show_completion_message()