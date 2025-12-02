const puppeteer = require('puppeteer');

async function generateFinalTestReport() {
    console.log('🎯 FINAL TEST REPORT: Split-Screen Question Editor');
    console.log('====================================================\n');
    
    const browser = await puppeteer.launch({ 
        headless: false, 
        defaultViewport: null,
        args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    try {
        // Navigate to exam with questions
        const examId = 'c4a70bde-58b2-4f23-9428-8f455af736f0';
        const url = `http://localhost:3000/exams/${examId}/edit?tab=questions`;
        
        console.log(`📋 Testing URL: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check Questions tab is active
        const isQuestionsTabActive = await page.evaluate(() => {
            const activeTab = document.querySelector('[data-state="active"]');
            return activeTab && activeTab.textContent.includes('Questions');
        });
        
        console.log(`✅ Questions tab active: ${isQuestionsTabActive}`);
        
        // Find and click "Configure with PDF" button
        const buttonFound = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const configureButton = buttons.find(btn => btn.textContent.includes('Configure with PDF'));
            if (configureButton) {
                configureButton.click();
                return true;
            }
            return false;
        });
        
        console.log(`✅ "Configure with PDF" button found and clicked: ${buttonFound}`);
        
        if (!buttonFound) {
            throw new Error('Configure with PDF button not found');
        }
        
        // Wait for split-screen to load
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Comprehensive component testing
        const components = await page.evaluate(() => {
            return {
                // PDF Viewer
                pdfViewer: !!document.querySelector('iframe[title="Exam PDF"]'),
                pdfContainer: !!document.querySelector('.w-1\\/2'),
                
                // Controls
                zoomInButton: !!Array.from(document.querySelectorAll('button')).find(btn => btn.innerHTML.includes('ZoomIn')),
                zoomOutButton: !!Array.from(document.querySelectorAll('button')).find(btn => btn.innerHTML.includes('ZoomOut')),
                resetButton: !!Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Reset')),
                rotateButton: !!Array.from(document.querySelectorAll('button')).find(btn => btn.innerHTML.includes('RotateCw')),
                
                // Question Navigation
                questionNavButtons: document.querySelectorAll('button.rounded-full').length,
                navigationHeader: !!document.querySelector('h2:contains("Configure Questions")'),
                questionCounter: !!document.querySelector('p:contains("Question 1 of")'),
                
                // Configuration Panel
                questionNumberInput: !!document.querySelector('input[id="question_number"]'),
                pointsInput: !!document.querySelector('input[id="points"]'),
                questionTypeSelect: !!document.querySelector('select, [role="combobox"]'),
                questionTextArea: !!document.querySelector('textarea[id="question_text"]'),
                saveButton: !!Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Save Question')),
                
                // Layout
                splitLayout: document.querySelectorAll('.w-1\\/2').length >= 2,
                headerPresent: !!document.querySelector('h2'),
                
                // Question-specific elements
                multipleChoiceOptions: document.querySelectorAll('.space-y-3 input[placeholder*="Option"]').length,
                trueFalseRadios: document.querySelectorAll('input[type="radio"][name="tf_answer"]').length
            };
        });
        
        console.log('\n📊 COMPONENT ANALYSIS:');
        console.log('====================');
        
        // Layout & Structure
        console.log('\n🏗️  Layout & Structure:');
        console.log(`   Split-screen layout: ${components.splitLayout ? '✅' : '❌'}`);
        console.log(`   PDF viewer panel: ${components.pdfViewer ? '✅' : '❌'}`);
        console.log(`   Configuration panel: ${components.questionNumberInput ? '✅' : '❌'}`);
        console.log(`   Header present: ${components.headerPresent ? '✅' : '❌'}`);
        
        // PDF Controls  
        console.log('\n🔧 PDF Controls:');
        console.log(`   Zoom In button: ${components.zoomInButton ? '✅' : '❌'}`);
        console.log(`   Zoom Out button: ${components.zoomOutButton ? '✅' : '❌'}`);
        console.log(`   Reset button: ${components.resetButton ? '✅' : '❌'}`);
        console.log(`   Rotate button: ${components.rotateButton ? '✅' : '❌'}`);
        
        // Navigation
        console.log('\n🧭 Question Navigation:');
        console.log(`   Navigation buttons: ${components.questionNavButtons} found`);
        console.log(`   Question counter: ${components.questionCounter ? '✅' : '❌'}`);
        
        // Configuration Form
        console.log('\n📝 Configuration Form:');
        console.log(`   Question number input: ${components.questionNumberInput ? '✅' : '❌'}`);
        console.log(`   Points input: ${components.pointsInput ? '✅' : '❌'}`);
        console.log(`   Question type selector: ${components.questionTypeSelect ? '✅' : '❌'}`);
        console.log(`   Question text area: ${components.questionTextArea ? '✅' : '❌'}`);
        console.log(`   Save button: ${components.saveButton ? '✅' : '❌'}`);
        
        // Question Type Testing
        console.log('\n🎯 Question Type Features:');
        console.log(`   Multiple choice options: ${components.multipleChoiceOptions} inputs`);
        console.log(`   True/False radio buttons: ${components.trueFalseRadios}`);
        
        // Test Navigation Functionality
        console.log('\n🧭 Testing Navigation Functionality:');
        const navigationTest = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button.rounded-full'));
            if (buttons.length >= 2) {
                // Click on question 2
                buttons[1].click();
                return true;
            }
            return false;
        });
        
        if (navigationTest) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Check if question 2 is now selected
            const question2Active = await page.evaluate(() => {
                const questionText = document.querySelector('textarea[id="question_text"]');
                return questionText && questionText.value.includes('True or False');
            });
            console.log(`   Navigation to Question 2: ${question2Active ? '✅' : '❌'}`);
            
            // Navigate back to question 1
            await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button.rounded-full'));
                if (buttons[0]) buttons[0].click();
            });
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const question1Active = await page.evaluate(() => {
                const questionText = document.querySelector('textarea[id="question_text"]');
                return questionText && questionText.value.includes('What is 2+2');
            });
            console.log(`   Navigation back to Question 1: ${question1Active ? '✅' : '❌'}`);
        }
        
        // Test Control Functionality
        console.log('\n🔧 Testing Control Functionality:');
        
        // Test zoom
        if (components.zoomInButton) {
            await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const zoomInBtn = buttons.find(btn => btn.innerHTML.includes('ZoomIn'));
                if (zoomInBtn) zoomInBtn.click();
            });
            await new Promise(resolve => setTimeout(resolve, 500));
            console.log('   Zoom In: ✅ Clicked');
            
            if (components.zoomOutButton) {
                await page.evaluate(() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const zoomOutBtn = buttons.find(btn => btn.innerHTML.includes('ZoomOut'));
                    if (zoomOutBtn) zoomOutBtn.click();
                });
                await new Promise(resolve => setTimeout(resolve, 500));
                console.log('   Zoom Out: ✅ Clicked');
            }
        }
        
        // Final screenshot
        await page.screenshot({ 
            path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/final-test-complete.png',
            fullPage: true 
        });
        
        // Calculate success score
        const scores = [
            components.splitLayout,
            components.pdfViewer, 
            components.questionNumberInput,
            components.questionTextArea,
            components.saveButton,
            components.zoomInButton || components.zoomOutButton,
            components.questionNavButtons > 0,
            navigationTest
        ];
        
        const successCount = scores.filter(Boolean).length;
        const successRate = Math.round((successCount / scores.length) * 100);
        
        console.log('\n🎯 FINAL ASSESSMENT:');
        console.log('===================');
        console.log(`Success Rate: ${successRate}% (${successCount}/${scores.length} features working)`);
        
        if (successRate >= 80) {
            console.log('🟢 EXCELLENT: Split-screen question editor is working very well!');
        } else if (successRate >= 60) {
            console.log('🟡 GOOD: Split-screen question editor is mostly working with minor issues');
        } else {
            console.log('🔴 NEEDS WORK: Split-screen question editor has significant issues');
        }
        
        console.log('\n📋 RECOMMENDATIONS:');
        console.log('==================');
        
        if (!components.rotateButton) {
            console.log('• Consider adding rotation controls for PDF viewing');
        }
        
        if (components.questionNavButtons < 3) {
            console.log('• Check question navigation button rendering');
        }
        
        if (!components.questionCounter) {
            console.log('• Add question counter for better UX');
        }
        
        return {
            success: successRate >= 80,
            successRate,
            components,
            navigationWorking: navigationTest
        };
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        await page.screenshot({ 
            path: '/Users/ian/Desktop/VIBECODE/PrimePath_v2/final-test-error.png' 
        }).catch(() => {});
        return { success: false, error: error.message };
    } finally {
        await browser.close();
    }
}

// Run the comprehensive test
generateFinalTestReport()
    .then(result => {
        console.log('\n📄 Test completed. Screenshots saved for review.');
        process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });