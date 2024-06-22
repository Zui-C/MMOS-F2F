import shutil
import json
import re
import string
import os
import ast
import itertools
from collections import Counter, defaultdict
import difflib
import textwrap
import argparse
import traceback
import matplotlib.pyplot as plt


from tqdm import tqdm


def plot_random_selection_stats(random_selection_stats, output_file):
    # 准备数据
    k_values = list(random_selection_stats.keys())
    counts = list(random_selection_stats.values())

    # 创建折线图
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, counts, marker='o')

    # 添加标题和标签
    plt.title('Random Selection Statistics')
    plt.xlabel('k Value')
    plt.ylabel('Count')

    # 显示网格
    plt.grid(True)

    # 保存图表为文件
    plt.savefig(output_file)

    # 关闭图形，防止内存泄漏
    plt.close()


def count_source_occurrences(args,input_file_path,output_file_path):
    # Initialize a dictionary to count the occurrences of each source value
    source_counts = defaultdict(int)

    # Read the file and count the source values
    with open(input_file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            # source = data['example']['full_name']
            source = data['prompt']
            source_counts[source] += 1

    # 初始化计数器
    k_values = list(range(1, 11)) + [20, 30, 40, 50, 100]
    count_1_10 = {i: 0 for i in k_values}


    # 准备用于计算中位数和平均数的列表
    values_list = []
    # print(source_counts)
    # exit()
    # 遍历字典的值来统计
    for count in source_counts.values():
        # 添加到列表中用于计算中位数和平均数
        values_list.append(count)

        # 统计数量分别大于等于1-10的情况
        for i in k_values:
            if count >= i:
                count_1_10[i] += 1



    # 计算平均数
    average_count = sum(values_list) / len(values_list)

    # 计算中位数
    values_list.sort()
    mid_index = len(values_list) // 2
    median_count = values_list[mid_index] if len(values_list) % 2 != 0 else (values_list[mid_index - 1] + values_list[
        mid_index]) / 2.0

    # 创建统计结果的字符串
    result_strings = [
        "数量大于等于1-10的类别统计：\n" + "\n".join([f"大于等于{i}: {count_1_10[i]}个类别" for i in k_values]),
        f"类别数量的平均数为: {average_count:.2f}",
        f"类别数量的中位数为: {median_count}"
    ]


    # 定义k值范围
    k_values = list(range(1, 51)) + []

    # 添加随机选择预统计功能
    def calculate_random_selection_stats(source_counts, k_values):
        selection_stats = {k: 0 for k in k_values}
        for count in source_counts.values():
            for k in k_values:
                selection_stats[k] += min(count, k)
        return selection_stats

    random_selection_stats = calculate_random_selection_stats(source_counts, k_values)
    random_selection_results = [f"在k值为{k}时，总共可以随机选取的数据数量为: {random_selection_stats[k]}" for k in k_values]

    # 将随机选择预统计结果添加到result_strings
    result_strings.extend(random_selection_results)


    # 输出结果到控制台
    for result in result_strings:
        print(result)

    if args.save:
        # 写入结果到文本文件
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for result in result_strings:
                file.write(result + "\n")

    plot_random_selection_stats(random_selection_stats, base_name + '.jpg')



if __name__ == "__main__":
    input_file_path = '/mnt/pfs_new/zitao_team/chenzui/llemma_formal2formal/tactics/mix3/dedup_samples.jsonl'

    parser = argparse.ArgumentParser(description='state')
    parser.add_argument('--save', action="store_true")
    args = parser.parse_args()
    print(args)


    base_name = os.path.splitext(input_file_path)[0]
    output_file_path = base_name + '_count.txt'


    count_source_occurrences(args,input_file_path,output_file_path)
