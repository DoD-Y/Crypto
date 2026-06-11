import random
import math
import os
import numpy as np

class RandomDataGenerator:
    """随机数数据生成器"""

    @staticmethod
    def uniform_distribution(n, size=10000):
        """均匀分布随机数（理论标准）"""
        return [int(random.random() * n) for _ in range(size)]

    @staticmethod
    def normal_distribution(n, size=10000):
        """正态分布随机数（截断正态，拒绝采样）"""
        mu = n / 2
        sigma = n / 6
        nums = []
        while len(nums) < size:
            u1, u2 = random.random(), random.random()
            while u1 == 0:
                u1 = random.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            val = int(mu + sigma * z)
            if 0 <= val < n:
                nums.append(val)
        return nums

    @staticmethod
    def linear_congruential(n, size=10000):
        """线性同余法生成随机数"""
        a = 1103515245
        c = 12345
        m = 2**31
        seed = random.randint(0, m-1)
        nums = []
        for _ in range(size):
            seed = (a * seed + c) % m
            nums.append(seed % n)
        return nums

    @staticmethod
    def mersenne_twister(n, size=10000):
        """Mersenne Twister 算法（使用numpy）"""
        return list(np.random.randint(0, n, size))

    @staticmethod
    def cryptographically_secure(n, size=10000):
        """密码学安全随机数 (CSPRNG)"""
        import secrets
        return [secrets.randbelow(n) for _ in range(size)]

    @staticmethod
    def binary_random(size=10000):
        """
        生成原始二进制随机数 (0/1)
        使用 os.urandom() 作为熵源，质量优于 random.randint
        """
        import secrets
        return [secrets.randbits(1) for _ in range(size)]

    # 🎯 核心逻辑：用真实的二进制位展开算法替代原来的中位数二值化
    @staticmethod
    def convert_to_binary(data, n):
        """
        将整数序列转换为二进制序列（按位展开）。
        对于范围为 0 ~ N-1 的数据，每个数用 ceil(log2(N)) 位固定宽度的二进制表示。
        例如：当 N = 10 时，每个数展开为 4 比特 (3 -> [0, 0, 1, 1])。
        """
        if n <= 1:
            bit_width = 1
        else:
            bit_width = math.ceil(math.log2(n))
        
        bits = []
        for x in data:
            # 限制数值在 [0, n-1] 安全范围内
            val = max(0, min(n - 1, int(x)))
            # 使用高位在前的位操作依次提取比特
            for i in range(bit_width - 1, -1, -1):
                bits.append((val >> i) & 1)
        return bits

    @staticmethod
    def save_raw_file(data, filename):
        """
        保存原始整数数据到文件（每行一个整数）。
        强制使用 LF 换行符，避免 Windows CRLF 污染。
        """
        with open(filename, 'w', newline='') as f:
            f.write('\n'.join(str(x) for x in data))
        print(f"  -> 已保存原始数据: {filename} ({len(data)} 个样本)")

    @staticmethod
    def save_nist_file(data, filename, required_size):
        """
        保存用于 NIST STS 测试的二进制文件。
        """
        # 截断或校验长度，确保精确等于 required_size 个比特
        bits = data[:required_size]

        if len(bits) < required_size:
            # 如果由于边界计算意外导致数据不足，用密码学安全随机比特补齐
            import secrets
            padding = [secrets.randbits(1) for _ in range(required_size - len(bits))]
            bits = bits + padding
            print(f"  [警告] 数据不足，已用 CSPRNG 补齐至 {required_size} 比特")

        # 拼成一个纯字符串，无任何空格/换行符
        bit_string = ''.join(str(b) for b in bits)

        # newline='' 是关键：禁止 Python 将 \n 转换为 \r\n
        with open(filename, 'w', newline='') as f:
            f.write(bit_string)

        # 最终验证：检查磁盘上的实际字节数
        actual_size = os.path.getsize(filename)
        status = "OK" if actual_size == required_size else f"WARN (实际{actual_size}字节)"
        print(f"  -> 已保存NIST数据: {filename} | {actual_size} 字节 [{status}]")


# ============================================================
#  主程序入口
# ============================================================

if __name__ == "__main__":

    # ---- 参数配置区 ----
    N           = 16       # 原始数值范围 0 ~ N-1
    SAMPLE_SIZE = 1000000   # NIST 测试所需的精确比特数
    OUTPUT_DIR  = "Cryptotest"  # 输出目录
    # --------------------

    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 计算表示单个数所需的固定二进制位宽
    bit_width = math.ceil(math.log2(N)) if N > 1 else 1
    
    # 根据位宽计算，非 binary 算法需要生成的原始整数数量
    raw_size_needed = math.ceil(SAMPLE_SIZE / bit_width)

    generator = RandomDataGenerator()

    print("=" * 60)
    print("  随机数数据生成器 - NIST STS 标准数据准备（按位展开版）")
    print("=" * 60)
    print(f"  数值范围  : 0 ~ {N-1}")
    print(f"  每数占比特: {bit_width} bits")
    print(f"  NIST比特数: {SAMPLE_SIZE}")
    print(f"  输出目录  : {OUTPUT_DIR}/")
    print("=" * 60)

    # 定义剩余的 6 种算法（去掉了 rand_mod）
    algorithms = {
        "uniform"  : lambda: generator.uniform_distribution(N, raw_size_needed),
        "normal"   : lambda: generator.normal_distribution(N, raw_size_needed),
        "lcg"      : lambda: generator.linear_congruential(N, raw_size_needed),
        "mt"       : lambda: generator.mersenne_twister(N, raw_size_needed),
        "csprng"   : lambda: generator.cryptographically_secure(N, raw_size_needed),
        "binary"   : lambda: generator.binary_random(SAMPLE_SIZE), # 纯 0/1 无需缩放
    }

    stats_data = {}

    print(f"\n开始生成数据文件... (非Binary算法将生成 {raw_size_needed} 个原始整数)\n" + "-" * 60)

    for name, generate_func in algorithms.items():
        print(f"\n[算法: {name.upper()}]")

        # 1. 生成原始数据
        raw_data = generate_func()

        # 2. 保存原始整数文件
        raw_path = os.path.join(OUTPUT_DIR, f"data_{name}.txt")
        generator.save_raw_file(raw_data, raw_path)

        # 3. 转换为 NIST 二进制序列
        if name == "binary":
            nist_data = raw_data
        else:
            nist_data = generator.convert_to_binary(raw_data, N)

        # 4. 保存 NIST 标准格式文件（单行、纯 LF、精确长度）
        nist_path = os.path.join(OUTPUT_DIR, f"nist_{name}.txt")
        generator.save_nist_file(nist_data, nist_path, SAMPLE_SIZE)

        stats_data[name] = {"raw": raw_data, "nist": nist_data}

    # ============================================================
    #  统计摘要
    # ============================================================
    print("\n" + "=" * 60)
    print("  数据统计摘要")
    print("=" * 60)

    for name, d in stats_data.items():
        raw  = d["raw"]
        nist = d["nist"][:SAMPLE_SIZE]  # 截取精确的样本大小进行统计评估
        ones  = sum(nist)
        zeros = len(nist) - ones
        balance = abs(50.0 - ones / len(nist) * 100)

        print(f"\n  算法: {name.upper()}")
        if name != "binary":
            print(f"    原始数据  | 均值: {np.mean(raw):.4f}  "
                  f"标准差: {np.std(raw):.4f}  "
                  f"范围: [{min(raw)}, {max(raw)}]")
        print(f"    NIST比特  | 0: {zeros/len(nist)*100:.2f}%  "
              f"1: {ones/len(nist)*100:.2f}%  "
              f"偏差: {balance:.2f}%  "
              f"{'[理想]' if balance < 1.0 else '[可接受]' if balance < 5.0 else '[偏差较大]'}")

    print("\n" + "=" * 60)
    print("  所有文件生成完毕！")
    print(f"  NIST 测试时请使用: {OUTPUT_DIR}/nist_<算法名>.txt")
    print(f"  启动命令示例: ./assess {SAMPLE_SIZE}")
    print("=" * 60)
