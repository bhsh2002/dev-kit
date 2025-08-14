# GitHub Packages Publishing Troubleshooting Guide

## Issue: 404 Error when publishing to GitHub Packages

The error you're encountering is typically caused by one or more of the following issues:

### 1. Repository URL Configuration

**Problem**: The repository URL in your configuration is missing a trailing slash.

**Solution**: Update your configuration files:

#### In `pyproject.toml`:
```toml
[[tool.poetry.source]]
name = "github"
url = "https://pypi.pkg.github.com/bhsh2002/"
priority = "supplemental"
```

#### In GitHub Actions workflow (`.github/workflows/publish.yml`):
```yaml
- name: Configure Poetry for GitHub Packages
  run: |
    poetry config repositories.github https://pypi.pkg.github.com/${{ github.repository_owner }}/
    poetry config http-basic.github __token__ ${{ secrets.GITHUB_TOKEN }}
```

#### In setup script (`setup_github_packages.sh`):
```bash
poetry config repositories.github https://pypi.pkg.github.com/bhsh2002/
```

### 2. GitHub Token Permissions

**Problem**: The GitHub token doesn't have the required permissions.

**Solution**: Ensure your GitHub token has the following scopes:
- `write:packages` - Required for publishing packages
- `read:packages` - Required for reading package metadata
- `repo` - Required if the repository is private

**Steps to create a proper token**:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select the required scopes
4. Copy the token and use it in your configuration

### 3. Repository Visibility

**Problem**: If your repository is private, the token needs additional permissions.

**Solution**: 
- Make sure the token has `repo` scope for private repositories
- Or make the repository public if you want the package to be publicly accessible

### 4. Package Name Conflicts

**Problem**: The package name might conflict with existing packages.

**Solution**: 
- Check if the package name `dev-kit` is already taken
- Consider using a more unique name like `bhsh2002-dev-kit` or `personal-dev-kit`

### 5. Authentication Configuration

**Problem**: The authentication is not properly configured.

**Solution**: Verify your authentication setup:

```bash
# Check current configuration
poetry config --list | grep github

# Reconfigure if needed
poetry config repositories.github https://pypi.pkg.github.com/bhsh2002/
poetry config http-basic.github __token__ YOUR_GITHUB_TOKEN
```

### 6. Testing the Configuration

Before publishing, test your configuration:

```bash
# Build the package
poetry build

# Check the built files
ls -la dist/

# Test publishing with dry-run (if available)
poetry publish --repository github --dry-run
```

### 7. Alternative Repository URL Format

If the above doesn't work, try using the repository-specific URL:

```bash
poetry config repositories.github https://pypi.pkg.github.com/bhsh2002/dev-kit/
```

### 8. Debugging Steps

1. **Check the exact error**: The 404 error suggests the URL is not found
2. **Verify the repository exists**: Make sure the GitHub repository exists and is accessible
3. **Test the URL manually**: Try accessing the URL in a browser to see if it exists
4. **Check GitHub Packages settings**: Ensure GitHub Packages is enabled for your repository

### 9. Common Solutions

1. **Use the correct repository URL format**:
   - `https://pypi.pkg.github.com/OWNER/` (for user/organization packages)
   - `https://pypi.pkg.github.com/OWNER/REPO/` (for repository-specific packages)

2. **Ensure proper authentication**:
   - Use `__token__` as the username
   - Use your GitHub token as the password

3. **Check package visibility**:
   - Public repositories create public packages by default
   - Private repositories require proper token permissions

### 10. Final Configuration

After making the changes, your final configuration should look like:

```toml
# pyproject.toml
[[tool.poetry.source]]
name = "github"
url = "https://pypi.pkg.github.com/bhsh2002/"
priority = "supplemental"
```

```yaml
# .github/workflows/publish.yml
- name: Configure Poetry for GitHub Packages
  run: |
    poetry config repositories.github https://pypi.pkg.github.com/${{ github.repository_owner }}/
    poetry config http-basic.github __token__ ${{ secrets.GITHUB_TOKEN }}
```

Try these solutions in order, and the 404 error should be resolved.