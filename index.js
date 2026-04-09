const express = require('express')
const path = require('path')

const port = process.env.PORT || 5006

const app = express()

app.use(express.static(path.join(__dirname, 'public')))
app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'ejs')

app.get('/', (req, res) => {
  console.log(`Rendering 'pages/index' for route '/'`)
  res.render('pages/index')
})

// MỒI NHỬ 2: Lỗ hổng XSS (Cross-Site Scripting)
// Tool phân tích động (DAST - ZAP) sẽ gửi các payload độc hại vào biến 'name' 
// để xem server có bị tấn công không.
// app.get('/test-xss', (req, res) => {
//   const user = req.query.name || "Guest";
//   res.send(`<h1>Hello ${user}</h1><p>Welcome to Smart DevSecOps!</p>`);
// })

// MỒI NHỬ 3: Lỗ hổng SAST (Command Injection)
// Semgrep sẽ quét luồng dữ liệu tĩnh và phát hiện input của người dùng 
// được đưa thẳng vào lõi hệ điều hành mà không qua bộ lọc.
const { exec } = require('child_process');

app.get('/api/network-test', (req, res) => {
  const targetHost = req.query.host || 'google.com';
  
  // LỖI CHÍ MẠNG: Hacker có thể truyền vào host = "google.com; cat /etc/passwd" 
  // để đánh cắp file hệ thống của server.
  exec(`ping -c 2 ${targetHost}`, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).send(`Lỗi thực thi: ${error.message}`);
    }
    res.send(`<h1>Kết quả Ping:</h1><pre>${stdout}</pre>`);
  });
});

// Thêm một Hardcoded Secret giả để tăng điểm v_score
const INTERNAL_API_TOKEN = "jwt-secret-super-hardcoded-token-12345";

const server = app.listen(port, () => {
  console.log(`Listening on ${port}`)
})

// The number of seconds an idle Keep-Alive connection is kept open. This should be greater than the Heroku Router's
// Keep-Alive idle timeout of 90 seconds:
// - to ensure that the closing of idle connections is always initiated by the router and not the Node.js server
// - to prevent a race condition if the router sends a request to the app just as Node.js is closing the connection
// https://devcenter.heroku.com/articles/http-routing#keepalives
// https://nodejs.org/api/http.html#serverkeepalivetimeout
server.keepAliveTimeout = 95 * 1000

process.on('SIGTERM', async () => {
  console.log('SIGTERM signal received: gracefully shutting down')
  if (server) {
    server.close(() => {
      console.log('HTTP server closed')
    })
  }
})
