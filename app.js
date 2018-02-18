const express = require('express')
const bodyParser = require('body-parser')
const cors = require('cors')
const morgan = require('morgan')
var serveStatic = require('serve-static')

const app = express()
app.use(morgan('combined'))
app.use(bodyParser.json())
app.use(cors())
app.use(serveStatic(__dirname + "/dist"))

app.get('/api/test', (req, res) => {
  res.send('it\'s working')
})

var port = process.env.PORT || 5000
app.listen(port)

console.log('Server listening at port '+ port)