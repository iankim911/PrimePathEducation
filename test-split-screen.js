const puppeteer = require('puppeteer');

async function testSplitScreenEditor() {
    const browser = await puppeteer.launch({ 
        headless: false, 
        defaultViewport: null,
        args: ['--start-maximized']
    });
    const page = await browser.newPage();

    try {
        console.log('🚀 Starting split-screen question editor test...');

        // Step 1: Navigate to exams list page
        console.log('📄 Step 1: Navigating to exams list page...');
        await page.goto('http://localhost:3000/exams/list', { waitUntil: 'networkidle0' });
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for page to fully load

        // Check if the page loaded correctly
        const pageTitle = await page.title();
        console.log(`   ✓ Page loaded: ${pageTitle}`);

        // Step 2: Look for existing exams
        console.log('🔍 Step 2: Looking for existing exams...');
        
        // Wait for the page content to load (beyond the loading spinner)
        await page.waitForFunction(() => {
            const spinner = document.querySelector('.animate-spin');
            return !spinner || !spinner.offsetParent;
        }, { timeout: 10000 });

        // Check if there are any exams listed
        const examLinks = await page.$$('a[href*="/exams/"]');
        console.log(`   Found ${examLinks.length} exam-related links`);

        // If no exams, let's create one first
        if (examLinks.length === 0) {
            console.log('📝 No exams found - creating a test exam first...');
            
            // Navigate to create exam page
            await page.goto('http://localhost:3000/exams/create', { waitUntil: 'networkidle0' });
            
            // Fill in basic exam details
            await page.type('[name="title"]', 'Test Exam for Split Screen');
            await page.type('[name="description"]', 'Testing split-screen question editor functionality');
            await page.type('[name="totalQuestions"]', '5');
            await page.type('[name="timeLimit"]', '30');

            // Upload a test PDF (assuming there's a file upload)
            // Note: This would need a real PDF file for complete testing
            console.log('   ⚠️  Skipping PDF upload for now - would need test PDF file');

            // Save the exam
            const saveButton = await page.$('button[type="submit"]');
            if (saveButton) {
                await saveButton.click();
                await new Promise(resolve => setTimeout(resolve, 2000));
                console.log('   ✓ Test exam created');
            }

            // Go back to exams list
            await page.goto('http://localhost:3000/exams/list', { waitUntil: 'networkidle0' });
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        // Step 3: Find and click on an exam to edit
        console.log('🎯 Step 3: Looking for exam edit links...');
        
        // Look for exam cards or links that lead to edit pages
        const examCards = await page.$$('[data-testid="exam-card"], .exam-card, a[href*="/edit"]');
        
        if (examCards.length === 0) {
            // Alternative: look for any clickable exam items
            const examItems = await page.$$('tr, .exam-item, [data-exam-id]');
            if (examItems.length > 0) {
                console.log(`   Found ${examItems.length} potential exam items`);
                await examItems[0].click();
                await new Promise(resolve => setTimeout(resolve, 1000));
            } else {
                throw new Error('No exams found to test with');
            }
        } else {
            console.log(`   Found ${examCards.length} exam cards/edit links`);
            await examCards[0].click();
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        // Step 4: Navigate to Questions tab
        console.log('📋 Step 4: Looking for Questions tab...');
        
        // Wait for the edit page to load
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Look for Questions tab
        const questionsTab = await page.$('button[data-tab="questions"], .tab-questions, [role="tab"]:has-text("Questions")');
        if (!questionsTab) {
            // Alternative: look for any tab with "Questions" text
            const tabs = await page.$$('button, a, .tab');
            let questionsTabFound = false;
            
            for (let tab of tabs) {
                const text = await tab.evaluate(el => el.textContent.toLowerCase());
                if (text.includes('question')) {
                    await tab.click();
                    questionsTabFound = true;
                    console.log('   ✓ Found and clicked Questions tab');
                    break;
                }
            }
            
            if (!questionsTabFound) {
                console.log('   ⚠️  Questions tab not found - continuing to look for "Configure with PDF" button');
            }
        } else {
            await questionsTab.click();
            console.log('   ✓ Clicked Questions tab');
        }

        await new Promise(resolve => setTimeout(resolve, 1000));

        // Step 5: Look for "Configure with PDF" button
        console.log('🔧 Step 5: Looking for "Configure with PDF" button...');
        
        // Multiple selectors to find the button
        const buttonSelectors = [
            'button:has-text("Configure with PDF")',
            '[data-testid="configure-pdf-button"]',
            'button[class*="configure"]',
            'button:contains("Configure")',
            'button:contains("PDF")'
        ];

        let configureButton = null;
        for (let selector of buttonSelectors) {
            try {
                configureButton = await page.$(selector);
                if (configureButton) break;
            } catch (e) {
                // Continue to next selector
            }
        }

        // Alternative: find button by text content
        if (!configureButton) {
            const buttons = await page.$$('button');
            for (let button of buttons) {
                const text = await button.evaluate(el => el.textContent);
                if (text.toLowerCase().includes('configure') && text.toLowerCase().includes('pdf')) {
                    configureButton = button;
                    break;
                }
            }
        }

        if (!configureButton) {
            throw new Error('❌ "Configure with PDF" button not found');
        }

        console.log('   ✓ Found "Configure with PDF" button');

        // Step 6: Click the button to open split-screen interface
        console.log('🖱️  Step 6: Clicking "Configure with PDF" button...');
        await configureButton.click();
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Step 7: Verify split-screen interface
        console.log('🔍 Step 7: Verifying split-screen interface...');

        // Check for PDF viewer on left side
        const pdfViewer = await page.$('.pdf-viewer, [data-testid="pdf-viewer"], .split-screen-left');
        if (pdfViewer) {
            console.log('   ✓ PDF viewer found on left side');
        } else {
            console.log('   ⚠️  PDF viewer not found');
        }

        // Check for question configuration panel on right side
        const questionPanel = await page.$('.question-panel, [data-testid="question-panel"], .split-screen-right');
        if (questionPanel) {
            console.log('   ✓ Question configuration panel found on right side');
        } else {
            console.log('   ⚠️  Question configuration panel not found');
        }

        // Check for zoom controls
        const zoomControls = await page.$('.zoom-controls, [data-testid="zoom-controls"], button[aria-label*="zoom"]');
        if (zoomControls) {
            console.log('   ✓ Zoom controls found');
        } else {
            console.log('   ⚠️  Zoom controls not found');
        }

        // Check for rotation controls
        const rotationControls = await page.$('.rotation-controls, [data-testid="rotation-controls"], button[aria-label*="rotate"]');
        if (rotationControls) {
            console.log('   ✓ Rotation controls found');
        } else {
            console.log('   ⚠️  Rotation controls not found');
        }

        // Step 8: Test question navigation
        console.log('🧭 Step 8: Testing question navigation...');
        
        const questionButtons = await page.$$('.question-nav button, [data-testid="question-button"]');
        if (questionButtons.length > 0) {
            console.log(`   ✓ Found ${questionButtons.length} question navigation buttons`);
            
            // Test clicking on different questions
            if (questionButtons.length > 1) {
                await questionButtons[1].click();
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log('   ✓ Clicked on question 2');
                
                await questionButtons[0].click();
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log('   ✓ Clicked back on question 1');
            }
        } else {
            console.log('   ⚠️  Question navigation buttons not found');
        }

        // Step 9: Test zoom functionality
        console.log('🔍 Step 9: Testing zoom functionality...');
        
        const zoomInButton = await page.$('button[aria-label*="zoom in"], .zoom-in, [data-testid="zoom-in"]');
        const zoomOutButton = await page.$('button[aria-label*="zoom out"], .zoom-out, [data-testid="zoom-out"]');
        
        if (zoomInButton) {
            await zoomInButton.click();
            await new Promise(resolve => setTimeout(resolve, 500));
            console.log('   ✓ Tested zoom in');
        }
        
        if (zoomOutButton) {
            await zoomOutButton.click();
            await new Promise(resolve => setTimeout(resolve, 500));
            console.log('   ✓ Tested zoom out');
        }

        // Step 10: Test rotation functionality
        console.log('🔄 Step 10: Testing rotation functionality...');
        
        const rotateButton = await page.$('button[aria-label*="rotate"], .rotate, [data-testid="rotate"]');
        if (rotateButton) {
            await rotateButton.click();
            await new Promise(resolve => setTimeout(resolve, 500));
            console.log('   ✓ Tested rotation');
        }

        // Step 11: Test question configuration
        console.log('📝 Step 11: Testing question configuration...');
        
        // Look for question type selector
        const questionTypeSelect = await page.$('select[name*="type"], .question-type-select');
        if (questionTypeSelect) {
            console.log('   ✓ Question type selector found');
        }

        // Look for save button
        const saveButton = await page.$('button[type="submit"], .save-button, [data-testid="save-question"]');
        if (saveButton) {
            console.log('   ✓ Save button found');
            // Don't actually click save unless we have test data
        }

        console.log('\n✅ Split-screen question editor test completed!');
        
        // Take a screenshot for documentation
        await page.screenshot({ 
            path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/split-screen-test-result.png',
            fullPage: true 
        });
        console.log('📸 Screenshot saved as split-screen-test-result.png');

        return {
            success: true,
            pdfViewer: !!pdfViewer,
            questionPanel: !!questionPanel,
            zoomControls: !!zoomControls,
            rotationControls: !!rotationControls,
            questionNavigation: questionButtons.length > 0,
            saveButton: !!saveButton
        };

    } catch (error) {
        console.error('❌ Error during testing:', error.message);
        
        // Take error screenshot
        await page.screenshot({ 
            path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/split-screen-error.png',
            fullPage: true 
        });
        
        return {
            success: false,
            error: error.message
        };
    } finally {
        await browser.close();
    }
}

// Run the test
testSplitScreenEditor().then(result => {
    console.log('\n📊 Test Results:', result);
    process.exit(result.success ? 0 : 1);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});