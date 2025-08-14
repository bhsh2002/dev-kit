# Publishing to GitHub Packages Guide

This guide explains how to publish your `dev-kit` package to GitHub Packages using Poetry.

## Prerequisites

1. **Poetry installed**: Make sure Poetry is installed on your system
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **GitHub Personal Access Token**: You need a token with `write:packages` and `read:packages` permissions
   - Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Select the following scopes:
     - `write:packages`
     - `read:packages`
   - Copy the generated token

## Setup Instructions

### Option 1: Automated Setup (Recommended)

Run the setup script provided in this repository:

```bash
./setup_github_packages.sh
```

This script will:
- Configure Poetry to use GitHub Packages repository
- Prompt you for your GitHub credentials
- Set up authentication

### Option 2: Manual Setup

1. **Configure the GitHub Packages repository**:
   ```bash
   poetry config repositories.github https://maven.pkg.github.com/bhsh2002/dev-kit
   ```

2. **Configure authentication**:
   ```bash
   poetry config http-basic.github YOUR_GITHUB_USERNAME YOUR_GITHUB_TOKEN
   ```

## Publishing Your Package

### Method 1: Manual Publishing

1. **Update the version** in `pyproject.toml`:
   ```toml
   [project]
   version = "0.1.1"  # Increment as needed
   ```

2. **Build the package**:
   ```bash
   poetry build
   ```

3. **Publish to GitHub Packages**:
   ```bash
   poetry publish --repository github
   ```

### Method 2: Automated Publishing via GitHub Actions

The repository includes a GitHub Action workflow that automatically publishes your package when you create a new release:

1. **Create a new release on GitHub**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag version: `v0.1.1` (or your desired version)
   - Release title: `Release 0.1.1`
   - Add release notes describing changes
   - Click "Publish release"

2. **The GitHub Action will automatically**:
   - Build your package
   - Publish it to GitHub Packages
   - Upload build artifacts

### Method 3: Manual Trigger

You can also manually trigger the publishing workflow:
- Go to your repository's "Actions" tab
- Select "Publish to GitHub Packages" workflow
- Click "Run workflow"

## Installing Your Published Package

Once published, others can install your package using:

```bash
pip install --index-url https://pypi.org/simple/ --extra-index-url https://maven.pkg.github.com/bhsh2002/dev-kit dev-kit
```

Or if using Poetry in another project:

```bash
poetry source add github https://maven.pkg.github.com/bhsh2002/dev-kit
poetry add dev-kit --source github
```

## Package Information

- **Package Name**: `dev-kit`
- **Current Version**: `0.1.0`
- **Repository**: `https://github.com/bhsh2002/dev-kit`
- **GitHub Packages URL**: `https://github.com/bhsh2002/dev-kit/packages`

## Troubleshooting

### Authentication Issues

If you get authentication errors:
1. Verify your GitHub token has the correct permissions
2. Check that your username and token are correctly configured:
   ```bash
   poetry config --list | grep github
   ```

### Version Conflicts

If you get version conflicts:
1. Make sure to increment the version in `pyproject.toml` before publishing
2. Each version can only be published once

### Package Not Found

If users can't find your package:
1. Ensure the package was published successfully (check GitHub Packages tab in your repo)
2. Verify the repository URL and package name are correct
3. Make sure users have read access to your repository

## Best Practices

1. **Version Management**: Always increment the version before publishing
2. **Release Notes**: Include comprehensive release notes with each version
3. **Testing**: Test your package build locally before publishing
4. **Security**: Never commit your GitHub token to the repository
5. **Documentation**: Keep installation instructions up to date

## Files Modified/Created

This setup created or modified the following files:
- `pyproject.toml` - Added GitHub Packages configuration and metadata
- `.github/workflows/publish.yml` - GitHub Action for automated publishing
- `setup_github_packages.sh` - Local setup script
- `PUBLISHING_GUIDE.md` - This guide

## Next Steps

1. Run the setup script: `./setup_github_packages.sh`
2. Test building your package: `poetry build`
3. Create your first release on GitHub to trigger automatic publishing
4. Share your package with others using the installation instructions above