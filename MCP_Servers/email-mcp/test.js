#!/usr/bin/env node

/**
 * Test script for Email MCP Server
 *
 * Tests all available tools in dry-run mode.
 */

import { spawn } from 'child_process';

const server = spawn('node', ['index.js'], {
  stdio: ['pipe', 'pipe', 'inherit'],
  env: { ...process.env, DRY_RUN: 'true' }
});

let buffer = '';

server.stdout.on('data', (data) => {
  buffer += data.toString();

  const lines = buffer.split('\n');
  buffer = lines.pop() || '';

  for (const line of lines) {
    if (!line.trim()) continue;

    try {
      const response = JSON.parse(line);
      console.log('Response:', JSON.stringify(response, null, 2));
    } catch (error) {
      console.log('Raw output:', line);
    }
  }
});

// Test sequence
const tests = [
  // 1. List available tools
  {
    method: 'tools/list',
    params: {}
  },

  // 2. Create email draft
  {
    method: 'tools/call',
    params: {
      name: 'draft_email',
      arguments: {
        to: 'test@example.com',
        subject: 'Test Email',
        body: 'This is a test email from AI Employee.',
        context: 'Testing MCP server'
      }
    }
  },

  // 3. Search emails
  {
    method: 'tools/call',
    params: {
      name: 'search_emails',
      arguments: {
        query: 'is:unread',
        maxResults: 5
      }
    }
  }
];

// Send tests sequentially
async function runTests() {
  for (let i = 0; i < tests.length; i++) {
    console.log(`\n=== Test ${i + 1}/${tests.length} ===`);
    console.log('Request:', JSON.stringify(tests[i], null, 2));

    server.stdin.write(JSON.stringify(tests[i]) + '\n');

    // Wait between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Shutdown
  setTimeout(() => {
    console.log('\n=== Tests complete ===');
    server.kill();
    process.exit(0);
  }, 2000);
}

runTests().catch(error => {
  console.error('Test error:', error);
  server.kill();
  process.exit(1);
});
