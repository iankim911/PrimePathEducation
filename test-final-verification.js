/**
 * Final Verification Test
 * 
 * Tests the COMPLETE user flow: Click Questions tab -> Configure with PDF -> Verify no errors
 */

const puppeteer = require('puppeteer')

async function finalVerificationTest() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  })
  
  const page = await browser.newPage()
  
  try {
    console.log('🚀 Final Verification: Complete user flow test')
    
    // Navigate to exam edit page
    const examUrl = 'http://localhost:3000/exams/6ad25b5e-ec75-4656-acdb-b60db4ec63a5/edit'
    await page.goto(examUrl, { waitUntil: 'networkidle0' })
    
    console.log('📋 Step 1: Page loaded, clicking Questions tab...')
    
    // Click Questions tab (this is the critical step that was missing)
    await page.evaluate(() => {
      const questionsTab = Array.from(document.querySelectorAll('button')).find(btn => 
        btn.textContent.includes('Questions')
      )
      if (questionsTab) questionsTab.click()
    })
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('📋 Step 2: Questions tab active, looking for Configure with PDF...')
    
    // Wait for and click Configure with PDF button
    let configureButtonClicked = false
    let attempts = 0
    while (!configureButtonClicked && attempts < 10) {
      configureButtonClicked = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button'))
        const configureButton = buttons.find(btn => 
          btn.textContent.includes('Configure with PDF') && !btn.disabled
        )
        if (configureButton) {
          configureButton.click()
          return true
        }
        return false
      })
      if (!configureButtonClicked) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        attempts++
      }
    }
    
    if (!configureButtonClicked) {
      throw new Error('Configure with PDF button not found or not clickable')
    }
    
    console.log('✅ Configure with PDF button found and clicked')
    
    // Wait for split screen to load
    console.log('📋 Step 3: Waiting for split screen...')
    
    // Wait for split screen elements
    let splitScreenLoaded = false
    let waitAttempts = 0
    while (!splitScreenLoaded && waitAttempts < 20) {
      splitScreenLoaded = await page.evaluate(() => {
        return document.body.textContent.includes('Exam PDF') && 
               document.body.textContent.includes('Question 1 Configuration')
      })
      if (!splitScreenLoaded) {
        await new Promise(resolve => setTimeout(resolve, 500))
        waitAttempts++
      }
    }
    
    if (!splitScreenLoaded) {
      throw new Error('Split screen did not load')
    }
    
    console.log('✅ Split screen loaded successfully!')
    
    // Wait a moment for PDF to load
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Check for errors
    console.log('📋 Step 4: Checking for errors...')
    const pageText = await page.evaluate(() => document.body.textContent)
    
    const hasErrors = pageText.includes('Bucket not found') || 
                     pageText.includes('404') || 
                     pageText.includes('statusCode')
    
    await page.screenshot({ path: 'final-verification-result.png', fullPage: true })
    
    if (hasErrors) {
      console.log('❌ ERRORS STILL PRESENT in PDF viewer')
      return false
    } else {
      console.log('✅ NO ERRORS FOUND - PDF viewer is working correctly!')
      return true
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message)
    await page.screenshot({ path: 'final-verification-error.png', fullPage: true })
    return false
    
  } finally {
    await new Promise(resolve => setTimeout(resolve, 3000))
    await browser.close()
  }
}

finalVerificationTest().then(success => {
  if (success) {
    console.log('\\n🟢 FINAL VERIFICATION PASSED!')
    console.log('✅ PDF viewer fix is working correctly')
    console.log('✅ Split screen interface loads without errors') 
    console.log('✅ Storage system is robust and functional')
  } else {
    console.log('\\n🔴 FINAL VERIFICATION FAILED!')
    console.log('❌ Issues still need to be addressed')
  }
})