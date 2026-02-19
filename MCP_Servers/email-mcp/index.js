#!/usr/bin/env node

/**
 * Email MCP Server for AI Employee
 *
 * Provides Gmail integration with approval workflow.
 * Implements Model Context Protocol for Claude Code.
 *
 * Tools:
 * - send_email: Send approved email drafts
 * - draft_email: Create email draft
 * - search_emails: Search Gmail
 * - get_email: Get email details
 * - list_labels: List Gmail labels
 */

import { google } from 'googleapis';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: join(process.cwd(), '../../AI_Employee_Vault/.env') });

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.compose'
];

const CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS_PATH ||
  join(process.cwd(), '../../AI_Employee_Vault/Watchers/credentials.json');
const TOKEN_PATH = join(__dirname, 'token.json');
const VAULT_PATH = process.env.VAULT_PATH ||
  join(process.cwd(), '../../AI_Employee_Vault');

// MCP Protocol implementation
class EmailMCPServer {
  constructor() {
    this.gmail = null;
    this.dryRun = process.env.DRY_RUN === 'true';
  }

  async initialize() {
    try {
      // Load credentials
      const credentials = JSON.parse(readFileSync(CREDENTIALS_PATH, 'utf8'));
      const { client_id, client_secret, redirect_uris } = credentials.installed || credentials.web;

      const oAuth2Client = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );

      // Load token if exists
      if (existsSync(TOKEN_PATH)) {
        const token = JSON.parse(readFileSync(TOKEN_PATH, 'utf8'));
        oAuth2Client.setCredentials(token);
      } else {
        throw new Error('Token not found. Run authenticate_gmail.py first.');
      }

      this.gmail = google.gmail({ version: 'v1', auth: oAuth2Client });

      this.log('Email MCP Server initialized successfully');
    } catch (error) {
      this.log(`Initialization error: ${error.message}`, 'error');
      throw error;
    }
  }

  log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;

    console.error(logEntry.trim());

    // Write to log file
    const logPath = join(VAULT_PATH, 'Logs', 'email-mcp.log');
    try {
      writeFileSync(logPath, logEntry, { flag: 'a' });
    } catch (err) {
      console.error(`Failed to write log: ${err.message}`);
    }
  }

  // Tool: send_email
  async sendEmail(to, subject, body, cc = null, bcc = null, attachments = []) {
    try {
      this.log(`Sending email to: ${to}, subject: "${subject}"`);

      if (this.dryRun) {
        this.log('[DRY RUN] Would send email', 'warn');
        return {
          success: true,
          messageId: 'DRY_RUN_MESSAGE_ID',
          dryRun: true,
          details: { to, subject, bodyLength: body.length }
        };
      }

      // Create email message
      const messageParts = [
        `To: ${to}`,
        subject ? `Subject: ${subject}` : '',
        cc ? `Cc: ${cc}` : '',
        bcc ? `Bcc: ${bcc}` : '',
        'Content-Type: text/html; charset=utf-8',
        '',
        body
      ];

      const message = messageParts.filter(Boolean).join('\n');
      const encodedMessage = Buffer.from(message)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

      const result = await this.gmail.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: encodedMessage
        }
      });

      this.log(`Email sent successfully. Message ID: ${result.data.id}`);

      return {
        success: true,
        messageId: result.data.id,
        threadId: result.data.threadId,
        to,
        subject
      };
    } catch (error) {
      this.log(`Failed to send email: ${error.message}`, 'error');
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Tool: draft_email
  async draftEmail(to, subject, body, context = '') {
    try {
      this.log(`Creating email draft for: ${to}`);

      const draftPath = join(VAULT_PATH, 'Pending_Approval',
        `EMAIL_DRAFT_${Date.now()}_${to.replace(/[^a-zA-Z0-9]/g, '_')}.md`);

      const draftContent = `---
type: email_draft
to: ${to}
subject: ${subject}
created: ${new Date().toISOString()}
status: pending_approval
context: ${context}
---

## Email Draft

**To:** ${to}
**Subject:** ${subject}

### Message Body

${body}

---

## To Approve
Move this file to \`/Approved\` folder to send this email.

## To Reject
Move this file to \`/Rejected\` folder to cancel.

## To Edit
Modify the message body above, then move to \`/Approved\`.
`;

      writeFileSync(draftPath, draftContent);
      this.log(`Draft created at: ${draftPath}`);

      return {
        success: true,
        draftPath,
        requiresApproval: true
      };
    } catch (error) {
      this.log(`Failed to create draft: ${error.message}`, 'error');
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Tool: search_emails
  async searchEmails(query, maxResults = 10) {
    try {
      this.log(`Searching emails: "${query}"`);

      const response = await this.gmail.users.messages.list({
        userId: 'me',
        q: query,
        maxResults
      });

      const messages = response.data.messages || [];
      this.log(`Found ${messages.length} emails`);

      return {
        success: true,
        count: messages.length,
        messages: messages.map(m => ({
          id: m.id,
          threadId: m.threadId
        }))
      };
    } catch (error) {
      this.log(`Search failed: ${error.message}`, 'error');
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Tool: get_email
  async getEmail(messageId) {
    try {
      this.log(`Fetching email: ${messageId}`);

      const response = await this.gmail.users.messages.get({
        userId: 'me',
        id: messageId,
        format: 'full'
      });

      const headers = response.data.payload.headers;
      const getHeader = (name) => headers.find(h => h.name === name)?.value || '';

      return {
        success: true,
        email: {
          id: response.data.id,
          threadId: response.data.threadId,
          from: getHeader('From'),
          to: getHeader('To'),
          subject: getHeader('Subject'),
          date: getHeader('Date'),
          snippet: response.data.snippet
        }
      };
    } catch (error) {
      this.log(`Failed to get email: ${error.message}`, 'error');
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Tool: list_labels
  async listLabels() {
    try {
      const response = await this.gmail.users.labels.list({ userId: 'me' });
      return {
        success: true,
        labels: response.data.labels.map(l => ({
          id: l.id,
          name: l.name,
          type: l.type
        }))
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // MCP Protocol handler
  async handleRequest(request) {
    const { method, params } = request;

    switch (method) {
      case 'tools/list':
        return this.listTools();

      case 'tools/call':
        return this.callTool(params);

      default:
        return {
          error: {
            code: -32601,
            message: `Method not found: ${method}`
          }
        };
    }
  }

  listTools() {
    return {
      tools: [
        {
          name: 'send_email',
          description: 'Send an email via Gmail (requires prior approval)',
          inputSchema: {
            type: 'object',
            properties: {
              to: { type: 'string', description: 'Recipient email address' },
              subject: { type: 'string', description: 'Email subject' },
              body: { type: 'string', description: 'Email body (HTML or plain text)' },
              cc: { type: 'string', description: 'CC recipients (optional)' },
              bcc: { type: 'string', description: 'BCC recipients (optional)' }
            },
            required: ['to', 'subject', 'body']
          }
        },
        {
          name: 'draft_email',
          description: 'Create email draft for approval',
          inputSchema: {
            type: 'object',
            properties: {
              to: { type: 'string' },
              subject: { type: 'string' },
              body: { type: 'string' },
              context: { type: 'string', description: 'Why this email is needed' }
            },
            required: ['to', 'subject', 'body']
          }
        },
        {
          name: 'search_emails',
          description: 'Search Gmail messages',
          inputSchema: {
            type: 'object',
            properties: {
              query: { type: 'string', description: 'Gmail search query' },
              maxResults: { type: 'number', default: 10 }
            },
            required: ['query']
          }
        },
        {
          name: 'get_email',
          description: 'Get email details by ID',
          inputSchema: {
            type: 'object',
            properties: {
              messageId: { type: 'string' }
            },
            required: ['messageId']
          }
        },
        {
          name: 'list_labels',
          description: 'List Gmail labels/folders',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        }
      ]
    };
  }

  async callTool(params) {
    const { name, arguments: args } = params;

    try {
      let result;
      switch (name) {
        case 'send_email':
          result = await this.sendEmail(
            args.to,
            args.subject,
            args.body,
            args.cc,
            args.bcc
          );
          break;

        case 'draft_email':
          result = await this.draftEmail(
            args.to,
            args.subject,
            args.body,
            args.context
          );
          break;

        case 'search_emails':
          result = await this.searchEmails(args.query, args.maxResults);
          break;

        case 'get_email':
          result = await this.getEmail(args.messageId);
          break;

        case 'list_labels':
          result = await this.listLabels();
          break;

        default:
          return {
            error: {
              code: -32602,
              message: `Unknown tool: ${name}`
            }
          };
      }

      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    } catch (error) {
      return {
        error: {
          code: -32603,
          message: error.message
        }
      };
    }
  }

  // Start MCP server (stdio mode)
  async start() {
    await this.initialize();

    this.log('MCP Server ready - listening on stdio');

    // Read JSON-RPC requests from stdin
    let buffer = '';
    process.stdin.on('data', async (chunk) => {
      buffer += chunk.toString();

      // Process complete JSON objects
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;

        try {
          const request = JSON.parse(line);
          const response = await this.handleRequest(request);

          // Send response to stdout
          process.stdout.write(JSON.stringify(response) + '\n');
        } catch (error) {
          this.log(`Request error: ${error.message}`, 'error');
        }
      }
    });
  }
}

// Main
const server = new EmailMCPServer();
server.start().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
