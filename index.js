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

//thêm lỗi vào để test SAST
// Cố tình lộ thông tin xác thực AWS và Database
// const AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"; 
// const DB_PASSWORD = "my-super-secret-password-123!";

// // Cố tình dùng hàm nguy hiểm (lỗ hổng Injection)
// function executeUserCommand(userInput) {
//     eval("console.log('User input: " + userInput + "')");
// }

const server = app.listen(port, () => {
  console.log(`Listening on ${port}`)
})

server.keepAliveTimeout = 95 * 1000

process.on('SIGTERM', async () => {
  console.log('SIGTERM signal received: gracefully shutting down')
  if (server) {
    server.close(() => {
      console.log('HTTP server closed')
    })
  }
})