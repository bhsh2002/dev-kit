#!/bin/bash

# Setup script for configuring Poetry to work with GitHub Packages
# This script should be run locally to configure authentication

echo "Setting up Poetry for GitHub Packages..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install Poetry first."
    echo "Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Configure the GitHub Packages repository
echo "Configuring GitHub Packages repository..."
poetry config repositories.github https://pypi.pkg.github.com/bhsh2002

# Prompt for GitHub token
echo ""
echo "You need a GitHub Personal Access Token with 'write:packages' permission."
echo "To create one:"
echo "1. Go to https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Select 'write:packages' and 'read:packages' scopes"
echo "4. Copy the generated token"
echo ""
read -p "Enter your GitHub username: " github_username
read -s -p "Enter your GitHub Personal Access Token: " github_token
echo ""

# Configure authentication
poetry config http-basic.github "$github_username" "$github_token"

echo "✅ Poetry configured for GitHub Packages!"
echo ""
echo "You can now:"
echo "- Build your package: poetry build"
echo "- Publish to GitHub Packages: poetry publish --repository github"
echo ""
echo "Note: Make sure to update the version in pyproject.toml before publishing."