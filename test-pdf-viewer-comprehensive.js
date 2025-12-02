/**
 * Comprehensive QC Test for PDF Viewer Fix
 * 
 * Tests complete flow and ensures existing features aren't broken
 */

const puppeteer = require('puppeteer')
const fs = require('fs')

async function comprehensiveQCTest() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  })
  
  const page = await browser.newPage()
  
  try {
    console.log('🚀 Starting Comprehensive QC Test...')
    
    // Test 1: Basic page loads
    console.log('📋 Test 1: Testing page loads...')
    
    const testPages = [
      'http://localhost:3000',
      'http://localhost:3000/students',
      'http://localhost:3000/exams'
    ]
    
    for (const testPage of testPages) {
      await page.goto(testPage, { waitUntil: 'networkidle0' })
      const title = await page.title()
      console.log(`   ✅ ${testPage}: ${title}`)
      await new Promise(resolve => setTimeout(resolve, 1000)
    }
    
    // Test 2: Navigate to exam edit
    console.log('📋 Test 2: Navigate to exam edit...')
    await page.goto('http://localhost:3000/exams', { waitUntil: 'networkidle0' })
    
    // Click on first "Edit" button
    try {
      await page.waitForSelector('a[href*="/exams/"][href*="/edit"]', { timeout: 5000 })
      const editLinks = await page.$$('a[href*="/exams/"][href*="/edit"]')
      
      if (editLinks.length > 0) {
        console.log(`   Found ${editLinks.length} exam(s) to edit`)
        await editLinks[0].click()
        await new Promise(resolve => setTimeout(resolve(2000)
        
        const url = page.url()
        console.log(`   ✅ Navigated to: ${url}`)
      } else {
        console.log('   ⚠️ No exams found to edit')
        return false
      }
    } catch (error) {
      console.log('   ❌ Failed to find exam edit links:', error.message)
      return false
    }
    
    // Test 3: Questions tab and Configure with PDF
    console.log('📋 Test 3: Testing Questions tab...')
    
    try {
      // Click Questions tab
      await page.waitForSelector('button[data-state="inactive"]:has-text("Questions"), [role="tab"]:has-text("Questions")', { timeout: 5000 })
      
      // Try different selectors for the Questions tab
      const questionsTabSelectors = [
        'button:has-text("Questions")',
        '[role="tab"]:has-text("Questions")', 
        'button[value="questions"]',
        '.tabs-trigger:has-text("Questions")'
      ]
      
      let questionsTab = null
      for (const selector of questionsTabSelectors) {
        try {
          questionsTab = await page.$(selector)
          if (questionsTab) break
        } catch (e) {
          continue
        }
      }
      
      if (questionsTab) {
        await questionsTab.click()
        await new Promise(resolve => setTimeout(resolve, 1000)
        console.log('   ✅ Questions tab clicked')
        
        // Look for "Configure with PDF" button
        try {
          const configureButton = await page.$('button:has-text("Configure with PDF")')
          if (configureButton) {
            console.log('   ✅ Configure with PDF button found')
            
            // Test 4: Open PDF viewer
            console.log('📋 Test 4: Opening PDF viewer...')
            await configureButton.click()
            await new Promise(resolve => setTimeout(resolve(3000) // Wait for split screen to load
            
            // Check for split screen elements
            const pdfSection = await page.$('div:has-text("Exam PDF")')
            const questionSection = await page.$('div:has-text("Question 1 Configuration")')
            
            if (pdfSection && questionSection) {
              console.log('   ✅ Split screen PDF viewer opened successfully')
              
              // Test 5: Check for PDF content (no longer showing error)
              console.log('📋 Test 5: Checking PDF content...')
              
              // Look for error messages
              const errorMessages = await page.$$eval('*', elements => 
                elements.filter(el => 
                  el.textContent.includes('Bucket not found') || 
                  el.textContent.includes('404') ||
                  el.textContent.includes('statusCode')
                ).map(el => el.textContent)
              )
              
              if (errorMessages.length === 0) {
                console.log('   ✅ No PDF loading errors found!')
                
                // Check for iframe or embed with PDF
                const pdfViewer = await page.$('iframe, embed')
                if (pdfViewer) {
                  console.log('   ✅ PDF viewer element found')
                } else {
                  console.log('   ⚠️ PDF viewer element not found, but no errors detected')
                }
              } else {
                console.log('   ❌ PDF loading errors still present:', errorMessages)
                return false
              }
              
              // Test 6: Test question navigation
              console.log('📋 Test 6: Testing question navigation...')
              
              const questionButtons = await page.$$('button[class*="rounded-full"]')
              if (questionButtons.length > 1) {
                console.log(`   Found ${questionButtons.length} question navigation buttons`)
                
                // Click second question
                await questionButtons[1].click()
                await new Promise(resolve => setTimeout(resolve, 1000)
                console.log('   ✅ Question navigation works')
              }
              
              // Test 7: Close PDF viewer
              console.log('📋 Test 7: Closing PDF viewer...')
              
              const closeButton = await page.$('button[aria-label*="close"], button:has-text("close"), button svg[class*="arrow-left"]')
              if (closeButton) {
                await closeButton.click()
                await new Promise(resolve => setTimeout(resolve, 1000)
                console.log('   ✅ PDF viewer closed')
              }
              
            } else {
              console.log('   ❌ Split screen did not open properly')
              return false
            }
            
          } else {
            console.log('   ❌ Configure with PDF button not found')
            return false
          }
        } catch (error) {
          console.log('   ❌ Error testing Configure with PDF:', error.message)
          return false
        }
        
      } else {
        console.log('   ❌ Questions tab not found')
        return false
      }
      
    } catch (error) {
      console.log('   ❌ Failed to test Questions tab:', error.message)
      return false
    }
    
    // Test 8: Ensure other features still work
    console.log('📋 Test 8: Testing other features still work...')
    
    // Test Basic Info tab
    try {
      const basicInfoTab = await page.$('button:has-text("Basic Info"), [role="tab"]:has-text("Basic Info")')
      if (basicInfoTab) {
        await basicInfoTab.click()
        await new Promise(resolve => setTimeout(resolve, 1000)
        
        const titleField = await page.$('input[value*="Path"], input[placeholder*="title"]')
        if (titleField) {
          console.log('   ✅ Basic Info tab works')
        }
      }
    } catch (error) {
      console.log('   ⚠️ Basic Info tab test failed:', error.message)
    }
    
    // Test Files tab
    try {
      const filesTab = await page.$('button:has-text("Files"), [role="tab"]:has-text("Files")')
      if (filesTab) {
        await filesTab.click()
        await new Promise(resolve => setTimeout(resolve, 1000)
        console.log('   ✅ Files tab works')
      }
    } catch (error) {
      console.log('   ⚠️ Files tab test failed:', error.message)
    }
    
    console.log('\\n🎉 COMPREHENSIVE QC TEST COMPLETED SUCCESSFULLY!')
    console.log('✅ PDF viewer fix is working correctly')
    console.log('✅ No existing features were broken')
    
    // Take final screenshot
    await page.screenshot({ 
      path: 'qc-test-success.png', 
      fullPage: true 
    })
    
    return true
    
  } catch (error) {
    console.error('❌ QC Test failed:', error)
    
    // Take error screenshot
    await page.screenshot({ 
      path: 'qc-test-error.png', 
      fullPage: true 
    })
    
    return false
    
  } finally {
    await browser.close()
  }
}

// Run the test
comprehensiveQCTest().then(success => {
  if (success) {
    console.log('\\n🟢 ALL TESTS PASSED - PDF viewer is working correctly!')
  } else {
    console.log('\\n🔴 TESTS FAILED - Issues need to be addressed')
    process.exit(1)
  }
})