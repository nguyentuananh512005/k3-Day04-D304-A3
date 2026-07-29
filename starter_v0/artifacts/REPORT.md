# Day 04 Lab v2 Report — Research Agent

## Team

- **Team Name**: K3-Day04-Group3
- **Members & Roles**:
  - **Nguyễn Tuấn Anh (2A202601669 - Nhóm trưởng)**: Phụ trách Giao diện Web UI Streamlit (`app.py`), Tích hợp hệ thống, Báo cáo & Demo Rehearsal.
  - **Nguyễn Thị Lý (2A202601962)**: Phụ trách Lập trình Tool mới (`weather`), Viết `TOOL.md` và Smoke-test công cụ.
  - **Đỗ Hùng Anh (2A202601175)**: Phụ trách Thiết kế 10 Benchmark Team Eval Cases (`data/eval_group.json`), Tối ưu hóa Prompt & Tools Declaration (`v0` -> `v3`), Chạy `run_eval.py` & Log `version_log.csv`.
- **Provider/model**: Groq / `llama-3.1-8b-instant`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent tự động hỗ trợ tra cứu thông tin đa nguồn (Web, Twitter/X, Dự báo thời tiết), đọc sâu nội dung URL, xử lý các tình huống thiếu thông tin bằng cách chủ động hỏi lại người dùng (`clarify`), và hỏi xin xác nhận trước khi thực hiện các hành động nhạy cảm (như đăng bài Telegram).

**Link dùng thử (truy cập được trong showdown):**
- Localhost UI: `http://localhost:8501` (Chạy bằng `streamlit run app.py`)
- Public Tunnel URL: `https://trycloudflare.com/...` (Bật qua Cloudflare Tunnel)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu tham số hoặc xin xác nhận Yes/No trước khi xuất bản | không |
| `timeline` | Lấy danh sách bài đăng gần đây của một tài khoản Twitter theo handle | không |
| `social_search` | Tìm kiếm các bài đăng trên mạng xã hội Twitter theo từ khóa hoặc chủ đề | không |
| `lookup` | Tra cứu thông tin trên Internet & tin tức báo chí trực tuyến | không |
| `fetch` | Tải và cào đọc nội dung chi tiết từ đường link URL cụ thể | không |
| `weather` | Tra cứu thời tiết thực tế (nhiệt độ, tốc độ gió, thời tiết) của một thành phố | **CÓ (Tool mới của nhóm)** |
| `format` | Trình bày dữ liệu đã có thành bản tin digest Markdown | không |
| `send` | Gửi tin nhắn xuất bản lên Telegram | không |

## A3. Câu hỏi mẫu để thử

1. *"Thời tiết ở Hà Nội hôm nay thế nào?"* (Thử nghiệm Tool mới `weather`).
2. *"Tóm tắt 5 tweet mới nhất giúp mình"* ➔ Agent sẽ gọi `clarify` hỏi sếp muốn xem của ai.
3. *"Đăng bản tin này lên Telegram giúp mình"* ➔ Agent sẽ xin xác nhận Yes/No trước khi gửi.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Đoán bừa vs Hỏi lại khi thiếu handle | `v0`: Gọi `timeline(screenname='elonmusk')` đoán bừa.<br>`v2`: Gọi `clarify(response_type='text')`. | Từ v0 đoán bừa ➔ v2 khôn lên, chủ động gọi `clarify` xin thông tin. | `transcripts/v2_groq_demo1.json` |
| 2. Xác nhận trước khi gửi Telegram | `v0`: Tự tiện gọi `send`.<br>`v2`: Gọi `clarify(response_type='yes_no')`. | v0 tự ý gửi ➔ v2 có guardrail an toàn tuyệt đối. | `transcripts/v2_groq_demo2.json` |
| 3. Tra cứu thời tiết mới | Gọi `weather(city='Hanoi')`. | Thêm thành công năng lực mới cho Agent. | `transcripts/v2_groq_demo3.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

Dữ liệu trích xuất trực tiếp từ `artifacts/version_log.csv` và `runs/*.json`:

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline starter prompt | Mặc định đoán bừa missing args và gọi tool cho mọi câu | case_accuracy | 0.0000 | 0.3158 | `runs/v0_B_base_groq_20260729T103610706427.json` |
| v1 | Thêm boundary clarify & handle mapping | Ép buộc clarify khi thiếu handle/URL và xác nhận trước khi send; khai báo weather tool | case_accuracy | 0.3158 | 0.5000 | `runs/v1_B_base_groq_20260729T104342209305.json` |
| v2 | Ma trận quy tắc precision & parallel routing | Thêm quy tắc boundary nghiêm ngặt, gọi tool song song và xử lý out-of-scope | case_accuracy | 0.5000 | 0.7222 | `runs/v2_B_base_groq_20260729T104955419562.json` |
| v3 | Tinh chỉnh strict tool routing | Chuẩn hóa tham số timeframe và multi-turn carry-over | case_accuracy | 0.7222 | 0.5000 | `runs/v3_B_base_groq_20260729T110241121357.json` |

## B2. Failure analysis

Phân tích các ca thất bại thực tế từ run log `results[*].result.failures`:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R01_user_tweets_routing` | `wrong_tool` | `social_search` | Model nhầm lẫn giữa search từ khóa và lấy tweet tài khoản | Thêm mapping rõ ràng tên Sam Altman -> handle `sama` và ép dùng `timeline` |
| `R07_search_type_arg` | `wrong_arg_value` | `social_search(search_type='Latest')` | Không nhận diện được chữ "top/phổ biến" để đặt `search_type='Top'` | Thêm quy tắc ép `search_type='Top'` khi có từ "phổ biến" |
| `R12_confirm_before_send` | `wrong_boundary` | `send` | Tự tiện gửi Telegram không xin phép | Ép buộc `clarify(response_type='yes_no')` trước hành động ghi/gửi |

## B3. Team eval cases

Danh sách 10 test cases trong file `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `R01_group_weather` | Tra cứu thời tiết theo thành phố | `weather(city='Hanoi')` | PASS |
| `R02_group_clarify_topic` | Hỏi lại khi thiếu chủ đề tin tức | `clarify(response_type='text')` | PASS |
| `R03_group_out_of_scope` | Từ chối yêu cầu viết script Bash | `no_tool: true` (Refuse) | PASS |
| `R04_group_lookup_general` | Tra cứu khái niệm khoa học chung | `lookup(query='Quantum Computing', topic='general')` | PASS |
| `R05_group_confirm_send` | Xin xác nhận trước khi gửi Telegram | `clarify(response_type='yes_no')` | PASS |
| `M01_group_weather_clarify` | Multi-turn hỏi thời tiết bổ sung city ở lượt 2 | `weather(city='Tokyo')` | PASS |
| `M02_group_timeline_correction` | Multi-turn đính chính handle Elon Musk & limit=5 | `timeline(screenname='elonmusk', limit=5)` | PASS |
| `M03_group_switch_weather_to_news` | Multi-turn chuyển từ thời tiết sang tin tức AI | `lookup(query='AI', topic='news', timeframe='day')` | PASS |
| `M04_group_url_clarify` | Multi-turn cung cấp URL ở lượt 2 | `fetch(url='https://example.com/ai-report')` | PASS |
| `M05_group_social_search_carryover` | Multi-turn cập nhật search_type=Top | `social_search(query='DeepSeek', search_type='Top')` | PASS |

## B4. Live chat evidence

Thực hiện tương tác live chat thực tế ghi trong `transcripts/*.transcript.json`:

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Hỏi thời tiết Hà Nội | v2 | `weather(city='Hanoi')` | `transcripts/v2_groq_live1.json` | Trả về thông số nhiệt độ & thời tiết chính xác |
| Hỏi tóm tắt 5 tweet | v2 | `clarify(response_type='text')` | `transcripts/v2_groq_live2.json` | Hỏi lại người dùng thay vì đoán bừa |
| Đăng tin Telegram | v2 | `clarify(response_type='yes_no')` | `transcripts/v2_groq_live3.json` | Yêu cầu xác nhận Yes/No an toàn |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **Must-have: Tool mới (`weather`)** | `tools/weather/tool.py` | Lấy đúng nhiệt độ, độ ẩm và thời tiết real-time từ Open-Meteo API | Xử lý ngoại lệ khi nhập sai tên thành phố |
| **Core: Tavily Search (`lookup`)** | `tools/lookup/tool.py` | Tìm kiếm tin tức mới nhất theo khoảng thời gian day/week | Giới hạn max_results để tránh quá tải token |
| **Core: Firecrawl (`fetch`)** | `tools/fetch/tool.py` | Cào nội dung sạch định dạng Markdown từ URL | Timeout guardrail 15 giây |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Các quy tắc phân định ranh giới (Clarify boundaries), quy tắc chuyển đổi tên người thành handle (`Sam Altman` -> `sama`), và quy tắc xử lý các câu hỏi ngoài phạm vi (`no_tool`).
- **Which fixes belonged in `tools.yaml`?**
  Mô tả chi tiết ý định của từng tool, quy định giá trị mặc định (default values) và liệt kê rõ enum của các tham số (`response_type`, `search_type`, `topic`, `timeframe`).
- **Which failure needed manual review instead of automatic grading?**
  Các trường hợp tool execution bị lỗi mạng hoặc lỗi API 403 (như RapidAPI chưa subscribe) cần được kiểm tra thủ công log response.
- **What would you improve next?**
  Tích hợp thêm cơ chế tự sửa lỗi tham số (Self-Correction Loop) khi Tool trả về lỗi `city_not_found` hoặc `404 Not Found`.
