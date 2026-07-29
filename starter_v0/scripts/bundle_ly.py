import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
dest_dir = Path(r"C:\Users\Admin\Desktop\Phan_Viec_Nguyen_Thi_Ly")
if dest_dir.exists():
    shutil.rmtree(dest_dir)

(dest_dir / "tools" / "weather").mkdir(parents=True, exist_ok=True)
(dest_dir / "artifacts").mkdir(parents=True, exist_ok=True)

shutil.copy2(ROOT / "tools" / "weather" / "TOOL.md", dest_dir / "tools" / "weather" / "TOOL.md")
shutil.copy2(ROOT / "tools" / "weather" / "tool.py", dest_dir / "tools" / "weather" / "tool.py")
shutil.copy2(ROOT / "tools" / "__init__.py", dest_dir / "tools" / "__init__.py")
shutil.copy2(ROOT / "artifacts" / "tools.yaml", dest_dir / "artifacts" / "tools.yaml")

guide = """============================================================
  HƯỚNG DẪN DÁN BÀI & COMMIT GIT - NGUYỄN THỊ LÝ (TOOL DEV)
============================================================

Các tệp công việc của Nguyễn Thị Lý trong thư mục này:
1. tools/weather/TOOL.md         (Tài liệu mô tả tool weather)
2. tools/weather/tool.py         (Code Python thực thi tool weather)
3. tools/__init__.py             (File đăng ký hàm get_weather)
4. artifacts/tools.yaml          (File cấu hình schema YAML tool)

CÁCH THỰC HIỆN:
------------------------------------------------------------
1. Bạn Lý chép các thư mục/tệp này dán đè vào đúng vị trí tương ứng trong repo starter_v0 ở máy của mình.
2. Mở Terminal tại repo và chạy lệnh Git để commit:

   git add tools/weather/ tools/__init__.py artifacts/tools.yaml
   git commit -m "feat: Add custom weather tool by Nguyen Thi Ly (2A202601962)"
   git push origin main

============================================================
"""
(dest_dir / "HUONG_DAN_COMMIT_LY.txt").write_text(guide, encoding="utf-8")

shutil.make_archive(str(dest_dir), "zip", str(dest_dir))
print("BUNDLED_SUCCESSFULLY")
