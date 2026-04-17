const express = require('express')
const path = require('path')
// Khai báo thư viện thực thi lệnh hệ thống (Để tạo lỗi DAST)
const { exec } = require('child_process');

const port = process.env.PORT || 5006
const app = express()

app.use(express.static(path.join(__dirname, 'public')))

app.get('/', (req, res) => {
  res.send('<h1>App is running</h1>')
})

// ==========================================
// 1. LỖI CHO SAST BẮT (Hardcoded Secrets)
// ==========================================
const AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"; 
const DB_PASSWORD = "my-super-secret-password-123!";
const INTERNAL_API_TOKEN = "jwt-secret-super-hardcoded-token-12345";

// ==========================================
// 2. LỖI CHO SAST BẮT (Hàm eval nguy hiểm)
// ==========================================
app.get('/api/eval', (req, res) => {
    const userInput = req.query.input || '"test"';
    // Lỗi Injection: Thực thi code JS bừa bãi
    eval("console.log('User input: " + userInput + "')");
    res.send("Đã chạy eval!");
});

// ==========================================
// 3. LỖI CHO DAST BẮT (Command Injection)
// ==========================================
app.get('/api/network-test', (req, res) => {
  const targetHost = req.query.host || 'google.com';
  
  // Lỗi chí mạng: DAST ZAP sẽ truyền "; cat /etc/passwd" vào biến host
  exec(`ping -c 1 ${targetHost}`, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Lỗi thực thi: ${error.message}`);
    }
    res.send(`<h1>Kết quả Ping:</h1><pre>${stdout}</pre>`);
  });
});

const server = app.listen(port, () => {
  console.log(`Listening on ${port}`)
})

server.keepAliveTimeout = 95 * 1000

process.on('SIGTERM', async () => {
  if (server) {
    server.close(() => {
      console.log('HTTP server closed')
    })
  }
})