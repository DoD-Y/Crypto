# frequency_stats.py - 统计每个数值出现的频率

def count_frequency(filepath, N):
    """
    统计文件中每个数值出现的频率
    
    参数:
        filepath: 数据文件路径（每行一个整数）
        N: 数值范围 0 到 N-1
    """
    
    # 初始化计数器
    freq = [0] * N
    total = 0
    
    # 读取文件并统计
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and line.lstrip('-').isdigit():
                val = int(line)
                if 0 <= val < N:
                    freq[val] += 1
                    total += 1
    
    # 打印结果
    print(f"\n文件: {filepath}")
    print(f"数值范围: 0 ~ {N-1}")
    print(f"总样本数: {total}\n")
    print(f"{'数值':>6} | {'频次':>10} | {'百分比':>10} | {'柱状图'}")
    print("-" * 50)
    
    for i in range(N):
        percent = (freq[i] / total * 100) if total > 0 else 0
        bar_length = int(percent / 2)  # 每个百分比占2个字符
        bar = "█" * bar_length
        
        print(f"{i:>6} | {freq[i]:>10,} | {percent:>9.2f}% | {bar}")
    
    print("-" * 50)
    print(f"{'合计':>6} | {total:>10,} | {'100.00%':>10}")
    
    return freq


# ========== 使用示例 ==========
if __name__ == "__main__":
    # 修改为您的文件路径和数值范围 N
    FILE_PATH = "Cryptotest/data_c_rand_mod100000.txt"  
    N = 32  # 数值范围 0-9
    
    freq = count_frequency(FILE_PATH, N)
