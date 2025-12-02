const puppeteer = require('puppeteer');

async function simpleTest() {
    const browser = await puppeteer.launch({ 
        headless: false,
        defaultViewport: { width: 1920, height: 1080 },
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    try {
        console.log('🔍 Simple test of Create Exam page...');
        
        await page.goto('http://localhost:3000/exams/create', { 
            waitUntil: 'networkidle0',
            timeout: 10000 
        });
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Take screenshot
        await page.screenshot({ 
            path: '/tmp/create-exam-final.png',
            fullPage: true
        });
        
        console.log('✅ Screenshot taken successfully');
        
        // Check for key elements
        const elements = await page.evaluate(() => {
            const hasTitle = document.title;
            const hasPdfConfig = document.body.textContent.includes('PDF Configuration');
            const hasSplit = document.body.textContent.includes('Enable Split');
            const hasZoom = document.body.textContent.includes('100%') || document.body.textContent.includes('Zoom');
            const hasRotation = document.body.textContent.includes('Rotation');
            const hasUpload = document.body.textContent.includes('Upload');
            
            return { hasTitle, hasPdfConfig, hasSplit, hasZoom, hasRotation, hasUpload };
        });
        
        console.log('📊 Element check results:');
        console.log(`   Page title: ${elements.hasTitle}`);
        console.log(`   PDF Configuration: ${elements.hasPdfConfig ? '✅' : '❌'}`);
        console.log(`   Enable Split: ${elements.hasSplit ? '✅' : '❌'}`);
        console.log(`   Zoom controls: ${elements.hasZoom ? '✅' : '❌'}`);
        console.log(`   Rotation controls: ${elements.hasRotation ? '✅' : '❌'}`);
        console.log(`   Upload functionality: ${elements.hasUpload ? '✅' : '❌'}`);
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
    
    await browser.close();
}

simpleTest();