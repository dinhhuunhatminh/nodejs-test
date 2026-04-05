const express = require('express')
const path = require('path')

const port = process.env.PORT || 5006

const app = express()

// 🚨 MỒI NHỬ 1: Lộ lọt mã bí mật (Hardcoded Secret)
// Tool phân tích tĩnh (SAST) sẽ đọc mã nguồn và bắt lỗi này ngay lập tức.
const AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE";

app.use(express.static(path.join(__dirname, 'public')))
app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'ejs')

app.get('/', (req, res) => {
  console.log(`Rendering 'pages/index' for route '/'`)
  res.render('pages/index')
})

// 🚨 MỒI NHỬ 2: Lỗ hổng XSS (Cross-Site Scripting)
// Tool phân tích động (DAST - ZAP) sẽ gửi các payload độc hại vào biến 'name' 
// để xem server có bị tấn công không.
app.get('/test-xss', (req, res) => {
  const user = req.query.name || "Guest";
  res.send(`<h1>Hello ${user}</h1><p>Welcome to Smart DevSecOps!</p>`);
})

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
