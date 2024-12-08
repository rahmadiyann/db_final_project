#!/bin/sh

echo "Updating npm..."
npm install -g npm@10.9.2

echo "Installing dependencies..."
npm install --legacy-peer-deps

echo "Building Next.js application..."
npm run build

echo "Starting Next.js application..."
exec npm start

