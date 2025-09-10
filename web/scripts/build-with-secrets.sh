#!/bin/bash

# Script to build the web app with Supabase secrets
# Usage: ./scripts/build-with-secrets.sh

echo "🔍 Checking for Supabase secrets..."

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL environment variable is not set"
    echo "   Please set it with: export SUPABASE_URL=your_supabase_url"
    exit 1
fi

if [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ SUPABASE_ANON_KEY environment variable is not set"
    echo "   Please set it with: export SUPABASE_ANON_KEY=your_anon_key"
    exit 1
fi

echo "✅ Supabase secrets found"
echo "   URL: ${SUPABASE_URL:0:20}..."
echo "   Key: ${SUPABASE_ANON_KEY:0:20}..."

echo "🏗️  Building web app with Supabase secrets..."

VITE_SUPABASE_URL="$SUPABASE_URL" \
VITE_SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "   Output: ./dist/"
else
    echo "❌ Build failed!"
    exit 1
fi
