/**
 * Health Check Script for Production Deployment
 * Verifies that the application is running correctly
 */

const http = require('http')

const options = {
  host: 'localhost',
  port: process.env.PORT || 3000,
  path: '/api/health',
  timeout: 2000,
  method: 'GET'
}

const request = http.request(options, (res) => {
  console.log(`Health check status: ${res.statusCode}`)
  
  if (res.statusCode === 200) {
    process.exit(0) // Healthy
  } else {
    process.exit(1) // Unhealthy
  }
})

request.on('timeout', () => {
  console.log('Health check timeout')
  request.destroy()
  process.exit(1)
})

request.on('error', (err) => {
  console.log('Health check error:', err.message)
  process.exit(1)
})

request.end()