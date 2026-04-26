const express = require('express')
const path = require('path')

const port = process.env.PORT || 5006
const app = express()

app.use(express.static(path.join(__dirname, 'public')))

app.get('/', (req, res) => {
  res.send('<h1>App is running securely!</h1>')
})

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