# Deployment Information

## Public URL
https://my-ai-agent-zohy.onrender.com

## Platform
Render (Tích hợp Key Value Redis Store nội bộ)

## Test Commands

### Health Check
```bash
curl -X GET https://my-ai-agent-zohy.onrender.com/health
# Expected: {"status":"ok","uptime_seconds": ...}
```

### Readiness Check
```bash
curl -X GET https://my-ai-agent-zohy.onrender.com/ready
# Expected: {"status":"ready"}
```

### API Test (with authentication)
```bash
curl -X POST https://my-ai-agent-zohy.onrender.com/ask \
  -H "X-API-Key: secret" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_01", "question": "Hello AI"}'
# Expected: Trả về câu trả lời JSON kèm session_id
```

## Environment Variables Set
- `PORT` (Được cung cấp động bởi môi trường Render)
- `REDIS_URL` (Link nội bộ dạng redis:// kết nối trực tiếp đến Key Value Store của Render)
- `AGENT_API_KEY` = `secret` (Khoá bảo vệ API khỏi truy cập trái phép)
