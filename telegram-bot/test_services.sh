#!/bin/bash
echo "=== সার্ভিস স্বাস্থ্য পরীক্ষা ==="

# Replace with your actual URLs after deployment
RAILWAY_URL="https://your-app-name.up.railway.app"
RENDER_URL="https://your-app-render.onrender.com"
CYCLIC_URL="https://your-app-cyclic.cyclic.app"
KOYEB_URL="https://your-app-koyeb.app"

# Railway check
echo "1. Railway:"
curl -s "$RAILWAY_URL/health" | grep -q "healthy" && echo "   ✓ UP" || echo "   ✗ DOWN"

# Render check
echo "2. Render:"
curl -s "$RENDER_URL/health" | grep -q "healthy" && echo "   ✓ UP" || echo "   ✗ DOWN"

# Cyclic check
echo "3. Cyclic:"
curl -s "$CYCLIC_URL/health" | grep -q "healthy" && echo "   ✓ UP" || echo "   ✗ DOWN"

# Koyeb check
echo "4. Koyeb:"
curl -s "$KOYEB_URL/health" | grep -q "healthy" && echo "   ✓ UP" || echo "   ✗ DOWN"

echo "=== পরীক্ষা সম্পন্ন ==="
