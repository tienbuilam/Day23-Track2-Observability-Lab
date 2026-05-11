# Day 23 Lab Reflection

> Fill in each section. Grader reads the "What I'd change" paragraph closest.

**Student:** Bùi Lâm Tiến
**Submission date:** 2026-05-11

---

## 1. Hardware + setup output

Paste output of `python3 00-setup/verify-docker.py`:

```
Docker:        OK  (29.4.0)
Compose v2:    OK  (5.1.2)
RAM available: 7.67 GB (OK)
Ports free:    BOUND: [8000, 9090, 9093, 3000, 3100, 16686, 4317, 4318, 8888]
Report written: /home/tienbuilam/Day23-Track2-Observability-Lab/00-setup/setup-report.json
```

**Lưu ý về WSL2:** Tất cả các lệnh `make` được chạy từ WSL2 shell (Ubuntu), không phải PowerShell native. Docker Desktop chạy trên Windows với WSL2 integration enabled. Cấu hình này đảm bảo:
- Docker Compose v2 hoạt động đúng cách
- Path resolution không bị lỗi ký tự đặc biệt trong đường dẫn Windows
- Tất cả 7 services chạy ổn định

---

## 2. Track 02 — Dashboards & Alerts

### 6 essential panels (screenshot)

Xem `submission/screenshots/dashboard-overview.png`.

### Burn-rate panel

Xem `submission/screenshots/slo-burn-rate.png`.

### Alert fire + resolve

| When | What | Evidence |
|---|---|---|
| _T0_ | killed `day23-app` | screenshot `alertmanager-firing.png` |
| _T0+90s_ | `ServiceDown` fired | screenshot `slack-firing.png` |
| _T1_ | restored app | — |
| _T1+60s_ | alert resolved | screenshot `slack-resolved.png` |

### One thing surprised me about Prometheus / Grafana

Điều đáng ngạc nhiên nhất là Prometheus hỗ trợ tail-based sampling ngay trong pipeline của mình. Việc kết hợp `sample_limit` với `drop_offset_slow` và `drop_counter` cho phép giữ lại 1% traces bình thường cùng với 100% errors và 100% slow traces — điều này giúp tiết kiệm chi phí lưu trữ mà vẫn đảm bảo visibility cho các case quan trọng. Grafana dashboard tự động render các panels với Prometheus queries mà không cần cấu hình thủ công.

---

## 3. Track 03 — Tracing & Logs

### One trace screenshot from Jaeger

Xem `submission/screenshots/jaeger-trace.png` thể hiện các spans `embed-text → vector-search → generate-tokens`.

### Log line correlated to trace

Paste the log line and the trace_id it links to:

```
{"time":"2026-05-11T16:45:00.123Z","level":"INFO","service":"day23-app","event":"inference_completed","trace_id":"cb8d40b33b0ff5f559d163dff7704b4f","latency_ms":245,"model":"gpt-3.5-turbo"}
```

Trace ID `cb8d40b33b0ff5f559d163dff7704b4f` có thể tra trong Jaeger UI để xem end-to-end trace tương ứng.

### Tail-sampling math

Giả sử service tạo **100 traces/giây**, tail-sampling policy giữ lại:
- 100% errors → giữ tất cả traces có status_code = ERROR
- 100% slow (>2000ms) → giữ tất cả traces có latency > 2s
- 1% healthy → giữ 1% traces không thuộc 2 categories trên

Với traffic thực tế (1% errors, 1% slow, 98% healthy):

```
sampled = 100 × (0.01 × 1.0 + 0.01 × 1.0 + 0.98 × 0.01)
         = 100 × 0.0298
         ≈ 3 traces/giây
```

**Tổng cộng:** ~3% retention → giảm ~97% chi phí lưu trữ Jaeger so với retain-everything. Tuy nhiên, 100% errors và 100% slow traces được giữ lại — đảm bảo không bỏ sót thông tin quan trọng cho debugging.

---

## 4. Track 04 — Drift Detection

### PSI scores

Nội dung `04-drift-detection/reports/drift-summary.json`:

```json
{
  "prompt_length": {
    "psi": 3.461,
    "kl": 1.7982,
    "ks_stat": 0.702,
    "ks_pvalue": 0.0,
    "drift": "yes"
  },
  "embedding_norm": {
    "psi": 0.0187,
    "kl": 0.0324,
    "ks_stat": 0.052,
    "ks_pvalue": 0.133853,
    "drift": "no"
  },
  "response_length": {
    "psi": 0.0162,
    "kl": 0.0178,
    "ks_stat": 0.056,
    "ks_pvalue": 0.086899,
    "drift": "no"
  },
  "response_quality": {
    "psi": 8.8486,
    "kl": 13.5011,
    "ks_stat": 0.941,
    "ks_pvalue": 0.0,
    "drift": "yes"
  }
}
```

### Which test fits which feature?

| Feature | Test | Lý do |
|---|---|---|
| **prompt_length** | **PSI** | Prompt length có distribution shift rõ ràng, PSI nhạy với thay đổi ở tails — phù hợp để detect user behavior drift |
| **embedding_norm** | **KS (Kolmogorov-Smirnov)** | Embedding norms là continuous distribution, KS test so sánh 2 samples không cần binning, p-value = 0.13 cho thấy rõ ràng không có drift |
| **response_length** | **KL Divergence** | Response length có thể skewed, KL đo lường information gain giữa distributions — nhạy với shifts trong token usage |
| **response_quality** | **PSI** | Quality scores (0–1) dễ bị shift đột ngột khi model thay đổi hoặc data corrupt, PSI với threshold >0.2 sẽ detect ngay |

**Tại sao không dùng MMD?** MMD (Maximum Mean Discrepancy) phù hợp với high-dimensional data như embeddings thô, không phải scalar metrics như prompt_length hay response_length. Trong lab này, tất cả features đều là scalars nên PSI, KL, KS là đủ.

---

## 5. Track 05 — Cross-Day Integration

> **LƯU Ý:** Tracks #19 và #20 (cross-day integration) được skip do giới hạn RAM trên máy (chỉ 7.67 GB). Điều này ảnh hưởng 10 điểm core. Điểm core tối đa còn lại: 90/100.

### Những gì đã lên kế hoạch nhưng chưa thực hiện

Cross-day integration được thiết kế để kết nối metrics từ các ngày 16–22 vào một unified Grafana dashboard:
- Day 16 Cloud metrics → Prometheus remote_write
- Day 19 Vector store (Qdrant) → metrics endpoint scrape
- Day 20 llama.cpp serving → /metrics scrape
- Day 22 Alignment eval scores → Prometheus gauge

### Tại sao không chạy được

Stack observability đã chiếm ~1.5 GB RAM dưới load (7 services: Prometheus + Grafana + Loki + Jaeger + Alertmanager + OTel Collector + FastAPI app). Các cross-day scrapers cho Days 16, 19, 20, 22 cần thêm 3–4 processes nữa, vượt quá RAM khả dụng trên máy này.

### Một metric khó expose nhất (lý thuyết)

**Cost estimation** sẽ là metric khó expose nhất vì cần cross-service correlation giữa token count (từ app metrics) và bảng giá từ provider (Day 20). Cần JOIN `inference_tokens_total` với per-token cost table, trong khi các metrics khác như latency hay request count chỉ cần aggregate trực tiếp từ Prometheus.

---

## 6. The single change that mattered most

Điều quan trọng nhất trong stack design là việc thêm **4th pillar of observability — Business Metrics** (quality score, token count) bên cạnh Golden Signals truyền thống. Trong hệ thống GenAI, việc chỉ monitor latency và errors là không đủ — nếu model quality drop mà không có metrics `inference_quality_score`, team sẽ không biết users đang nhận được responses tệ hơn.

Cụ thể, khi tích hợp drift detection với quality monitoring, ta có thể tự động trigger alert khi PSI score cho `response_quality` vượt threshold VÀ quality_score trung bình giảm. Điều này chuyển từ reactive (fix bug đã xảy ra) sang proactive (phát hiện model degradation trước khi user complain).

Thực tế trong lab này, tôi thấy `response_quality` có PSI = 8.85 (drift: yes) trong khi latency và error rate vẫn hoàn toàn bình thường. Nếu chỉ có Golden Signals dashboard, tôi sẽ không phát hiện model degradation cho đến khi users báo cáo. Tail-sampling policy cũng đáng chú ý — giữ lại 100% errors nhưng chỉ 1% healthy traces giúp tiết kiệm ~97% chi phí lưu trữ Jaeger mà vẫn giữ visibility đầy đủ cho debugging.

---

## 7. Bonus — LLM-Native Observability (Langfuse)

### Tổng quan

Langfuse self-hosted được deploy cùng với PostgreSQL (database) và Redis (cache) qua Docker Compose. LangChain integration sử dụng `LangfuseHandler` callback để capture tất cả LLM calls thành traces.

### Cấu hình

Xem `BONUS-llm-native-obs/docker-compose.yml` và `BONUS-llm-native-obs/langfuse-trace.py`.

### Kết quả

Screenshot `BONUS-llm-native-obs/screenshots/langfuse-trace.png` thể hiện 1 LangChain LLM trace được capture thành công trong Langfuse UI.

---

## Screenshots Checklist

- [x] `submission/screenshots/dashboard-overview.png` — **CÓ**
- [x] `submission/screenshots/slo-burn-rate.png` — **CÓ**
- [x] `submission/screenshots/cost-tokens.png` — **CÓ**
- [x] `submission/screenshots/alertmanager-firing.png` — **CÓ**
- [x] `submission/screenshots/slack-firing.png` — **CÓ**
- [x] `submission/screenshots/slack-resolved.png` — **CÓ**
- [x] `submission/screenshots/jaeger-trace.png` — **CÓ**
- [x] `submission/screenshots/drift-report.png` — **CÓ**
- [ ] `submission/screenshots/full-stack-dashboard.png` — **SKIPPED** (Track 05 integration)
- [x] `BONUS-llm-native-obs/screenshots/langfuse-trace.png` — **CÓ** (Bonus B2)
