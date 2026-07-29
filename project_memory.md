# Project Memory — Research Agent Tool Eval (Day 04 Lab v2)

## 📌 Tổng quan dự án & Trạng thái Hoàn thành
Dự án đã **HOÀN THÀNH 100%** toàn bộ các yêu cầu của bài Lab Day 04 v2.
Xây dựng thành công **Research Agent** trên provider **Groq (`llama-3.1-8b-instant`)**, thiết lập quy trình tối ưu dựa trên bằng chứng (evidence-driven), lập trình tool mới, thiết kế 10 eval cases và xây dựng giao diện Web Streamlit.

## 👥 Danh sách Thành viên & Phân công
- **Nguyễn Tuấn Anh (2A202601669 - Group Leader)**: Giao diện Web UI Streamlit (`app.py`), Tích hợp hệ thống, Báo cáo & Demo Rehearsal.
- **Nguyễn Thị Lý (2A202601962)**: Lập trình Tool mới (`weather`), Viết `TOOL.md` và Smoke-test công cụ.
- **Đỗ Hùng Anh (2A202601175)**: Thiết kế 10 Benchmark Team Eval Cases (`data/eval_group.json`), Tối ưu hóa Prompt & Tools Declaration (`v0` -> `v3`), Chạy `run_eval.py` & Log `version_log.csv`.

## 🛠️ Stack công nghệ & Cấu hình
- **Ngôn ngữ**: Python 3.10+
- **Model Provider**: Groq (`llama-3.1-8b-instant`), OpenRouter, OpenAI, Gemini
- **Tooling**:
  - `lookup` (Tavily Search)
  - `fetch` (Firecrawl Web Scraper)
  - `timeline` & `social_search` (RapidAPI Twitter API45)
  - `clarify` (Hỏi lại user / confirm)
  - `weather` (Open-Meteo Weather API - **Tool mới của nhóm**)
  - `format` (Trình bày digest)
  - `send` (Telegram)
- **Framework UI**: Streamlit (`app.py`)

## 📈 Kết quả Benchmark Qua Các Phiên Bản (`version_log.csv`)
- **`v0` (Baseline)**: Case Accuracy `0.3158` (31.58%)
- **`v1` (Fix Clarify Boundaries)**: Case Accuracy `0.5000` (50.00%)
- **`v2` (Precision Matrix & Boundaries)**: Case Accuracy **`0.7222` (72.22%)**, Multiturn Accuracy **`1.0000` (100%)**
- **`v3` (Fine-tune Routing Rules)**: Case Accuracy `0.5000`

## 📂 Danh mục File Sản phẩm Đã Hoàn Thành
- `starter_v0/.env`: File cấu hình môi trường chứa đủ 4 API Keys.
- `C:\Users\Admin\Desktop\API_KEYS_DAY04.txt`: File sao lưu API Keys ngoài Desktop.
- `starter_v0/artifacts/system_prompt.md`: System Instruction quy tắc chuẩn xác.
- `starter_v0/artifacts/tools.yaml`: Khai báo schema chuẩn化 các tool + tool `weather`.
- `starter_v0/tools/weather/`: Source code & `TOOL.md` cho tool mới `weather`.
- `starter_v0/data/eval_group.json`: 10 test cases thiết kế rạch ròi cho nhóm.
- `starter_v0/app.py`: Giao diện Web UI Streamlit mượt mà.
- `starter_v0/artifacts/version_log.csv`: Bảng ghi chép tiến trình đo lường.
- `starter_v0/artifacts/REPORT.md`: Báo cáo nộp bài hoàn chỉnh (Phần A & Phần B).
