#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 10            // 随机数范围 [0, N-1]
#define SAMPLE_SIZE 1000 // 生成的样本数量
#define FILE_NAME "Cryptotest/data_c_rand_mod100.txt"

int main() {
    // 1. 使用当前系统时间初始化随机数发生器种子
    // 在实际生产中，如果需要密码学安全，绝不能使用 time(NULL) 作为唯一熵源
    srand((unsigned int)time(NULL));

    printf("====================================================\n");
    printf("  C 语言 rand() %% N 随机数生成器\n");
    printf("====================================================\n");
    printf("  数值范围  : 0 ~ %d\n", N - 1);
    printf("  生成样本数: %d\n", SAMPLE_SIZE);
    printf("  输出目标  : 控制台 & 文件 (%s)\n", FILE_NAME);
    printf("====================================================\n\n");

    // 打开文件准备写入（使用 "w" 模式，在 Windows 下建议配合特定处理防 CRLF，这里在 Linux/WSL 下天然为 LF）
    FILE *fp = fopen(FILE_NAME, "w");
    if (fp == NULL) {
        printf("❌ 无法打开或创建文件: %s\n", FILE_NAME);
        printf("💡 请确保 Cryptotest 目录已存在，或手动创建该目录。\n");
        return 1;
    }

    printf("🎲 开始生成并在屏幕打印:\n");
    for (int i = 0; i < SAMPLE_SIZE; i++) {
        // 🎯 核心方法：取模运算限制范围在 0 到 N-1 之间
        int x = rand() % N;

        // 打印到控制台
        printf("%d ", x);

        // 写入到文件，强制使用 '\n' (LF) 换行，与 Python 数据生成器规范对齐
        fprintf(fp, "%d\n", x);
    }
    printf("\n\n");

    // 关闭文件流
    fclose(fp);

    printf("💾 [成功] 原始数据已安全保存至: %s\n", FILE_NAME);
    printf("====================================================\n");

    return 0;
}
