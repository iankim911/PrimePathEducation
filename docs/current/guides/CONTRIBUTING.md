# Contributing to PrimePath

Thank you for your interest in contributing to PrimePath! We welcome contributions from the community and are grateful for any help you can provide.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Commit Guidelines](#commit-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Testing](#testing)
9. [Documentation](#documentation)
10. [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Prioritize the project's best interests

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing private information without consent
- Any conduct that could be considered inappropriate in a professional setting

## Getting Started

1. **Fork the Repository**: Click the "Fork" button on GitHub
2. **Clone Your Fork**: 
   ```bash
   git clone https://github.com/your-username/PrimePath.git
   cd PrimePath
   ```
3. **Add Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/PrimePath.git
   ```
4. **Keep Your Fork Updated**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix reported issues
- **Features**: Implement new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize code performance
- **UI/UX**: Enhance user interface and experience
- **Translations**: Add language support

### Finding Issues to Work On

- Check the [Issues](https://github.com/original-owner/PrimePath/issues) page
- Look for labels:
  - `good first issue` - Great for newcomers
  - `help wanted` - Community help needed
  - `bug` - Bug fixes
  - `enhancement` - New features
  - `documentation` - Documentation improvements

### Creating Issues

Before creating an issue:
1. Search existing issues to avoid duplicates
2. Use the appropriate issue template
3. Provide clear and detailed information

#### Bug Report Template

```markdown
**Description**
A clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Python Version: [e.g., 3.9.5]
- Django Version: [e.g., 5.0.1]
```

#### Feature Request Template

```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
Describe your solution

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Any other relevant information
```

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment tool (venv, virtualenv)
- PostgreSQL (for production setup)
- Redis (optional, for caching)

### Local Development

1. **Setup Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

4. **Database Setup**:
   ```bash
   cd primepath_project
   python manage.py migrate --settings=primepath_project.settings_sqlite
   python manage.py createsuperuser --settings=primepath_project.settings_sqlite
   ```

5. **Run Development Server**:
   ```bash
   python manage.py runserver --settings=primepath_project.settings_sqlite
   ```

## Coding Standards

### Python (PEP 8)

```python
# Good
def calculate_score(answers, answer_key):
    """
    Calculate the test score based on answers and answer key.
    
    Args:
        answers (list): Student's answers
        answer_key (dict): Correct answers
        
    Returns:
        int: Total score
    """
    score = 0
    for question_num, answer in enumerate(answers, 1):
        if answer == answer_key.get(question_num):
            score += 1
    return score

# Bad
def calc(a,ak):
    s=0
    for i,ans in enumerate(a,1):
        if ans==ak.get(i):s+=1
    return s
```

### JavaScript (ES6+)

```javascript
// Good
class ExamManager {
    constructor(examId) {
        this.examId = examId;
        this.questions = [];
        this.currentQuestion = 1;
    }
    
    async loadQuestions() {
        try {
            const response = await fetch(`/api/exams/${this.examId}/questions/`);
            this.questions = await response.json();
        } catch (error) {
            console.error('Failed to load questions:', error);
            throw error;
        }
    }
}

// Bad
function exam_mgr(id) {
    var self = this;
    self.id = id;
    self.q = [];
}
```

### CSS (BEM Methodology)

```css
/* Good */
.exam-card {
    padding: 1rem;
    border-radius: 0.5rem;
}

.exam-card__title {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.exam-card__button--primary {
    background-color: var(--primary-color);
}

/* Bad */
.examCard {
    padding: 1rem;
}

.examCard h2 {
    font-size: 1.5rem;
}
```

### HTML (Semantic)

```html
<!-- Good -->
<article class="exam-card">
    <header class="exam-card__header">
        <h2 class="exam-card__title">Placement Test</h2>
    </header>
    <section class="exam-card__content">
        <p>Test description...</p>
    </section>
    <footer class="exam-card__footer">
        <button class="btn btn--primary">Start Test</button>
    </footer>
</article>

<!-- Bad -->
<div class="card">
    <div class="top">
        <span class="title">Placement Test</span>
    </div>
    <div>Test description...</div>
    <div class="bottom">
        <div class="button">Start Test</div>
    </div>
</div>
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```bash
# Good
git commit -m "feat(exam): add audio file support for questions"
git commit -m "fix(auth): resolve login redirect issue"
git commit -m "docs(api): update endpoint documentation"

# Bad
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "update"
```

## Pull Request Process

### Before Submitting

1. **Update Your Branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run Tests**:
   ```bash
   python manage.py test
   ```

3. **Check Code Quality**:
   ```bash
   # Python
   flake8 .
   black --check .
   
   # JavaScript
   npm run lint
   ```

4. **Update Documentation**: If needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console.log() statements
- [ ] No commented code
- [ ] No breaking changes

## Screenshots (if applicable)
```

### Review Process

1. **Automatic Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one maintainer reviews
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves
5. **Merge**: PR is merged to main branch

## Testing

### Writing Tests

#### Python/Django Tests

```python
from django.test import TestCase
from placement_test.models import Exam

class ExamModelTest(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create(
            name="Test Exam",
            time_limit=120
        )
    
    def test_exam_creation(self):
        self.assertEqual(self.exam.name, "Test Exam")
        self.assertEqual(self.exam.time_limit, 120)
    
    def test_exam_str_representation(self):
        self.assertEqual(str(self.exam), "Test Exam")
```

#### JavaScript Tests

```javascript
describe('ExamManager', () => {
    let examManager;
    
    beforeEach(() => {
        examManager = new ExamManager(1);
    });
    
    test('should initialize with correct exam ID', () => {
        expect(examManager.examId).toBe(1);
    });
    
    test('should load questions successfully', async () => {
        // Mock fetch
        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve([{id: 1, text: 'Question 1'}])
            })
        );
        
        await examManager.loadQuestions();
        expect(examManager.questions).toHaveLength(1);
    });
});
```

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test placement_test

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# JavaScript tests
npm test
npm run test:coverage
```

## Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Include parameter descriptions and return types
- Add inline comments for complex logic
- Update README.md for significant changes

### API Documentation

- Document all endpoints in API.md
- Include request/response examples
- Specify authentication requirements
- List possible error codes

### User Documentation

- Update user guides for UI changes
- Add screenshots when helpful
- Keep language clear and simple
- Test instructions by following them

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: support@primepath.com (for sensitive issues)

### Getting Help

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Create a new issue if needed

### Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## Development Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# ... edit files ...

# 3. Stage changes
git add .

# 4. Commit with meaningful message
git commit -m "feat(module): add new feature"

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Create Pull Request on GitHub
```

### Bug Fixes

```bash
# 1. Create bugfix branch
git checkout -b fix/issue-description

# 2. Fix the bug
# ... edit files ...

# 3. Add tests to prevent regression
# ... write tests ...

# 4. Commit
git commit -m "fix(module): resolve issue #123"

# 5. Push and create PR
git push origin fix/issue-description
```

## Resources

### Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [JavaScript Standard Style](https://standardjs.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Learning Resources

- Django Tutorial: Official Django tutorial
- MDN Web Docs: Web development documentation
- Real Python: Python tutorials and articles

## Questions?

If you have questions about contributing:
1. Check this guide
2. Search existing issues/discussions
3. Ask in GitHub Discussions
4. Contact maintainers

Thank you for contributing to PrimePath! 🎉

---

**Contributing Guide Version**: 1.0.0 | **Last Updated**: August 13, 2025