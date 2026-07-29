import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
dest_dir = Path(r"C:\Users\Admin\Desktop\Phan_Viec_Do_Hung_Anh")
if dest_dir.exists():
    shutil.rmtree(dest_dir)

(dest_dir / "data").mkdir(parents=True, exist_ok=True)
(dest_dir / "artifacts").mkdir(parents=True, exist_ok=True)
(dest_dir / "runs").mkdir(parents=True, exist_ok=True)
(dest_dir / "analysis").mkdir(parents=True, exist_ok=True)
(dest_dir / "scripts").mkdir(parents=True, exist_ok=True)
(dest_dir / "providers").mkdir(parents=True, exist_ok=True)

# 1. Copy data/eval_group.json
shutil.copy2(ROOT / "data" / "eval_group.json", dest_dir / "data" / "eval_group.json")

# 2. Copy artifacts/system_prompt.md & artifacts/version_log.csv
shutil.copy2(ROOT / "artifacts" / "system_prompt.md", dest_dir / "artifacts" / "system_prompt.md")
shutil.copy2(ROOT / "artifacts" / "version_log.csv", dest_dir / "artifacts" / "version_log.csv")

# 3. Copy scripts/ (run_eval.py, preflight_provider.py, parse_runs.py)
scripts_dir = ROOT / "scripts"
if scripts_dir.exists():
    for f in scripts_dir.glob("*.py"):
        shutil.copy2(f, dest_dir / "scripts" / f.name)

# 4. Copy providers/ (groq_provider.py, __init__.py...)
providers_dir = ROOT / "providers"
if providers_dir.exists():
    for f in providers_dir.glob("*.py"):
        shutil.copy2(f, dest_dir / "providers" / f.name)

# 5. Copy runs/*.json
runs_dir = ROOT / "runs"
if runs_dir.exists():
    for f in runs_dir.glob("*.json"):
        shutil.copy2(f, dest_dir / "runs" / f.name)

# 6. Copy analysis/base_runs.csv
analysis_file = ROOT / "analysis" / "base_runs.csv"
if analysis_file.exists():
    shutil.copy2(analysis_file, dest_dir / "analysis" / "base_runs.csv")

guide = """============================================================
  HƯỚNG DẪN DÁN BÀI & COMMIT GIT - ĐỖ HÙNG ANH (EVAL & BENCHMARK)
============================================================

Các tệp công việc & Code Script của Đỗ Hùng Anh trong thư mục này:
1. data/eval_group.json         (10 test cases benchmark do nhóm tự thiết kế)
2. artifacts/system_prompt.md   (System Instruction tối ưu qua các phiên bản)
3. artifacts/version_log.csv    (Nhật ký tiến trình tối ưu phiên bản v0->v3)
4. scripts/                     (Code Python chạy benchmark: run_eval.py, preflight_provider.py, parse_runs.py)
5. providers/                   (Code Python các LLM Providers: groq_provider.py...)
6. runs/*.json                  (Các file bằng chứng run log benchmark)
7. analysis/base_runs.csv       (Bảng phân tích CSV kết quả benchmark)

CÁCH THỰC HIỆN:
------------------------------------------------------------
1. Bạn Hùng Anh chép các thư mục/tệp này dán đè vào đúng vị trí tương ứng trong repo starter_v0 ở máy của mình.
2. Mở Terminal tại repo và chạy lệnh Git để commit:

   git add data/eval_group.json artifacts/system_prompt.md artifacts/version_log.csv scripts/ providers/ runs/ analysis/
   git commit -m "feat: Add group eval suite, prompt optimization, and benchmark evaluation scripts by Do Hung Anh (2A202601175)"
   git push origin main

============================================================
"""
(dest_dir / "HUONG_DAN_COMMIT_HUNG_ANH.txt").write_text(guide, encoding="utf-8")

shutil.make_archive(str(dest_dir), "zip", str(dest_dir))
print("BUNDLED_HUNG_ANH_WITH_CODE_SUCCESSFULLY")
