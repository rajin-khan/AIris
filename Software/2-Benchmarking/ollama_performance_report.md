# Ollama Model Performance Report for Raspberry Pi 5 (16GB)
**AIris Team Benchmark Suite**

Generated on: 2025-07-25 13:47:01

## Test Configuration
- **Test Question**: Why is the sky blue?
- **Models Tested**: 9
- **Successful Tests**: 7
- **Failed Tests**: 2

## Performance Rankings

### Top Performers (by Evaluation Rate)

| Rank | Model | Eval Rate (tokens/s) | Response Time (s) | Response Length (words) |
|------|-------|---------------------|-------------------|------------------------|
| 1 | `llama3.2:1b` | **29.77** | 52.4 | 229 |
| 2 | `tinydolphin:1.1b` | **27.19** | 8.0 | 75 |
| 3 | `gemma3:1b` | **25.69** | 29.3 | 260 |
| 4 | `qwen2.5:1.5b` | **19.48** | 22.9 | 181 |
| 5 | `gemma2:2b` | **12.29** | 55.6 | 230 |
| 6 | `qwen2.5:3b` | **9.34** | 67.8 | 278 |
| 7 | `llama3.2:3b` | **9.33** | 90.2 | 238 |

## Performance Summary

- **Fastest Model**: `llama3.2:1b` (29.77 tokens/s)
- **Average Rate**: 19.01 tokens/s
- **Median Rate**: 19.48 tokens/s

## Failed Tests

| Model | Error | Timestamp |
|-------|-------|-----------|
| `phi3.5:3.8b` | Timeout | 2025-07-25T13:26:18.394280 |
| `gemma3n:e2b` | Timeout | 2025-07-25T13:47:01.806834 |

## Detailed Results

### llama3.2:1b [SUCCESS]

- **Eval Rate**: 29.77 tokens/s
- **Response Time**: 52.4 seconds
- **Response Length**: 229 words
- **Timestamp**: 2025-07-25T13:10:18.203387

### gemma2:2b [SUCCESS]

- **Eval Rate**: 12.29 tokens/s
- **Response Time**: 55.6 seconds
- **Response Length**: 230 words
- **Timestamp**: 2025-07-25T13:16:50.700301

### phi3.5:3.8b [FAILED]

- **Eval Rate**: 0.00 tokens/s
- **Response Time**: 120.0 seconds
- **Response Length**: 0 words
- **Timestamp**: 2025-07-25T13:26:18.394280
- **Error**: Timeout

### tinydolphin:1.1b [SUCCESS]

- **Eval Rate**: 27.19 tokens/s
- **Response Time**: 8.0 seconds
- **Response Length**: 75 words
- **Timestamp**: 2025-07-25T13:28:44.231585

### qwen2.5:1.5b [SUCCESS]

- **Eval Rate**: 19.48 tokens/s
- **Response Time**: 22.9 seconds
- **Response Length**: 181 words
- **Timestamp**: 2025-07-25T13:32:32.752980

### qwen2.5:3b [SUCCESS]

- **Eval Rate**: 9.34 tokens/s
- **Response Time**: 67.8 seconds
- **Response Length**: 278 words
- **Timestamp**: 2025-07-25T13:40:13.634595

### gemma3:1b [SUCCESS]

- **Eval Rate**: 25.69 tokens/s
- **Response Time**: 29.3 seconds
- **Response Length**: 260 words
- **Timestamp**: 2025-07-25T13:43:31.524599

### llama3.2:3b [SUCCESS]

- **Eval Rate**: 9.33 tokens/s
- **Response Time**: 90.2 seconds
- **Response Length**: 238 words
- **Timestamp**: 2025-07-25T13:45:01.784633

### gemma3n:e2b [FAILED]

- **Eval Rate**: 0.00 tokens/s
- **Response Time**: 120.0 seconds
- **Response Length**: 0 words
- **Timestamp**: 2025-07-25T13:47:01.806834
- **Error**: Timeout

---
*Report generated by AIris Team Ollama Performance Testing Framework*
