import os
import subprocess
import shutil
import sys
# 🎯 确保导入了 Form
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse

try:
    from config import NIST_DIR, NIST_DIR_WIN, NIST_DIR_WSL
except ImportError:
    NIST_DIR = NIST_DIR_WIN = NIST_DIR_WSL = ""

app = FastAPI(title="NIST 随机性在线评估平台")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>前端模板 templates/index.html 未找到！</h1>"

@app.post("/api/test-randomness/")
async def test_randomness(
    file: UploadFile = File(...),
    # 🎯 动态接收前端传递的参数
    bitstreams: int = Form(1),      # 默认序列数为 1
    test_mode: str = Form("1"),     # 默认运行所有测试
    selected_tests: str = Form("")  # 自定义测试时选中的测试编号（逗号分隔）
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    temp_file_name = "uploaded_temp_data.txt"
    is_windows = sys.platform == "win32"

    if is_windows:
        nist_dir = NIST_DIR_WIN
        temp_file_path = os.path.join(NIST_DIR_WIN, temp_file_name)
        report_path = os.path.join(NIST_DIR_WIN, "experiments", "AlgorithmTesting", "finalAnalysisReport.txt")
    else:
        nist_dir = NIST_DIR
        temp_file_path = os.path.join(NIST_DIR, temp_file_name)
        report_path = os.path.join(NIST_DIR, "experiments", "AlgorithmTesting", "finalAnalysisReport.txt")

    # 1. 清理旧报告
    if os.path.exists(report_path):
        try:
            os.remove(report_path)
        except Exception as cleanup_err:
            print(f"[WARNING] 清理旧报告失败: {cleanup_err}")

    try:
        if not os.path.exists(nist_dir):
            raise HTTPException(
                status_code=500,
                detail=f"无法访问 NIST 目录: {nist_dir}，请检查配置。"
            )

        # 2. 写入临时文件
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. 统计文件总比特数
        with open(temp_file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        total_bit_size = content.count('0') + content.count('1')

        if total_bit_size == 0:
            raise HTTPException(status_code=400, detail="上传的文件中未检测到有效的 0/1 比特字符！")

        # 4. 根据前端传递的序列数，动态计算单序列分配的比特长度
        bit_size_per_stream = total_bit_size // bitstreams

        if bit_size_per_stream == 0:
            raise HTTPException(
                status_code=400,
                detail=f"文件比特数不足！当前文件包含 {total_bit_size} 个比特，无法分为 {bitstreams} 个序列。"
            )

        # 5. 构造交互输入
        if test_mode == "0" and selected_tests.strip():
            selected = set(int(n.strip()) for n in selected_tests.split(",") if n.strip().isdigit())
            binary_flags = "\n".join("1" if i in selected else "0" for i in range(1, 16))
            param_tests = {2, 8, 9, 11, 14, 15}
            has_params = bool(selected & param_tests)
            if has_params:
                interactive_inputs = f"0\n{temp_file_name}\n0\n{binary_flags}\n0\n{bitstreams}\n0\n"
            else:
                interactive_inputs = f"0\n{temp_file_name}\n0\n{binary_flags}\n{bitstreams}\n0\n"
        else:
            interactive_inputs = f"0\n{temp_file_name}\n{test_mode}\n0\n{bitstreams}\n0\n"

        # 6. 构造启动命令
        if is_windows:
            cmd_args = ["wsl", "--cd", NIST_DIR_WSL, "./assess", str(bit_size_per_stream)]
        else:
            cmd_args = [os.path.join(NIST_DIR, "assess"), str(bit_size_per_stream)]

        print(f"[RUNNING] 单序列比特: {bit_size_per_stream} | 序列总数: {bitstreams}")
        print(f"   交互流: {repr(interactive_inputs)}")

        process = subprocess.run(
            cmd_args,
            input=interactive_inputs,
            text=True,
            capture_output=True,
            timeout=30
        )

        # 7. 检测并读取报告
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
                report_content = f.read()
            print("[SUCCESS] NIST 评估已成功完成。")
            return {
                "status": "success",
                "filename": file.filename,
                "bit_size": bit_size_per_stream,
                "sequence_count": bitstreams,
                "report": report_content
            }
        else:
            print("[FAIL] NIST 未生成 finalAnalysisReport.txt。")
            debug_report = (
                "⚠️【NIST 运行完毕，但未生成 finalAnalysisReport.txt】\n"
                "请检查文件长度是否满足测试要求。以下为运行日志：\n"
                "--------------------------------------------------\n"
                f"【标准输出 (STDOUT)】:\n{process.stdout}\n"
                f"【错误输出 (STDERR)】:\n{process.stderr}"
            )
            return {
                "status": "success",
                "filename": file.filename,
                "bit_size": bit_size_per_stream,
                "sequence_count": bitstreams,
                "report": debug_report
            }

    except subprocess.TimeoutExpired as te:
        timeout_report = (
            "⚠️【系统提示：NIST 运行超时（30秒）】\n"
            f"部分输出内容如下:\n{te.stdout if te.stdout else '无输出'}"
        )
        return {
            "status": "success",
            "filename": file.filename,
            "bit_size": total_bit_size,
            "sequence_count": bitstreams,
            "report": timeout_report
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return {"status": "error", "message": f"执行评估出错: {str(e)}"}

    finally:
        # 清理临时上传文件
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"[CLEANUP] 临时文件已安全删除: {temp_file_path}")
            except Exception as cleanup_err:
                print(f"[WARNING] 无法清理临时文件: {cleanup_err}")
