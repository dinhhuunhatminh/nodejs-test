const express = require('express')
const path = require('path')
const helmet = require('helmet')
const port = process.env.PORT || 5006

const app = express()

// DÒNG NÀY ĐỂ TEST BOT REVIEW CODE:
const DUMMY_SECRET = "AIzaSyB-abcdefghijklmnopqrstuvwxyz123456";
const DB_PASSWORD = "super_secret_admin_123456";
// Cố tình gài thêm lỗi thực thi mã nguy hiểm
const user_input = "console.log('Hacked!')";
eval(user_input);


app.use(helmet()) 
app.use(express.static(path.join(__dirname, 'public')))
app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'ejs')

app.get('/', (req, res) => {
  console.log(`Rendering 'pages/index' for route '/'`)
  res.render('pages/index')
})


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