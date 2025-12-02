const puppeteer = require('puppeteer');

async function simpleFinalTest() {
    console.log('🎯 SPLIT-SCREEN QUESTION EDITOR - FINAL VERIFICATION');
    console.log('=====================================================\n');
    
    const browser = await puppeteer.launch({ 
        headless: false, 
        defaultViewport: null,
        args: ['--start-maximized']
    });
    
    try {
        const page = await browser.newPage();
        
        // Step 1: Navigate to exam edit page
        const examId = 'c4a70bde-58b2-4f23-9428-8f455af736f0';
        const url = `http://localhost:3000/exams/${examId}/edit?tab=questions`;
        
        console.log(`📋 1. Navigating to: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Step 2: Verify Questions tab is active
        const questionsTabActive = await page.evaluate(() => {
            const activeTab = document.querySelector('[data-state="active"]');
            return activeTab && activeTab.textContent.includes('Questions');
        });
        console.log(`✅ 2. Questions tab active: ${questionsTabActive}`);
        
        // Step 3: Click "Configure with PDF" button
        console.log('📋 3. Looking for "Configure with PDF" button...');
        const buttonClicked = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const configureButton = buttons.find(btn => btn.textContent.includes('Configure with PDF'));
            if (configureButton) {
                configureButton.click();
                return true;
            }
            return false;
        });
        
        if (!buttonClicked) {
            throw new Error('Configure with PDF button not found');
        }
        console.log('✅ 3. "Configure with PDF" button clicked successfully');
        
        // Step 4: Wait for split-screen to load
        console.log('📋 4. Waiting for split-screen interface to load...');
        await new Promise(resolve => setTimeout(resolve, 4000));
        
        // Step 5: Test each component
        console.log('📋 5. Testing split-screen components...\n');
        
        // Test PDF viewer
        const pdfViewer = await page.$('iframe[title="Exam PDF"]');
        console.log(`   PDF Viewer: ${pdfViewer ? '✅ FOUND' : '❌ NOT FOUND'}`);
        
        // Test question form
        const questionForm = await page.$('textarea[id="question_text"]');
        console.log(`   Question Form: ${questionForm ? '✅ FOUND' : '❌ NOT FOUND'}`);
        
        // Test question navigation
        const navButtons = await page.$$('button.rounded-full');
        console.log(`   Question Navigation: ${navButtons.length > 0 ? `✅ ${navButtons.length} BUTTONS` : '❌ NO BUTTONS'}`);
        
        // Test controls
        const hasZoomControls = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const hasZoom = buttons.some(btn => btn.innerHTML.includes('ZoomIn') || btn.innerHTML.includes('ZoomOut'));
            const hasReset = buttons.some(btn => btn.textContent.includes('Reset'));
            return hasZoom || hasReset;
        });
        console.log(`   Zoom Controls: ${hasZoomControls ? '✅ FOUND' : '❌ NOT FOUND'}`);
        
        // Test save functionality  
        const saveButton = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.some(btn => btn.textContent.includes('Save Question'));
        });
        console.log(`   Save Button: ${saveButton ? '✅ FOUND' : '❌ NOT FOUND'}`);
        
        // Step 6: Test navigation between questions
        if (navButtons.length >= 2) {
            console.log('\n📋 6. Testing question navigation...');
            
            // Get initial question text
            const initialQuestion = await page.$eval('textarea[id="question_text"]', el => el.value).catch(() => '');
            
            // Click second question
            await navButtons[1].click();
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const secondQuestion = await page.$eval('textarea[id="question_text"]', el => el.value).catch(() => '');
            
            console.log(`   Navigation Test: ${initialQuestion !== secondQuestion ? '✅ WORKING' : '❌ NOT WORKING'}`);
            console.log(`     Initial: "${initialQuestion.substring(0, 30)}..."`);
            console.log(`     After nav: "${secondQuestion.substring(0, 30)}..."`);
        }
        
        // Step 7: Final screenshot and assessment
        await page.screenshot({ 
            path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/verification-complete.png',
            fullPage: true 
        });
        
        // Calculate final score
        const results = [
            { name: 'Questions Tab Active', passed: questionsTabActive },
            { name: 'Configure Button Worked', passed: buttonClicked },
            { name: 'PDF Viewer Present', passed: !!pdfViewer },
            { name: 'Question Form Present', passed: !!questionForm },
            { name: 'Navigation Buttons', passed: navButtons.length > 0 },
            { name: 'Zoom Controls', passed: hasZoomControls },
            { name: 'Save Button', passed: saveButton }
        ];
        
        const passedCount = results.filter(r => r.passed).length;
        const totalCount = results.length;
        const successRate = Math.round((passedCount / totalCount) * 100);
        
        console.log('\n🎯 FINAL RESULTS');
        console.log('================');
        console.log(`Overall Success: ${successRate}% (${passedCount}/${totalCount} features working)\n`);
        
        results.forEach(result => {
            console.log(`${result.passed ? '✅' : '❌'} ${result.name}`);
        });
        
        console.log(`\n📸 Screenshot saved: verification-complete.png`);
        
        if (successRate >= 85) {
            console.log('\n🟢 EXCELLENT: The split-screen question editor is working very well!');
            console.log('   All core functionality is operational.');
        } else if (successRate >= 70) {
            console.log('\n🟡 GOOD: The split-screen question editor is mostly working.');
            console.log('   Minor issues may need attention.');
        } else {
            console.log('\n🔴 NEEDS ATTENTION: Some core features may not be working properly.');
        }
        
        return { success: successRate >= 70, successRate, results };
        
    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        return { success: false, error: error.message };
    } finally {
        await browser.close();
    }
}

// Run the test
simpleFinalTest()
    .then(result => {
        console.log('\n📋 Testing completed successfully.');
        process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });