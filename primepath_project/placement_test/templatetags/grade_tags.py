from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Split a string by delimiter and return a list
    Usage: {{ value|split:',' }}
    
    For multiple short answers:
    - If delimiter is ',' and value contains '|', use '|' instead
    - This handles mixed data formats in the database
    """
    if value is None:
        return []
    
    # Convert to string
    value_str = str(value)
    
    # For SHORT answer fields, if looking for commas but only pipes exist, use pipes
    if delimiter == ',' and '|' in value_str and ',' not in value_str:
        delimiter = '|'
    
    # Split and clean
    parts = [item.strip() for item in value_str.split(delimiter)]
    
    # Filter out empty parts
    return [part for part in parts if part]

@register.filter
def has_multiple_answers(question):
    """
    Check if a question has multiple answer fields
    Returns True if it should show multiple input fields
    Works for SHORT, LONG, and MIXED question types
    """
    if not question:
        return False
    
    # Handle SHORT questions
    if question.question_type == 'SHORT':
        # Check options_count first
        if hasattr(question, 'options_count') and question.options_count > 1:
            return True
        
        # Also check correct_answer field for separators
        if hasattr(question, 'correct_answer') and question.correct_answer:
            answer = str(question.correct_answer)
            # Check for multiple answers indicated by separators
            # Note: '|' could mean alternatives OR multiple fields depending on context
            # If options_count > 1, then '|' means multiple fields
            # Otherwise '|' means alternatives
            if ',' in answer or (question.options_count > 1 and '|' in answer):
                return True
    
    # Handle LONG questions  
    elif question.question_type == 'LONG':
        # LONG questions with options_count > 1 have multiple response areas
        if hasattr(question, 'options_count') and question.options_count > 1:
            return True
        
        # Also check for triple pipe separator
        if hasattr(question, 'correct_answer') and question.correct_answer:
            answer = str(question.correct_answer)
            if '|||' in answer:
                parts = answer.split('|||')
                return len(parts) > 1
    
    # Handle MIXED questions
    elif question.question_type == 'MIXED':
        # MIXED questions with options_count > 1 have multiple components
        if hasattr(question, 'options_count') and question.options_count > 1:
            return True
        
        # Also check the JSON structure if available
        if hasattr(question, 'correct_answer') and question.correct_answer:
            try:
                import json
                parsed = json.loads(question.correct_answer)
                # Count short answer components
                short_count = sum(1 for item in parsed if item.get('type') == 'Short Answer')
                return short_count > 1
            except:
                pass
    
    return False

@register.filter
def get_answer_letters(question):
    """
    Get the answer letters for a multiple answer question
    Returns a list of letters like ['B', 'C'] or ['A', 'B', 'C']
    Works for SHORT, LONG, and MIXED question types
    
    Priority: Always use options_count if available for consistency
    """
    if not question:
        return []
    
    # SHORT, LONG, and MIXED questions can have multiple letter-based inputs
    if question.question_type not in ['SHORT', 'LONG', 'MIXED']:
        return []
    
    # CRITICAL FIX: If options_count is 0 or 1, return empty list
    # Single input questions don't need letter labels
    if hasattr(question, 'options_count'):
        if question.options_count <= 1:
            return []
        # For options_count > 1, return that many letters
        letters = "ABCDEFGHIJ"
        return list(letters[:question.options_count])
    
    # Legacy fallback for questions without options_count
    # (This should rarely be reached in modern data)
    if not question.correct_answer:
        return []
    
    answer = str(question.correct_answer)
    
    # Try to extract letter answers
    # Check if answer contains letter format (B,C or B|C)
    import re
    
    # Pattern for single letters separated by comma or pipe
    pattern = r'^[A-Ja-j](?:[,|][A-Ja-j])*$'
    if re.match(pattern, answer.replace(' ', '')):
        # It's letter format
        if ',' in answer:
            parsed_letters = [l.strip().upper() for l in answer.split(',')]
        elif '|' in answer:
            parsed_letters = [l.strip().upper() for l in answer.split('|')]
        else:
            parsed_letters = []
        
        return parsed_letters
    
    # Not letter format, check for separators to determine count
    if ',' in answer:
        count = len(answer.split(','))
    elif '|' in answer:
        # Only treat pipe as separator if it's clearly multiple values
        # not alternatives like "cat|feline"
        parts = answer.split('|')
        # If all parts look like numbers or very short, likely multiple values
        if all(part.strip().isdigit() or len(part.strip()) <= 3 for part in parts):
            count = len(parts)
        else:
            # Likely alternatives, not multiple answers
            return []
    else:
        return []
    
    letters = "ABCDEFGHIJ"
    return list(letters[:count])

@register.filter
def is_mixed_question(question):
    """Check if a question is MIXED type"""
    return question and question.question_type == 'MIXED'

@register.filter
def get_mixed_components(question):
    """
    Get the components of a MIXED question
    Returns a list of dicts with 'type', 'value', and 'index' for each component
    
    Important: If options_count > 1, we prioritize showing text inputs
    regardless of the JSON structure, to match user expectations from control panel
    """
    if not question or question.question_type != 'MIXED':
        return []
    
    # ALWAYS use options_count if available to determine number of inputs
    # This ensures consistency with what the control panel shows
    if hasattr(question, 'options_count') and question.options_count > 1:
        components = []
        letters = "ABCDEFGHIJ"
        
        # Check if we have JSON data to determine component types
        has_json_data = False
        json_components = []
        
        if hasattr(question, 'correct_answer') and question.correct_answer:
            try:
                import json
                parsed = json.loads(question.correct_answer)
                has_json_data = True
                
                # Count how many are Short Answer vs MCQ
                short_count = sum(1 for item in parsed if item.get('type') == 'Short Answer')
                mcq_count = sum(1 for item in parsed if item.get('type') == 'Multiple Choice')
                
                # Process components based on their actual types in JSON
                for i, item in enumerate(parsed):
                    if i >= question.options_count:
                        break  # Don't exceed options_count
                    
                    component_type = item.get('type', '')
                    
                    if component_type == 'Multiple Choice':
                        # Parse the value to get selected options
                        value = item.get('value', '')
                        selected_options = [opt.strip() for opt in value.split(',') if opt.strip()]
                        
                        # Use the question's options_count to determine available options
                        # For MIXED questions, MCQ components should respect the options_count
                        num_options = min(question.options_count, 10) if hasattr(question, 'options_count') else 5
                        available_options = list("ABCDEFGHIJ"[:num_options])
                        
                        # Create MCQ checkbox group
                        components.append({
                            'type': 'mcq',
                            'letter': letters[i] if i < len(letters) else str(i),
                            'index': i,
                            'options': available_options,  # Dynamic options based on question.options_count
                            'selected': selected_options,
                            'value': value
                        })
                    elif component_type == 'Long Answer':
                        # Long Answer - use textarea
                        components.append({
                            'type': 'textarea',
                            'letter': letters[i] if i < len(letters) else str(i),
                            'index': i,
                            'value': item.get('value', '')
                        })
                    else:
                        # Short Answer or unknown type - use text input
                        components.append({
                            'type': 'input',
                            'letter': letters[i] if i < len(letters) else str(i),
                            'index': i
                        })
            except:
                pass
        
        # If no JSON data or parsing failed, create text inputs based on options_count
        if not components:
            for i in range(question.options_count):
                components.append({
                    'type': 'input',
                    'letter': letters[i] if i < len(letters) else str(i),
                    'index': i
                })
        
        return components
    
    # Fallback for questions without options_count
    return []

@register.filter
def format_grade(grade):
    """Format grade number to Korean school system format"""
    try:
        grade = int(grade)
        if 1 <= grade <= 6:
            return f"Primary {grade}"
        elif 7 <= grade <= 9:
            return f"Middle School {grade - 6}"
        elif 10 <= grade <= 12:
            return f"High School {grade - 9}"
        else:
            return f"Grade {grade}"
    except (ValueError, TypeError):
        return str(grade)