/**
 * Full Flow Test for PDF Viewer Fix
 */

const puppeteer = require('puppeteer')

async function testFullFlow() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  })
  
  const page = await browser.newPage()
  
  // Capture all console messages
  page.on('console', msg => {
    console.log('BROWSER:', msg.text())
  })
  
  try {
    console.log('🚀 Testing full PDF viewer flow...')
    
    // Navigate to exam edit page
    const examUrl = 'http://localhost:3000/exams/6ad25b5e-ec75-4656-acdb-b60db4ec63a5/edit'
    await page.goto(examUrl, { waitUntil: 'networkidle0' })
    
    console.log('📋 Step 1: Page loaded')
    await page.screenshot({ path: 'step-1-page-loaded.png' })
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Click Questions tab
    console.log('📋 Step 2: Clicking Questions tab...')
    const questionsTabClicked = await page.evaluate(() => {
      const questionsTab = Array.from(document.querySelectorAll('button')).find(btn => 
        btn.textContent.includes('Questions')
      )
      if (questionsTab) {
        questionsTab.click()
        return true
      }
      return false
    })
    
    if (!questionsTabClicked) {
      console.log('❌ Questions tab not found')
      await page.screenshot({ path: 'error-no-questions-tab.png' })
      return false
    }
    
    console.log('✅ Questions tab clicked')
    await new Promise(resolve => setTimeout(resolve, 3000))
    await page.screenshot({ path: 'step-2-questions-tab.png' })
    
    // Look for Configure with PDF button
    console.log('📋 Step 3: Looking for Configure with PDF button...')
    const configureButtonFound = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'))
      const configureButton = buttons.find(btn => 
        btn.textContent.includes('Configure with PDF')
      )
      return !!configureButton
    })
    
    if (!configureButtonFound) {
      console.log('❌ Configure with PDF button not found')
      await page.screenshot({ path: 'error-no-configure-button.png' })
      return false
    }
    
    console.log('✅ Configure with PDF button found')
    
    // Click Configure with PDF
    console.log('📋 Step 4: Clicking Configure with PDF...')
    const splitScreenOpened = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'))
      const configureButton = buttons.find(btn => 
        btn.textContent.includes('Configure with PDF')
      )
      if (configureButton) {
        configureButton.click()
        return true
      }
      return false
    })
    
    if (!splitScreenOpened) {
      console.log('❌ Failed to click Configure with PDF')
      return false
    }
    
    console.log('✅ Configure with PDF button clicked')
    await new Promise(resolve => setTimeout(resolve, 5000)) // Wait longer for split screen
    await page.screenshot({ path: 'step-3-after-configure-click.png' })
    
    // Check if split screen opened
    console.log('📋 Step 5: Checking if split screen opened...')
    const splitScreenElements = await page.evaluate(() => {
      const examPdfText = document.body.textContent.includes('Exam PDF')
      const questionConfigText = document.body.textContent.includes('Question 1 Configuration')
      const bucketError = document.body.textContent.includes('Bucket not found')
      const status404 = document.body.textContent.includes('404')
      
      return {
        examPdfText,
        questionConfigText,
        bucketError,
        status404
      }
    })
    
    console.log('📊 Split screen check results:', splitScreenElements)
    
    if (splitScreenElements.examPdfText && splitScreenElements.questionConfigText) {
      console.log('✅ Split screen opened successfully')
      
      if (splitScreenElements.bucketError || splitScreenElements.status404) {
        console.log('❌ Still showing bucket/404 errors')
        await page.screenshot({ path: 'error-still-showing-errors.png' })
        return false
      } else {
        console.log('✅ No bucket/404 errors found!')
        await page.screenshot({ path: 'success-split-screen.png' })
        return true
      }
    } else {
      console.log('❌ Split screen did not open properly')
      await page.screenshot({ path: 'error-split-screen-not-opened.png' })
      return false
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message)
    await page.screenshot({ path: 'test-error.png' })
    return false
    
  } finally {
    await new Promise(resolve => setTimeout(resolve, 3000))
    await browser.close()
  }
}

testFullFlow().then(success => {
  if (success) {
    console.log('\n🟢 FULL FLOW TEST PASSED!')
    console.log('✅ PDF viewer is working correctly')
  } else {
    console.log('\n🔴 FULL FLOW TEST FAILED!')
  }
})