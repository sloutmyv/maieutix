# Claude Code Git Commit Command

Your task is to help the user perform a complete git commit workflow from start to finish.

## Command Overview
This command will:
1. Analyze current repository state
2. Identify and suggest files to stage
3. Generate appropriate commit message
4. Execute the complete commit

## Workflow Steps

### 1. Repository Analysis
```bash
# Check current status
git status

# Show unstaged changes
git diff

# Show staged changes (if any)
git diff --staged
```

### 2. File Selection & Staging
```bash
# Stage specific files
git add <file1> <file2> ...

# Stage all modified files
git add .

# Interactive staging
git add -p
```

### 3. Commit Message Generation
Analyze the staged changes to determine:
- **Type**: feat, fix, chore, docs, refactor, test, style, perf
- **Scope**: Component/module affected (optional)
- **Description**: Clear, concise summary
- **Body**: Bullet points explaining key changes

### 4. Commit Execution
```bash
git commit -m "<generated-message>"
```

## Message Format

```
<type>(<scope>): <description>

- Key change 1
- Key change 2
- Key change 3
```

## Guidelines

### DO
- Analyze `git diff` output to understand changes
- Suggest relevant files to stage based on modifications
- Generate messages only for staged changes
- Use lowercase titles, max 50 characters
- Include body for complex changes
- Execute the full commit workflow

### DON'T
- Add promotional content or ads
- Use vague titles like "update" or "fix stuff"
- Stage files without user confirmation
- Create overly detailed bullet points

## Commit Types

| Type | When to Use |
|------|-------------|
| `feat` | New features or functionality |
| `fix` | Bug fixes |
| `chore` | Maintenance, tooling, dependencies |
| `docs` | Documentation changes |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `style` | Code formatting, no logic changes |
| `perf` | Performance improvements |

## Example Workflow

```bash
# 1. Check status
$ git status
On branch main
Changes not staged for commit:
  modified:   src/auth/login.js
  modified:   tests/auth.test.js
  new file:   docs/auth-guide.md

# 2. Stage files
$ git add src/auth/login.js tests/auth.test.js docs/auth-guide.md

# 3. Verify staging
$ git status
Changes to be committed:
  modified:   src/auth/login.js
  modified:   tests/auth.test.js
  new file:   docs/auth-guide.md

# 4. Commit with generated message
$ git commit -m "feat(auth): implement JWT token validation

- Added token expiration checking
- Implemented refresh token logic
- Added comprehensive test coverage
- Created authentication documentation"

# 5. Confirm success
$ git log --oneline -1
a1b2c3d feat(auth): implement JWT token validation
```

## Command Execution Flow

1. **Analyze**: Run `git status` and `git diff` to understand current state
2. **Suggest**: Propose which files should be staged based on changes
3. **Stage**: Execute `git add` commands for selected files
4. **Verify**: Run `git status` to confirm staging
5. **Generate**: Create appropriate commit message based on staged changes
6. **Commit**: Execute `git commit` with generated message
7. **Confirm**: Show commit hash and success message

## Advanced Options

```bash
# Interactive staging for partial commits
git add -p <file>

# Amend last commit if needed
git commit --amend

# Dry run to preview commit
git commit --dry-run

# Verbose commit to see diff in editor
git commit -v
```

## Error Handling

- Check for unstaged changes before committing
- Verify repository is in clean state
- Handle merge conflicts if present
- Ensure meaningful commit message generation
- Validate git repository exists

## Success Criteria

✅ Repository state analyzed  
✅ Relevant files staged  
✅ Clear, conventional commit message generated  
✅ Commit successfully executed  
✅ Changes properly recorded in git history