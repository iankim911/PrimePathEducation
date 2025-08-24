#!/usr/bin/env python3
"""
Copy Exam Modal Final Fix Test
Tests the comprehensive copy exam modal functionality
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_copy_exam_functionality():
    """Test the Copy Exam modal functionality end-to-end"""
    print("=" * 60)
    print("COPY EXAM MODAL COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Step 1: Navigate to login page
        print("\n1. Navigating to login page...")
        driver.get("http://127.0.0.1:8000/RoutineTest/login/")
        time.sleep(2)
        
        # Step 2: Login as teacher1
        print("2. Logging in as teacher1...")
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("teacher1")
        password_field.send_keys("teacher1")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        login_button.click()
        
        # Wait for redirect
        time.sleep(3)
        
        # Step 3: Navigate to Exam Library
        print("3. Navigating to Exam Library...")
        driver.get("http://127.0.0.1:8000/RoutineTest/exams/library/")
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        
        # Step 4: Check if Copy Exam buttons exist
        print("4. Checking for Copy Exam buttons...")
        copy_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn-copy, button[onclick*='openCopyModal']")
        
        if not copy_buttons:
            print("❌ No Copy Exam buttons found on the page")
            # Let's check what buttons exist
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(all_buttons)} buttons total:")
            for i, btn in enumerate(all_buttons[:10]):  # Show first 10
                try:
                    print(f"  Button {i+1}: {btn.text} | class={btn.get_attribute('class')} | onclick={btn.get_attribute('onclick')}")
                except:
                    print(f"  Button {i+1}: [unable to read attributes]")
            return False
        
        print(f"✅ Found {len(copy_buttons)} Copy Exam buttons")
        
        # Step 5: Click the first Copy Exam button
        print("5. Clicking first Copy Exam button...")
        first_copy_button = copy_buttons[0]
        
        # Get exam details from button attributes
        onclick_attr = first_copy_button.get_attribute('onclick')
        print(f"   Button onclick: {onclick_attr}")
        
        # Click the button
        driver.execute_script("arguments[0].click();", first_copy_button)
        time.sleep(2)
        
        # Step 6: Check if modal opens
        print("6. Checking if Copy Modal opens...")
        try:
            modal = wait.until(EC.presence_of_element_located((By.ID, "copyExamModal")))
            modal_style = modal.get_attribute('style')
            modal_display = driver.execute_script("return window.getComputedStyle(arguments[0]).display", modal)
            
            print(f"   Modal found: {modal is not None}")
            print(f"   Modal style: {modal_style}")  
            print(f"   Modal display: {modal_display}")
            
            if modal_display == 'none':
                print("❌ Modal exists but is not visible (display: none)")
                return False
            else:
                print("✅ Modal is visible")
                
        except TimeoutException:
            print("❌ Modal not found or did not appear")
            return False
        
        # Step 7: Check modal content
        print("7. Checking modal content...")
        
        # Check for form elements
        form_elements = {
            'sourceExamId': driver.find_elements(By.ID, "sourceExamId"),
            'sourceExamName': driver.find_elements(By.ID, "sourceExamName"),
            'copyProgramSelect': driver.find_elements(By.ID, "copyProgramSelect"),
            'copySubprogramSelect': driver.find_elements(By.ID, "copySubprogramSelect"),
            'copyLevelSelect': driver.find_elements(By.ID, "copyLevelSelect"),
            'copyExamForm': driver.find_elements(By.ID, "copyExamForm")
        }
        
        for element_id, elements in form_elements.items():
            if elements:
                print(f"   ✅ {element_id}: Found")
                if element_id == 'copyProgramSelect':
                    # Check if dropdown is populated
                    select_element = Select(elements[0])
                    options = select_element.options
                    print(f"      Program dropdown has {len(options)} options:")
                    for opt in options[:5]:  # Show first 5 options
                        print(f"        - {opt.text} (value: {opt.get_attribute('value')})")
            else:
                print(f"   ❌ {element_id}: Not found")
        
        # Step 8: Test dropdown functionality
        print("8. Testing dropdown functionality...")
        try:
            program_select = Select(driver.find_element(By.ID, "copyProgramSelect"))
            
            # Get available programs
            program_options = [opt for opt in program_select.options if opt.get_attribute('value')]
            
            if program_options:
                print(f"   Found {len(program_options)} program options")
                
                # Select first program
                first_program = program_options[0]
                print(f"   Selecting program: {first_program.text}")
                program_select.select_by_value(first_program.get_attribute('value'))
                
                # Wait for subprogram dropdown to populate
                time.sleep(2)
                
                # Check subprogram dropdown
                try:
                    subprogram_select = Select(driver.find_element(By.ID, "copySubprogramSelect"))
                    subprogram_options = [opt for opt in subprogram_select.options if opt.get_attribute('value')]
                    print(f"   Subprogram dropdown populated with {len(subprogram_options)} options")
                    
                    if subprogram_options:
                        # Select first subprogram
                        first_subprogram = subprogram_options[0]
                        print(f"   Selecting subprogram: {first_subprogram.text}")
                        subprogram_select.select_by_value(first_subprogram.get_attribute('value'))
                        
                        # Wait for level dropdown to populate
                        time.sleep(2)
                        
                        # Check level dropdown
                        try:
                            level_select = Select(driver.find_element(By.ID, "copyLevelSelect"))
                            level_options = [opt for opt in level_select.options if opt.get_attribute('value')]
                            print(f"   Level dropdown populated with {len(level_options)} options")
                            
                            if level_options:
                                print("✅ Dropdown cascade functionality working!")
                            else:
                                print("❌ Level dropdown not populated")
                                
                        except NoSuchElementException:
                            print("❌ Level dropdown not found")
                    else:
                        print("❌ Subprogram dropdown not populated")
                        
                except NoSuchElementException:
                    print("❌ Subprogram dropdown not found")
            else:
                print("❌ No program options available")
                
        except NoSuchElementException:
            print("❌ Program dropdown not found")
        
        # Step 9: Check console for JavaScript errors
        print("9. Checking browser console...")
        try:
            logs = driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if js_errors:
                print(f"❌ Found {len(js_errors)} JavaScript errors:")
                for error in js_errors:
                    print(f"   - {error['message']}")
            else:
                print("✅ No JavaScript errors found")
                
        except Exception as e:
            print(f"   Unable to check console logs: {e}")
        
        # Step 10: Close modal
        print("10. Closing modal...")
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, "#copyExamModal .modal-close, #copyExamModal .close")
            close_button.click()
            time.sleep(1)
            print("✅ Modal closed successfully")
        except NoSuchElementException:
            print("❌ Close button not found")
        
        print("\n" + "=" * 60)
        print("✅ COPY EXAM MODAL TEST COMPLETED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    success = test_copy_exam_functionality()
    exit(0 if success else 1)