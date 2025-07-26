#!/bin/bash

# TRS Alliance Production Deployment Script
# Run this to fix the script error and deploy to production

echo "🛡️ TRS Alliance - Production Deployment"
echo "========================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo "🎨 Building Tailwind CSS..."
npx tailwindcss -i ./src/index.css -o ./dist/tailwind.css --minify

echo "⚡ Building production bundle..."
npm run build

echo "🔍 Checking build output..."
if [ -d "dist" ]; then
    echo "✅ Build successful! Files created in dist/"
    ls -la dist/
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi

echo "📤 Committing changes to Git..."
git add .
git commit -m "Fix script error: Move to Vite + local Tailwind ($(date))"

echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your site should now be live at: https://trsalliance.org"
echo "📱 Test on your phone to confirm the script error is fixed."
echo ""
echo "Next steps:"
echo "1. Visit trsalliance.org to verify the fix"
echo "2. Test Grok access at grok.com"
echo "3. Test DeepSeek access at chat.deepseek.com"
echo "4. Complete your xAI application"
