const puppeteer = require('puppeteer');

async function simplePDFTest() {
    let browser;
    
    try {
        browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1400, height: 900 }
        });
        
        const page = await browser.newPage();
        
        console.log('=== SIMPLE PDF SPLIT TEST ===\n');
        
        // Test 1: Create Exam page
        console.log('1. Loading Create Exam page...');
        await page.goto('http://localhost:3000/exams/create', { waitUntil: 'networkidle0' });
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        await page.screenshot({ path: './test_results/create_exam_page.png', fullPage: true });
        
        // Get page content
        const pageContent = await page.evaluate(() => {
            return {
                title: document.title,
                hasForm: !!document.querySelector('form'),
                inputCount: document.querySelectorAll('input').length,
                buttonCount: document.querySelectorAll('button').length,
                selectCount: document.querySelectorAll('select').length,
                bodyText: document.body.innerText.toLowerCase(),
                htmlContent: document.body.innerHTML
            };
        });
        
        console.log('Page Analysis:');
        console.log('- Title:', pageContent.title);
        console.log('- Has form:', pageContent.hasForm ? 'YES' : 'NO');
        console.log('- Input elements:', pageContent.inputCount);
        console.log('- Button elements:', pageContent.buttonCount);
        console.log('- Select elements:', pageContent.selectCount);
        console.log('- Contains "split":', pageContent.bodyText.includes('split') ? 'YES' : 'NO');
        console.log('- Contains "zoom":', pageContent.bodyText.includes('zoom') ? 'YES' : 'NO');
        console.log('- Contains "rotate":', pageContent.bodyText.includes('rotate') ? 'YES' : 'NO');
        console.log('- Contains "pdf":', pageContent.bodyText.includes('pdf') ? 'YES' : 'NO');
        
        // Test 2: Exams List page
        console.log('\n2. Loading Exams List page...');
        await page.goto('http://localhost:3000/exams', { waitUntil: 'networkidle0' });
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        await page.screenshot({ path: './test_results/exams_list_page.png', fullPage: true });
        
        const listPageContent = await page.evaluate(() => {
            return {
                title: document.title,
                hasTable: !!document.querySelector('table'),
                linkCount: document.querySelectorAll('a').length,
                bodyText: document.body.innerText
            };
        });
        
        console.log('Exams List Analysis:');
        console.log('- Title:', listPageContent.title);
        console.log('- Has table:', listPageContent.hasTable ? 'YES' : 'NO');
        console.log('- Link count:', listPageContent.linkCount);
        console.log('- Page content preview:', listPageContent.bodyText.substring(0, 200));
        
        // Test 3: Other pages for backward compatibility
        const testPages = [
            { url: 'http://localhost:3000', name: 'Dashboard' },
            { url: 'http://localhost:3000/students', name: 'Students' },
            { url: 'http://localhost:3000/classes', name: 'Classes' }
        ];
        
        console.log('\n3. Testing backward compatibility...');
        for (const testPage of testPages) {
            try {
                await page.goto(testPage.url, { waitUntil: 'networkidle0' });
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                const status = await page.evaluate(() => document.readyState);
                console.log(`- ${testPage.name}:`, status === 'complete' ? 'LOADED' : 'LOADING');
                
            } catch (error) {
                console.log(`- ${testPage.name}: ERROR - ${error.message}`);
            }
        }
        
        console.log('\n=== TEST COMPLETED ===');
        console.log('Screenshots saved in test_results/');
        
    } catch (error) {
        console.error('Test failed:', error.message);
        
        if (browser && page) {
            try {
                await page.screenshot({ path: './test_results/error.png', fullPage: true });
            } catch (e) {}
        }
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

simplePDFTest().catch(console.error);