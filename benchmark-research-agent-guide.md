# Hướng Dẫn & Nguồn Benchmark Cho Research Agent (Day 04 Lab v2)

## 🎯 1. Benchmark Có Sẵn Trong Dự Án (Repo hiện tại)

Trong bài lab Day 04, các bộ benchmark đã được đóng gói sẵn trong thư mục `starter_v0/data/` dưới dạng các file JSON test cases:

| File Benchmark | Mục đích & Số lượng | Cách sử dụng / Lệnh chạy |
|---|---|---|
| **`data/eval_base.json`** | **Base Eval cố định (19 cases)**: Đo khả năng chọn đúng tool, truyền đúng tham số (args), hỏi lại khi thiếu thông tin, từ chối câu hỏi ngoài phạm vi. | `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json` |
| **`data/eval_group.json`** | **Team Eval (10 cases)**: Bộ benchmark do chính nhóm tự thiết kế (5 câu đơn single-turn + 5 câu hội thoại multi-turn). | `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json` |
| **`data/eval_research_extension.json`** | **Extension Eval (11 cases)**: Benchmark mở rộng cho các tool đọc PDF arXiv (`papers`, `paper_text`) và nội quy công ty (`policy`). | `python run_eval.py --provider openrouter --version v3 --suite extension --eval-cases data/eval_research_extension.json` |

---

## 📊 2. Các Chỉ Số Benchmark Được Đo Lường

Khi chạy script `run_eval.py`, hệ thống sẽ tự động tính toán các chỉ số trong file báo cáo `runs/*.json`:

1. **`summary.case_accuracy`**: Tỷ lệ phần trăm tổng số case đạt điểm hoàn hảo.
2. **`summary.tool_routing_accuracy`**: Tỷ lệ gọi đúng tên Tool cần dùng.
3. **`summary.argument_accuracy`**: Tỷ lệ truyền đúng giá trị các tham số (arguments) vào tool.
4. **`summary.multiturn_accuracy`**: Tỷ lệ xử lý đúng trong các ngữ cảnh hội thoại nhiều lượt (carry over context / sửa lỗi ở lượt sau).

---

## 🌍 3. Các Bộ Benchmark Chuẩn Quốc Tế Cho Tool Use & AI Agent (Tham Khảo)

Nếu nhóm muốn tìm hiểu các bộ Benchmark thực tế đang được thế giới dùng để chấm điểm Tool Calling / Agent:

1. **BFCL (Berkeley Function Calling Benchmark)**:
   - **Tổ chức**: UC Berkeley (Gorilla LLM).
   - **Mục đích**: Benchmark chuẩn nhất hiện nay cho khả năng gọi API/Function Calling của các model (GPT-4o, Claude 3.5, Gemini 1.5, Llama 3...).
   - **Link**: [https://gorilla.cs.berkeley.edu/leaderboard.html](https://gorilla.cs.berkeley.edu/leaderboard.html)

2. **ToolBench / ToolEval**:
   - **Tổ chức**: Tsinghua University / OpenBMB.
   - **Mục đích**: Đánh giá Agent với hơn 16,000 thực tế REST APIs (môi trường phức tạp, nhiều bước liên tiếp).
   - **Link**: [https://github.com/OpenBMB/ToolBench](https://github.com/OpenBMB/ToolBench)

3. **GAIA (General AI Assistants Benchmark)**:
   - **Tổ chức**: Meta AI, Hugging Face, AutoGPT.
   - **Mục đích**: Đánh giá AI Agent giải quyết các tác vụ thực tế cần duyệt web, đọc file, tính toán và dùng nhiều tool tổng hợp.
   - **Link**: [https://huggingface.co/spaces/gaia-benchmark/leaderboard](https://huggingface.co/spaces/gaia-benchmark/leaderboard)

4. **WebArena / OSWorld**:
   - **Mục đích**: Benchmark cho Agent tương tác trực tiếp với giao diện web và hệ điều hành.

---

## 📝 4. Hướng Dẫn Nhóm Tự Tạo Benchmark (`eval_group.json`)

Để tự tạo 10 câu Benchmark cho nhóm mình:
- **5 câu Single-turn (`query`)**: 
  - Đặt ra các tình huống thiếu link, sai tên người nổi tiếng, hỏi tin tức hôm nay vs tin tuần này.
- **5 câu Multi-turn (`turns`)**: 
  - Lượt 1 hỏi chung chung ➔ Agent hỏi lại (`clarify`) ➔ Lượt 2 user bổ sung thông tin ➔ Agent gọi đúng tool.
- Xem file mẫu cấu trúc JSON tại: `starter_v0/samples/eval_group.schema.example.json`.
