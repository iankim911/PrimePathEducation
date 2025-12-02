/**
 * Final QC Test for PDF Viewer Fix
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
    
    // Navigate to exam edit page
    const examUrl = 'http://localhost:3000/exams/6ad25b5e-ec75-4656-acdb-b60db4ec63a5/edit'
    console.log('📋 Navigating to:', examUrl)
    
    await page.goto(examUrl, { waitUntil: 'networkidle0' })
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('📋 Looking for Questions tab...')
    
    // Find Questions tab
    const questionsTab = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'))
      return buttons.find(button => button.textContent.includes('Questions'))
    })
    
    if (questionsTab.asElement()) {
      console.log('✅ Questions tab found')
      await questionsTab.asElement().click()
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      console.log('📋 Looking for Configure with PDF button...')
      
      // Find Configure with PDF button
      const configureButton = await page.evaluateHandle(() => {
        const buttons = Array.from(document.querySelectorAll('button'))
        return buttons.find(button => button.textContent.includes('Configure with PDF'))
      })
      
      if (configureButton.asElement()) {
        console.log('✅ Configure with PDF button found')
        await configureButton.asElement().click()
        await new Promise(resolve => setTimeout(resolve, 4000))
        
        console.log('📋 Checking for PDF viewer and errors...')
        
        // Check page content
        const pageText = await page.evaluate(() => document.body.textContent)
        
        // Check for errors
        if (pageText.includes('Bucket not found') || pageText.includes('404')) {
          console.log('❌ Still showing bucket/404 errors!')
          await page.screenshot({ path: 'pdf-viewer-error.png', fullPage: true })
          return false
        }
        
        // Check for PDF viewer elements
        const hasExamPdfText = pageText.includes('Exam PDF')
        const hasQuestionConfigText = pageText.includes('Question 1 Configuration')
        
        if (hasExamPdfText && hasQuestionConfigText) {
          console.log('✅ PDF viewer opened successfully!')
          console.log('✅ Split screen interface is working!')
          await page.screenshot({ path: 'pdf-viewer-success.png', fullPage: true })
          return true
        } else {
          console.log('⚠️ PDF viewer interface not fully loaded')
          console.log('   - Has Exam PDF section:', hasExamPdfText)
          console.log('   - Has Question Config section:', hasQuestionConfigText)
          await page.screenshot({ path: 'pdf-viewer-partial.png', fullPage: true })
          return false
        }
        
      } else {
        console.log('❌ Configure with PDF button not found')
        await page.screenshot({ path: 'no-configure-button.png', fullPage: true })
        return false
      }
      
    } else {
      console.log('❌ Questions tab not found')
      await page.screenshot({ path: 'no-questions-tab.png', fullPage: true })
      return false
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message)
    await page.screenshot({ path: 'test-error.png', fullPage: true })
    return false
    
  } finally {
    await browser.close()
  }
}

testPdfViewer().then(success => {
  if (success) {
    console.log('\n🟢 PDF VIEWER TEST PASSED!')
    console.log('✅ The fix is working correctly')
    console.log('✅ No bucket errors found')
    console.log('✅ Split screen interface loads properly')
  } else {
    console.log('\n🔴 PDF VIEWER TEST FAILED!')
    console.log('❌ Issues still need to be addressed')
    process.exit(1)
  }
})