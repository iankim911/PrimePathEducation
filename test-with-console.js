/**
 * PDF Viewer Test with Console Logging
 */

const puppeteer = require('puppeteer')

async function testWithConsole() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  })
  
  const page = await browser.newPage()
  
  // Capture console messages
  page.on('console', msg => {
    const text = msg.text()
    if (text.includes('🔍') || text.includes('✅') || text.includes('❌')) {
      console.log('BROWSER:', text)
    }
  })
  
  // Capture network failures
  page.on('requestfailed', request => {
    console.log('NETWORK FAIL:', request.url())
  })
  
  try {
    console.log('🚀 Testing PDF viewer with console logging...')
    
    // Navigate to exam edit page
    const examUrl = 'http://localhost:3000/exams/6ad25b5e-ec75-4656-acdb-b60db4ec63a5/edit'
    await page.goto(examUrl, { waitUntil: 'networkidle0' })
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('📋 Clicking Questions tab...')
    await page.evaluate(() => {
      const questionsTab = Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Questions'))
      if (questionsTab) questionsTab.click()
    })
    
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    console.log('📋 Checking console logs for API calls...')
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Take screenshot
    await page.screenshot({ path: 'console-test.png', fullPage: true })
    
    console.log('📋 Test completed - check browser console output above')
    return true
    
  } catch (error) {
    console.error('❌ Test error:', error.message)
    return false
    
  } finally {
    await new Promise(resolve => setTimeout(resolve, 5000))
    await browser.close()
  }
}

testWithConsole()