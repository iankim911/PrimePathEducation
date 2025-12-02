/**
 * Simple QC Test for PDF Viewer Fix
 */

const puppeteer = require('puppeteer')

async function testPdfViewer() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  })
  
  const page = await browser.newPage()
  
  try {
    console.log('🚀 Testing PDF viewer fix...')
    
    // Navigate to exam edit page with known exam
    const examUrl = 'http://localhost:3000/exams/6ad25b5e-ec75-4656-acdb-b60db4ec63a5/edit'
    await page.goto(examUrl, { waitUntil: 'networkidle0' })
    
    console.log('📋 Page loaded, looking for Questions tab...')
    
    // Click Questions tab
    await new Promise(resolve => setTimeout(resolve, 2000))
    await page.click('button:has-text("Questions")')
    
    console.log('📋 Questions tab clicked, looking for Configure with PDF...')
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Click Configure with PDF
    await page.click('button:has-text("Configure with PDF")')
    
    console.log('📋 Configure with PDF clicked, waiting for split screen...')
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Check for errors
    const content = await page.content()
    
    if (content.includes('Bucket not found') || content.includes('statusCode":"404')) {
      console.log('❌ Still showing bucket/404 errors!')
      await page.screenshot({ path: 'pdf-test-error.png' })
      return false
    } else {
      console.log('✅ No bucket errors found!')
      
      // Check if PDF viewer opened
      const pdfSection = await page.$('div:has-text("Exam PDF")')
      if (pdfSection) {
        console.log('✅ PDF viewer section found')
        await page.screenshot({ path: 'pdf-test-success.png' })
        return true
      } else {
        console.log('⚠️ PDF viewer section not found')
        await page.screenshot({ path: 'pdf-test-partial.png' })
        return false
      }
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message)
    await page.screenshot({ path: 'pdf-test-failed.png' })
    return false
    
  } finally {
    await browser.close()
  }
}

testPdfViewer().then(success => {
  if (success) {
    console.log('🟢 PDF VIEWER TEST PASSED!')
  } else {
    console.log('🔴 PDF VIEWER TEST FAILED!')
    process.exit(1)
  }
})