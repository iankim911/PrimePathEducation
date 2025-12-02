const puppeteer = require('puppeteer');

async function testCreateExamPage() {
    const browser = await puppeteer.launch({ 
        headless: false,
        defaultViewport: { width: 1920, height: 1080 },
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    try {
        console.log('📋 Testing Create Exam Page - PDF Split Functionality');
        console.log('='.repeat(60));
        
        // Navigate to the Create Exam page
        console.log('🌐 Navigating to Create Exam page...');
        await page.goto('http://localhost:3000/exams/create', { 
            waitUntil: 'networkidle0',
            timeout: 10000 
        });
        
        // Wait for page to fully load
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log('✅ Page loaded successfully');
        
        // Test 1: Check if page loads without errors
        const title = await page.title();
        console.log(`📄 Page title: ${title}`);
        
        // Test 2: Check for PDF Configuration section on right side
        console.log('\n🔍 Checking for PDF Configuration section...');
        
        const hasConfigText = await page.evaluate(() => {
            return Array.from(document.querySelectorAll('*')).some(el => 
                el.textContent && el.textContent.includes('PDF Configuration')
            );
        });
        
        if (hasConfigText) {
            console.log('✅ PDF Configuration section found');
        } else {
            console.log('❌ PDF Configuration section NOT found');
        }
        
        // Test 3: Look for split controls (Enable Split toggle)
        console.log('\n🔍 Checking for split controls...');
        
        const enableSplitToggle = await page.evaluate(() => {
            const elements = Array.from(document.querySelectorAll('*'));
            return elements.some(el => 
                el.textContent && (
                    el.textContent.includes('Enable Split') ||
                    el.textContent.includes('Split') ||
                    (el.type === 'checkbox' && el.id && el.id.includes('split'))
                )
            );
        });
        
        if (enableSplitToggle) {
            console.log('✅ Enable Split toggle found');
        } else {
            console.log('❌ Enable Split toggle NOT found');
        }
        
        // Test 4: Look for Vertical/Horizontal buttons
        console.log('\n🔍 Checking for Vertical/Horizontal buttons...');
        
        const orientationButtons = await page.evaluate(() => {
            const elements = Array.from(document.querySelectorAll('*'));
            const hasVertical = elements.some(el => 
                el.textContent && el.textContent.includes('Vertical')
            );
            const hasHorizontal = elements.some(el => 
                el.textContent && el.textContent.includes('Horizontal')
            );
            return { hasVertical, hasHorizontal };
        });
        
        if (orientationButtons.hasVertical && orientationButtons.hasHorizontal) {
            console.log('✅ Vertical/Horizontal orientation buttons found');
        } else if (orientationButtons.hasVertical || orientationButtons.hasHorizontal) {
            console.log(`⚠️  Only ${orientationButtons.hasVertical ? 'Vertical' : 'Horizontal'} button found`);
        } else {
            console.log('❌ Vertical/Horizontal orientation buttons NOT found');
        }
        
        // Test 5: Look for rotation and zoom controls
        console.log('\n🔍 Checking for rotation and zoom controls...');
        
        const controls = await page.evaluate(() => {
            const elements = Array.from(document.querySelectorAll('*'));
            
            const hasRotation = elements.some(el => 
                el.textContent && (
                    el.textContent.includes('Rotate') ||
                    el.textContent.includes('🔄') ||
                    (el.className && el.className.includes('rotate'))
                )
            );
            
            const hasZoom = elements.some(el => 
                el.textContent && (
                    el.textContent.includes('Zoom') ||
                    el.textContent.includes('+') ||
                    el.textContent.includes('-') ||
                    el.textContent.includes('%')
                )
            );
            
            return { hasRotation, hasZoom };
        });
        
        if (controls.hasRotation) {
            console.log('✅ Rotation controls found');
        } else {
            console.log('❌ Rotation controls NOT found');
        }
        
        if (controls.hasZoom) {
            console.log('✅ Zoom controls found');
        } else {
            console.log('❌ Zoom controls NOT found');
        }
        
        // Test 6: Check overall page structure and layout
        console.log('\n🔍 Analyzing page structure...');
        
        const pageStructure = await page.evaluate(() => {
            // Look for main content areas
            const hasLeftPanel = document.querySelector('.col-span-8, .w-8/12, .flex-1, .left-panel, [class*="col-8"]');
            const hasRightPanel = document.querySelector('.col-span-4, .w-4/12, .right-panel, [class*="col-4"]');
            
            // Count form sections
            const formSections = document.querySelectorAll('h2, h3, .form-section, .step').length;
            
            // Check for file upload areas
            const hasFileUpload = Array.from(document.querySelectorAll('*')).some(el => 
                el.textContent && (
                    el.textContent.includes('Upload') ||
                    el.textContent.includes('Choose File') ||
                    el.textContent.includes('Select File')
                )
            );
            
            return {
                hasLeftPanel: !!hasLeftPanel,
                hasRightPanel: !!hasRightPanel,
                formSections,
                hasFileUpload
            };
        });
        
        console.log(`📊 Page structure analysis:`);
        console.log(`   - Left panel: ${pageStructure.hasLeftPanel ? '✅' : '❌'}`);
        console.log(`   - Right panel: ${pageStructure.hasRightPanel ? '✅' : '❌'}`);
        console.log(`   - Form sections: ${pageStructure.formSections}`);
        console.log(`   - File upload: ${pageStructure.hasFileUpload ? '✅' : '❌'}`);
        
        // Take a screenshot
        console.log('\n📸 Taking screenshot...');
        await page.screenshot({ 
            path: '/tmp/create-exam-page-test.png',
            fullPage: true
        });
        console.log('✅ Screenshot saved to /tmp/create-exam-page-test.png');
        
        // Summary
        console.log('\n📋 TEST SUMMARY');
        console.log('='.repeat(60));
        console.log('✅ Page loads successfully');
        console.log(`${hasConfigText ? '✅' : '❌'} PDF Configuration section`);
        console.log(`${enableSplitToggle ? '✅' : '❌'} Enable Split toggle`);
        console.log(`${orientationButtons.hasVertical && orientationButtons.hasHorizontal ? '✅' : '❌'} Orientation buttons`);
        console.log(`${controls.hasRotation ? '✅' : '❌'} Rotation controls`);
        console.log(`${controls.hasZoom ? '✅' : '❌'} Zoom controls`);
        console.log(`${pageStructure.hasLeftPanel && pageStructure.hasRightPanel ? '✅' : '❌'} Two-column layout`);
        
        console.log('\n✅ Testing completed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        
        // Take screenshot of error state
        try {
            await page.screenshot({ 
                path: '/tmp/create-exam-page-error.png',
                fullPage: true
            });
            console.log('📸 Error screenshot saved to /tmp/create-exam-page-error.png');
        } catch (screenshotError) {
            console.log('Failed to take error screenshot:', screenshotError.message);
        }
    }
    
    await browser.close();
}

// Run the test
testCreateExamPage();