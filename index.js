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

//thêm lỗi vào để test
// Cố tình lộ thông tin xác thực AWS và Database
const AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"; 
const DB_PASSWORD = "my-super-secret-password-123!";

// Cố tình dùng hàm nguy hiểm (lỗ hổng Injection)
function executeUserCommand(userInput) {
    eval("console.log('User input: " + userInput + "')");
}

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