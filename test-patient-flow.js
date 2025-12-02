/**
 * Patient Flow Test - waits for UI updates
 */

const puppeteer = require('puppeteer')

async function waitForElement(page, selector, timeout = 10000) {
  try {
    await page.waitForSelector(selector, { timeout })
    return true
  } catch (error) {
    return false
  }
}

async function waitForText(page, text, timeout = 10000) {
  try {
    await page.waitForFunction(
      (text) => document.body.textContent.includes(text),
      { timeout },
      text
    )
    return true
  } catch (error) {
    return false
  }
}

async function testPatientFlow() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  })
  
  const page = await browser.newPage()
  
  // Capture all console messages
  page.on('console', msg => {
    const text = msg.text()
    if (text.includes('🔍') || text.includes('✅') || text.includes('❌')) {
      console.log('BROWSER:', text)
    }
  })
  
  try {
    console.log('🚀 Testing patient PDF viewer flow...')
    
    // Navigate to exam edit page
    const examUrl = 'http://localhost:3000/exams/6ad25b5e-ec75-4656-acdb-b60db4ec63a5/edit'
    await page.goto(examUrl, { waitUntil: 'networkidle0' })
    
    console.log('📋 Step 1: Page loaded, waiting for questions to load...')
    
    // Wait for questions to load by looking for console log
    let questionsLoaded = false
    let retries = 0
    while (!questionsLoaded && retries < 20) {
      await new Promise(resolve => setTimeout(resolve, 500))
      const content = await page.content()
      questionsLoaded = content.includes('7 questions') || content.includes('Total Questions: 7')
      retries++
    }
    
    if (!questionsLoaded) {
      console.log('❌ Questions did not load in time')
      await page.screenshot({ path: 'error-questions-not-loaded.png' })
      return false
    }
    
    console.log('✅ Questions appear to be loaded')
    
    // Click Questions tab
    console.log('📋 Step 2: Clicking Questions tab...')
    await page.evaluate(() => {
      const questionsTab = Array.from(document.querySelectorAll('button')).find(btn => 
        btn.textContent.includes('Questions')
      )
      if (questionsTab) questionsTab.click()
    })
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Wait patiently for Configure with PDF button
    console.log('📋 Step 3: Waiting patiently for Configure with PDF button...')
    
    let configureButtonFound = false
    let attempts = 0
    while (!configureButtonFound && attempts < 30) {
      configureButtonFound = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button'))
        return buttons.some(btn => 
          btn.textContent.includes('Configure with PDF') && 
          !btn.disabled
        )
      })
      
      if (!configureButtonFound) {
        await new Promise(resolve => setTimeout(resolve, 500))
        attempts++
        
        // Debug: Check what buttons are available
        if (attempts % 5 === 0) {
          const availableButtons = await page.evaluate(() => {
            return Array.from(document.querySelectorAll('button')).map(btn => ({
              text: btn.textContent?.substring(0, 50),
              disabled: btn.disabled
            }))
          })
          console.log(`   Attempt ${attempts}: Available buttons:`, availableButtons.slice(0, 5))
        }
      }
    }
    
    if (!configureButtonFound) {
      console.log('❌ Configure with PDF button not found after 15 seconds')
      await page.screenshot({ path: 'error-no-configure-button-final.png' })
      
      // Final debug: What's in the Questions tab?
      const questionsTabContent = await page.evaluate(() => {
        return document.querySelector('[role="tabpanel"]')?.textContent?.substring(0, 500) || 'No tab panel found'
      })
      console.log('📊 Questions tab content:', questionsTabContent)
      
      return false
    }
    
    console.log('✅ Configure with PDF button found!')
    
    // Click Configure with PDF
    console.log('📋 Step 4: Clicking Configure with PDF...')
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'))
      const configureButton = buttons.find(btn => 
        btn.textContent.includes('Configure with PDF') && 
        !btn.disabled
      )
      if (configureButton) configureButton.click()
    })
    
    // Wait for split screen
    console.log('📋 Step 5: Waiting for split screen...')
    const splitScreenLoaded = await waitForText(page, 'Exam PDF', 10000)
    
    if (splitScreenLoaded) {
      console.log('✅ Split screen opened!')
      
      // Check for errors
      await new Promise(resolve => setTimeout(resolve, 2000))
      const hasError = await page.evaluate(() => {
        return document.body.textContent.includes('Bucket not found') || 
               document.body.textContent.includes('404')
      })
      
      await page.screenshot({ path: 'final-split-screen-result.png', fullPage: true })
      
      if (hasError) {
        console.log('❌ Still showing bucket/404 errors in split screen')
        return false
      } else {
        console.log('✅ No errors found in split screen!')
        return true
      }
    } else {
      console.log('❌ Split screen did not load')
      await page.screenshot({ path: 'error-split-screen-timeout.png' })
      return false
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message)
    await page.screenshot({ path: 'test-error-patient.png' })
    return false
    
  } finally {
    await new Promise(resolve => setTimeout(resolve, 3000))
    await browser.close()
  }
}

testPatientFlow().then(success => {
  if (success) {
    console.log('\\n🟢 PATIENT FLOW TEST PASSED!')
    console.log('✅ PDF viewer is working correctly')
  } else {
    console.log('\\n🔴 PATIENT FLOW TEST FAILED!')
  }
})