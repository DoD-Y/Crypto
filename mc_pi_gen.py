import random
import math
import os
import secrets
import numpy as np

OUTPUT_DIR = "Cryptotest"
RANGE = 10**9
SAMPLE_SIZES = [1000, 10000, 100000, 1000000]


class MonteCarloPiGenerator:

    @staticmethod
    def uniform(size):
        return [random.randint(0, RANGE) for _ in range(size)]

    @staticmethod
    def lcg(size):
        a, c, m = 1103515245, 12345, 2**31
        seed = random.randint(0, m - 1)
        nums = []
        for _ in range(size):
            seed = (a * seed + c) % m
            nums.append(seed % (RANGE + 1))
        return nums

    @staticmethod
    def mersenne_twister(size):
        return list(np.random.randint(0, RANGE + 1, size))

    @staticmethod
    def csprng(size):
        return [secrets.randbelow(RANGE + 1) for _ in range(size)]

    @staticmethod
    def save_data(data, filename):
        with open(filename, "w", newline="") as f:
            for n in data:
                f.write(f"{n}\n")
        actual = os.path.getsize(filename)
        print(f"  -> {filename}  ({len(data)} 个整数, {actual} 字节)")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    generators = {
        "uniform": MonteCarloPiGenerator.uniform,
        "lcg": MonteCarloPiGenerator.lcg,
        "mt": MonteCarloPiGenerator.mersenne_twister,
        "csprng": MonteCarloPiGenerator.csprng,
    }

    print("=" * 55)
    print("  Monte Carlo Pi 随机数生成器")
    print("=" * 55)

    for name, gen_func in generators.items():
        print(f"\n[{name.upper()}]")
        for size in SAMPLE_SIZES:
            filename = os.path.join(OUTPUT_DIR, f"mc_pi_{name}_{size}.txt")
            data = gen_func(size)
            MonteCarloPiGenerator.save_data(data, filename)

    print("\n" + "=" * 55)
    print("  生成完毕！")
    print("  每行一个整数，范围为 0 ~ 10^9")
    print("  使用时两个连续整数组成一个 (x, y) 点")
    print("=" * 55)
