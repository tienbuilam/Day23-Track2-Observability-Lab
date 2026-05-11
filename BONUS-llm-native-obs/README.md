# BONUS-llm-native-obs — Self-hosted Langfuse + LangChain LLM Trace

## Mục tiêu

Capture 1 LangChain LLM trace vào self-hosted Langfuse instance.

**Checkpoint rubric:** Langfuse self-hosted (v2, PostgreSQL + Redis, no ClickHouse required), capture 1 LangChain LLM trace (10 pts bonus).

---

## Kiến trúc

```
LangChain app (langfuse-trace.py)
    │
    │  LangfuseCallbackHandler (traces every LLM call)
    ▼
Langfuse service (:3000)
    │
    ├── PostgreSQL (metrics, traces, users)
    └── Redis (session cache)
```

---

## Cách chạy

### 1. Start Langfuse stack

```bash
cd BONUS-llm-native-obs/
docker compose up -d
```

Đợi ~30 giây cho Langfuse khởi tạo database schema.

### 2. Truy cập Langfuse UI

Mở: **http://localhost:3002**

Đăng nhập lần đầu:
- **Email:** `admin@langfuse.com`
- **Password:** `langfuse123`

### 3. Lấy API keys

Sau khi login, vào **Settings → API Keys** trong Langfuse UI:
- Copy **Public Key** (bắt đầu bằng `pk-lf-`)
- Copy **Secret Key** (bắt đầu bằng `sk-lf-`)
- Copy **Project ID**

### 4. Update credentials

Edit `langfuse-trace.py`, thay các giá trị:

```python
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-xxxxxxxxxxxx"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-xxxxxxxxxxxx"
```

### 5. (Optional) Dùng real LLM

Để trace hiển thị token usage thực, set OpenAI key:

```bash
export OPENAI_API_KEY=sk-...
python langfuse-trace.py
```

Nếu không có OpenAI key, script vẫn chạy với mock response — Langfuse vẫn ghi nhận trace.

### 6. Chạy script

```bash
pip install langfuse langchain langchain-openai langchain-core
python langfuse-trace.py
```

Output:

```
============================================================
Langfuse Self-Hosted — LangChain LLM Trace Capture
============================================================

Running LangChain chain with prompt: Explain in one sentence...
Response: Observability...
Trace URL: http://localhost:3002/project/xxx/traces/xxx
Open the URL above to see the LangChain LLM trace in Langfuse.
```

### 7. Screenshot

Mở trace URL trong browser → screenshot panel **Trace Detail** → save vào
`BONUS-llm-native-obs/screenshots/langfuse-trace.png`.

---

## Screenshot checklist

- [ ] `screenshots/langfuse-trace.png` — Trace detail panel trong Langfuse UI

---

## Cleanup

```bash
docker compose down     # stop (giữ data)
docker compose down -v  # stop + xoá data volume
```

---

## Troubleshooting

| Vấn đề | Nguyên nhân | Fix |
|---|---|---|
| Langfuse UI không load | Container chưa ready | `docker compose logs -f langfuse`, đợi thêm 30s |
| Login fail | Lần đầu chưa có DB | Đợi `postgres` healthcheck pass rồi thử lại |
| Trace không hiện | API keys sai | Kiểm tra lại trong Settings → API Keys |
| Import error | Thiếu package | `pip install langfuse langchain langchain-openai` |
