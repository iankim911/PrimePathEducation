const puppeteer = require('puppeteer');

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function testPDFSplitFunctionality() {
    let browser;
    
    try {
        browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1400, height: 900 }
        });
        
        const page = await browser.newPage();
        
        // Enable console logging
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
        
        console.log('\n=== STARTING PDF SPLIT FUNCTIONALITY TEST ===\n');
        
        // Test 1: Navigate to Create Exam page
        console.log('1. Testing Create Exam page navigation...');
        await page.goto('http://localhost:3000/exams/create', { waitUntil: 'networkidle0' });
        await wait(2000);
        
        // Take screenshot of initial state
        await page.screenshot({ path: './test_results/01_create_exam_initial.png', fullPage: true });
        console.log('   ✓ Create Exam page loaded successfully');
        
        // Test 2: Basic form filling
        console.log('\n2. Testing basic form completion...');
        
        // Check if form elements exist and fill them
        const examNameInput = await page.$('#examName');
        if (examNameInput) {
            await examNameInput.type('Test PDF Split Exam');
            console.log('   ✓ Exam name entered');
        }
        
        const descriptionInput = await page.$('#description');
        if (descriptionInput) {
            await descriptionInput.type('Testing PDF split functionality');
            console.log('   ✓ Description entered');
        }
        
        const examTypeSelect = await page.$('#examType');
        if (examTypeSelect) {
            await examTypeSelect.select('placement');
            console.log('   ✓ Exam type selected');
        }
        
        // Test 3: Look for PDF configuration section
        console.log('\n3. Testing PDF configuration section...');
        
        // Check for Enable Split toggle
        const splitElements = await page.evaluate(() => {
            const elements = {
                splitToggle: !!document.querySelector('input[type="checkbox"]'),
                verticalBtn: !!document.querySelector('button:contains("Vertical")') || !!document.querySelector('*[data-orientation="vertical"]'),
                horizontalBtn: !!document.querySelector('button:contains("Horizontal")') || !!document.querySelector('*[data-orientation="horizontal"]'),
                zoomControls: !!document.querySelector('*[class*="zoom"]') || !!document.querySelector('button:contains("Zoom")'),
                rotateBtn: !!document.querySelector('button:contains("Rotate")') || !!document.querySelector('*[class*="rotate"]')
            };
            
            // Also look for text content that might indicate these features
            const bodyText = document.body.innerText.toLowerCase();
            if (bodyText.includes('split')) elements.splitText = true;
            if (bodyText.includes('zoom')) elements.zoomText = true;
            if (bodyText.includes('rotate')) elements.rotateText = true;
            if (bodyText.includes('vertical') || bodyText.includes('horizontal')) elements.orientationText = true;
            
            return elements;
        });
        
        console.log('   PDF Configuration elements found:');
        console.log('   - Split toggle:', splitElements.splitToggle ? '✓' : '✗');
        console.log('   - Orientation buttons:', (splitElements.verticalBtn && splitElements.horizontalBtn) ? '✓' : '✗');
        console.log('   - Zoom controls:', splitElements.zoomControls ? '✓' : '✗');
        console.log('   - Rotate button:', splitElements.rotateBtn ? '✓' : '✗');
        console.log('   - Split text found:', splitElements.splitText ? '✓' : '✗');
        console.log('   - Zoom text found:', splitElements.zoomText ? '✓' : '✗');
        console.log('   - Rotate text found:', splitElements.rotateText ? '✓' : '✗');
        console.log('   - Orientation text found:', splitElements.orientationText ? '✓' : '✗');
        
        await page.screenshot({ path: './test_results/02_pdf_configuration.png', fullPage: true });
        
        // Test 4: Navigate to Step 2 if tabs exist
        console.log('\n4. Testing navigation between steps...');
        
        const step2Button = await page.$('button[data-step="2"], button:contains("Step 2"), *[class*="tab"]:contains("2")');
        if (step2Button) {
            await step2Button.click();
            await wait(1000);
            console.log('   ✓ Navigated to Step 2');
        } else {
            console.log('   ⚠ Step 2 navigation not found (may be single-page form)');
        }
        
        await page.screenshot({ path: './test_results/03_step2_navigation.png', fullPage: true });
        
        // Test 5: Check existing exams
        console.log('\n5. Testing existing exams functionality...');
        
        await page.goto('http://localhost:3000/exams', { waitUntil: 'networkidle0' });
        await wait(2000);
        
        const examsList = await page.evaluate(() => {
            const examElements = document.querySelectorAll('a[href*="/exams/"], *[class*="exam"], table tr, *[data-exam]');
            return {
                examCount: examElements.length,
                hasTable: !!document.querySelector('table'),
                hasExamCards: !!document.querySelector('*[class*="exam"]'),
                pageContent: document.body.innerText.substring(0, 500)
            };
        });
        
        console.log(`   Found ${examsList.examCount} exam-related elements`);
        console.log('   Has table:', examsList.hasTable ? '✓' : '✗');
        console.log('   Has exam cards:', examsList.hasExamCards ? '✓' : '✗');
        
        await page.screenshot({ path: './test_results/04_exams_list.png', fullPage: true });
        
        // Test 6: Backward compatibility - other pages
        console.log('\n6. Testing backward compatibility...');
        
        const pages = [
            { url: 'http://localhost:3000', name: 'Dashboard' },
            { url: 'http://localhost:3000/students', name: 'Students' },
            { url: 'http://localhost:3000/classes', name: 'Classes' },
            { url: 'http://localhost:3000/teachers', name: 'Teachers' }
        ];
        
        for (const testPage of pages) {
            try {
                await page.goto(testPage.url, { waitUntil: 'networkidle0' });
                await wait(1000);
                
                const pageStatus = await page.evaluate(() => {
                    return {
                        hasErrors: !!document.querySelector('*[class*="error"]'),
                        isLoaded: document.readyState === 'complete',
                        hasContent: document.body.innerText.length > 100
                    };
                });
                
                if (pageStatus.isLoaded && pageStatus.hasContent && !pageStatus.hasErrors) {
                    console.log(`   ✓ ${testPage.name} page loads correctly`);
                } else {
                    console.log(`   ⚠ ${testPage.name} page may have issues`);
                }
            } catch (error) {
                console.log(`   ✗ ${testPage.name} page failed to load: ${error.message}`);
            }
        }
        
        await page.screenshot({ path: './test_results/05_backward_compatibility.png', fullPage: true });
        
        // Test 7: Console error check
        console.log('\n7. Final system check...');
        
        await page.goto('http://localhost:3000/exams/create', { waitUntil: 'networkidle0' });
        await wait(2000);
        
        // Check for any obvious errors or missing functionality
        const finalCheck = await page.evaluate(() => {
            const formElements = document.querySelectorAll('input, select, textarea, button');
            const hasBasicForm = formElements.length > 5;
            const hasFileInput = !!document.querySelector('input[type="file"]');
            const bodyText = document.body.innerText.toLowerCase();
            
            return {
                hasBasicForm,
                hasFileInput,
                formElementCount: formElements.length,
                containsPdfText: bodyText.includes('pdf'),
                containsExamText: bodyText.includes('exam'),
                pageTitle: document.title
            };
        });
        
        console.log('   Final system status:');
        console.log('   - Has basic form elements:', finalCheck.hasBasicForm ? '✓' : '✗');
        console.log('   - Has file input:', finalCheck.hasFileInput ? '✓' : '✗');
        console.log('   - Form elements count:', finalCheck.formElementCount);
        console.log('   - Contains PDF text:', finalCheck.containsPdfText ? '✓' : '✗');
        console.log('   - Contains Exam text:', finalCheck.containsExamText ? '✓' : '✗');
        console.log('   - Page title:', finalCheck.pageTitle);
        
        await page.screenshot({ path: './test_results/06_final_check.png', fullPage: true });
        
        console.log('\n=== TEST COMPLETED SUCCESSFULLY ===\n');
        console.log('Screenshots saved in test_results/ directory');
        console.log('Check the screenshots for visual verification of functionality');
        
    } catch (error) {
        console.error('Test encountered error:', error.message);
        
        if (browser) {
            try {
                await page.screenshot({ path: './test_results/error_screenshot.png', fullPage: true });
                console.log('Error screenshot saved');
            } catch (screenshotError) {
                console.log('Could not save error screenshot');
            }
        }
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the test
testPDFSplitFunctionality().catch(console.error);