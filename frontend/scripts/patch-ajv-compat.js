#!/usr/bin/env node
/**
 * Patch nested ajv-keywords _formatLimit.js files for ajv@8 compatibility.
 * In ajv@8, ajv._formats was removed/renamed.
 * Old ajv-keywords@3.x code does: var formats = ajv._formats;
 * This crashes with: TypeError: Cannot read properties of undefined (reading 'date')
 * Fix: default to {} so format-limit keywords are silently skipped.
 */
const fs = require('fs');
const path = require('path');

const targets = [
  'node_modules/fork-ts-checker-webpack-plugin/node_modules/ajv-keywords/keywords/_formatLimit.js',
  'node_modules/babel-loader/node_modules/ajv-keywords/keywords/_formatLimit.js',
  'node_modules/file-loader/node_modules/ajv-keywords/keywords/_formatLimit.js',
];

targets.forEach((target) => {
  const fullPath = path.resolve(target);
  if (!fs.existsSync(fullPath)) {
    console.log('Skip (not found):', target);
    return;
  }
  let content = fs.readFileSync(fullPath, 'utf8');
  if (content.includes('ajv._formats || {}')) {
    console.log('Already patched:', target);
    return;
  }
  // ajv@8 removed the _formats property; default to {} to avoid TypeError
  const patched = content.replace(
    'var formats = ajv._formats;',
    'var formats = ajv._formats || {};'
  );
  if (patched !== content) {
    fs.writeFileSync(fullPath, patched);
    console.log('Patched:', target);
  } else {
    console.log('No match found in:', target);
    // Log first 200 chars to debug
    console.log('Content preview:', content.slice(0, 200));
  }
});

console.log('ajv-compat patch done.');
