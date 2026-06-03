#!/bin/bash
# Generate TypeScript types from backend OpenAPI spec
# Usage: ./scripts/generate-types.sh [backend_url]

BACKEND_URL="${1:-http://localhost:8000}"
OUTPUT="src/types/api-generated.ts"

echo "Fetching OpenAPI spec from $BACKEND_URL/openapi.json..."
npx openapi-typescript "$BACKEND_URL/openapi.json" -o "$OUTPUT"
echo "Types generated to $OUTPUT"