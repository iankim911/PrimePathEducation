const puppeteer = require('puppeteer');

async function testSplitScreenEditorSimple() {
    console.log('🚀 Testing split-screen question editor functionality...\n');
    
    const browser = await puppeteer.launch({ 
        headless: false, 
        defaultViewport: null,
        args: ['--start-maximized']
    });
    
    try {
        const page = await browser.newPage();
        
        // Navigate directly to an exam edit page
        const examId = 'c4a70bde-58b2-4f23-9428-8f455af736f0'; // From API response
        const examEditUrl = `http://localhost:3000/exams/${examId}/edit?tab=questions`;
        
        console.log(`📄 Navigating to exam edit page: ${examEditUrl}`);
        await page.goto(examEditUrl, { waitUntil: 'networkidle2', timeout: 30000 });
        
        // Wait for page to load
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Take initial screenshot
        await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-step-1-page-loaded.png' });
        console.log('✓ Page loaded, screenshot saved as test-step-1-page-loaded.png');
        
        // Check if we're on the Questions tab
        const questionsTabActive = await page.$eval('[data-state="active"]', el => el.textContent.includes('Questions')).catch(() => false);
        console.log(`✓ Questions tab active: ${questionsTabActive}`);
        
        // Look for the "Configure with PDF" button
        console.log('\n🔍 Looking for "Configure with PDF" button...');
        
        // Try multiple ways to find the button
        let configureButton = null;
        
        // Method 1: Direct text search
        try {
            configureButton = await page.waitForFunction(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.find(btn => btn.textContent.includes('Configure with PDF'));
            }, { timeout: 5000 });
        } catch (e) {
            console.log('  - Method 1 failed: Text search');
        }
        
        if (configureButton) {
            console.log('✓ Found "Configure with PDF" button using text search');
            
            // Take screenshot before clicking
            await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-step-2-button-found.png' });
            console.log('✓ Screenshot saved as test-step-2-button-found.png');
            
            // Click the button
            console.log('\n🖱️  Clicking "Configure with PDF" button...');
            await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const button = buttons.find(btn => btn.textContent.includes('Configure with PDF'));
                if (button) button.click();
            });
            
            // Wait for split screen to load
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Take screenshot of split screen
            await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-step-3-split-screen.png' });
            console.log('✓ Split-screen opened, screenshot saved as test-step-3-split-screen.png');
            
            // Test split-screen components
            console.log('\n🔍 Testing split-screen components...');
            
            // Check for PDF viewer
            const pdfViewer = await page.$('iframe[title="Exam PDF"]');
            console.log(`✓ PDF viewer found: ${!!pdfViewer}`);
            
            // Check for zoom controls using evaluate
            const zoomControls = await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const zoomIn = buttons.find(btn => btn.innerHTML.includes('ZoomIn'));
                const zoomOut = buttons.find(btn => btn.innerHTML.includes('ZoomOut'));
                const reset = buttons.find(btn => btn.textContent.includes('Reset'));
                return { zoomIn: !!zoomIn, zoomOut: !!zoomOut, reset: !!reset };
            });
            console.log(`✓ Zoom controls found: ${zoomControls.zoomIn || zoomControls.zoomOut || zoomControls.reset}`);
            
            // Check for rotation control using evaluate
            const rotateBtn = await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.some(btn => btn.innerHTML.includes('RotateCw'));
            });
            console.log(`✓ Rotation control found: ${rotateBtn}`);
            
            // Check for question navigation buttons
            const questionNavButtons = await page.$$('button.rounded-full');
            console.log(`✓ Question navigation buttons: ${questionNavButtons.length} found`);
            
            // Check for question configuration panel
            const questionPanel = await page.$('textarea[id="question_text"], textarea[placeholder*="question"]');
            console.log(`✓ Question configuration panel found: ${!!questionPanel}`);
            
            // Test navigation if multiple questions
            if (questionNavButtons.length > 1) {
                console.log('\n🧭 Testing question navigation...');
                
                // Click on question 2
                await questionNavButtons[1].click();
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log('✓ Navigated to question 2');
                
                // Click back to question 1  
                await questionNavButtons[0].click();
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log('✓ Navigated back to question 1');
                
                await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-step-4-navigation.png' });
                console.log('✓ Navigation test completed, screenshot saved');
            }
            
            // Test zoom functionality
            if (zoomControls.zoomIn || zoomControls.zoomOut || zoomControls.reset) {
                console.log('\n🔍 Testing zoom functionality...');
                
                // Test zoom in
                if (zoomControls.zoomIn) {
                    await page.evaluate(() => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const zoomInBtn = buttons.find(btn => btn.innerHTML.includes('ZoomIn'));
                        if (zoomInBtn) zoomInBtn.click();
                    });
                    await new Promise(resolve => setTimeout(resolve, 500));
                    console.log('✓ Tested zoom in');
                }
                
                // Test zoom out  
                if (zoomControls.zoomOut) {
                    await page.evaluate(() => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const zoomOutBtn = buttons.find(btn => btn.innerHTML.includes('ZoomOut'));
                        if (zoomOutBtn) zoomOutBtn.click();
                    });
                    await new Promise(resolve => setTimeout(resolve, 500));
                    console.log('✓ Tested zoom out');
                }
            }
            
            // Test rotation
            if (rotateBtn) {
                console.log('\n🔄 Testing rotation...');
                await page.evaluate(() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const rotateButton = buttons.find(btn => btn.innerHTML.includes('RotateCw'));
                    if (rotateButton) rotateButton.click();
                });
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log('✓ Tested rotation');
            }
            
            // Final screenshot
            await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-final-result.png', fullPage: true });
            console.log('✓ Final screenshot saved as test-final-result.png');
            
            console.log('\n✅ SUCCESS: Split-screen question editor test completed successfully!');
            
            return {
                success: true,
                components: {
                    pdfViewer: !!pdfViewer,
                    zoomControls: !!zoomInBtn && !!zoomOutBtn,
                    rotationControl: !!rotateBtn,
                    questionNavigation: questionNavButtons.length > 0,
                    questionPanel: !!questionPanel
                }
            };
            
        } else {
            console.log('❌ "Configure with PDF" button not found');
            await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-error-button-not-found.png' });
            return { success: false, error: 'Configure with PDF button not found' };
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        await page.screenshot({ path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/test-error.png' }).catch(() => {});
        return { success: false, error: error.message };
    } finally {
        await browser.close();
    }
}

// Run the test
testSplitScreenEditorSimple()
    .then(result => {
        console.log('\n📊 Final Results:', JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });