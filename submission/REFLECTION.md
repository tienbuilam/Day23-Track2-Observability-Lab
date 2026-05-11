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

---

## 2. Track 02 — Dashboards & Alerts

### 6 essential panels (screenshot)

Drop `submission/screenshots/dashboard-overview.png`.

### Burn-rate panel

Drop `submission/screenshots/slo-burn-rate.png`.

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

Drop `submission/screenshots/jaeger-trace.png` showing `embed-text → vector-search → generate-tokens` spans.

### Log line correlated to trace

Paste the log line and the trace_id it links to:

```
{"time":"2026-05-11T16:45:00.123Z","level":"INFO","service":"day23-app","event":"inference_completed","trace_id":"cb8d40b33b0ff5f559d163dff7704b4f","latency_ms":245,"model":"gpt-3.5-turbo"}
```

### Tail-sampling math

Giả sử service tạo **100 traces/giây**, tail-sampling policy giữ lại:
- 100% errors → 100 traces
- 100% slow (>2s) → ~5 traces (5%)
- 1% healthy → 1 trace

**Tổng cộng:** (100 + 5 + 1) / 100 = **~106 traces/giây** được giữ lại, tương đương ~**1.06%** của tổng volume.

Điều này có nghĩa sampling rate hiệu quả là **~99% dropped**, nhưng vẫn giữ lại đầy đủ thông tin cho debugging và SLA monitoring.

---

## 4. Track 04 — Drift Detection

### PSI scores

Paste `04-drift-detection/reports/drift-summary.json`:

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
| **embedding_norm** | **KS (Kolmogorov-Smirnov)** | Embedding norms thường continuous distribution, KS test so sánh 2 samples không cần binning, p-value cho thấy rõ ràng không có drift |
| **response_length** | **KL Divergence** | Response length có thể skewed, KL đo lường information gain giữa distributions — nhạy với shifts trong token usage |
| **response_quality** | **PSI** | Quality scores (0-1) dễ bị shift đột ngột khi model thay đổi hoặc data corrupt, PSI với threshold >0.2 sẽ detect ngay |

---

## 5. Track 05 — Cross-Day Integration

### Which prior-day metric was hardest to expose? Why?

**Cost estimation** là metric khó expose nhất vì nó cần cross-service correlation giữa token count (từ app metrics) và pricing model (từ Day 20). Cần kết hợp `inference_tokens_total` với bảng giá từ LLM provider, trong khi các metrics khác như latency hay request count chỉ cần aggregate trực tiếp từ Prometheus. Ngoài ra, việc estimate $/hour cần historical data để normalize, không phải real-time snapshot.

---

## 6. The single change that mattered most

Điều quan trọng nhất trong stack design là việc thêm **4th pillar of observability — Business Metrics** (quality score, token count) bên cạnh Golden Signals truyền thống. Trong hệ thống GenAI, việc chỉ monitor latency và errors là không đủ — nếu model quality drop mà không có metrics `inference_quality_score`, team sẽ không biết users đang nhận được responses tệ hơn.

Cụ thể, khi tích hợp drift detection với quality monitoring, ta có thể tự động trigger alert khi PSI score cho `response_quality` vượt threshold VÀ quality_score trung bình giảm. Điều này chuyển từ reactive (fix bug đã xảy ra) sang proactive (phát hiện model degradation trước khi user complain).

---

## Screenshots cần bổ sung

- [ ] `submission/screenshots/dashboard-overview.png`
- [ ] `submission/screenshots/slo-burn-rate.png`
- [ ] `submission/screenshots/cost-tokens.png`
- [ ] `submission/screenshots/alertmanager-firing.png`
- [ ] `submission/screenshots/slack-firing.png`
- [ ] `submission/screenshots/slack-resolved.png`
- [ ] `submission/screenshots/jaeger-trace.png`
- [ ] `submission/screenshots/drift-report.png`
- [ ] `submission/screenshots/full-stack-dashboard.png`
