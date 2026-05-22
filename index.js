const express = require('express')
const path = require('path')
const helmet = require('helmet')
const { MongoClient } = require('mongodb')
const marked = require('marked')
const port = process.env.PORT || 5006

const app = express()

const MONGO_URI = process.env.MONGO_URI || "mongodb+srv://mikazuki241125111_db_user:15102005Huuminnh!@cluster0.ozb6qg2.mongodb.net/?appName=Cluster0";
let db;
MongoClient.connect(MONGO_URI)
  .then(client => {
    db = client.db('devsecops');
    console.log('Connected to MongoDB');
  })
  .catch(err => console.error(err));

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

app.get('/feedback', async (req, res) => {
  try {
    if (!db) {
      return res.status(500).send('Database not initialized');
    }
    const reviews = await db.collection('ai_reviews').find().sort({ timestamp: -1 }).limit(10).toArray();
    
    // Parse markdown into HTML
    const formattedReviews = reviews.map(r => ({
      ...r,
      html_content: marked.parse(r.markdown_content || ""),
      date: r.timestamp ? new Date(r.timestamp).toLocaleString() : "Unknown date"
    }));

    res.render('pages/feedback', { reviews: formattedReviews });
  } catch (error) {
    console.error(error);
    res.status(500).send('Error fetching feedback');
  }
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