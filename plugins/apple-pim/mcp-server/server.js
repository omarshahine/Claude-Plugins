#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SWIFT_BIN_DIR = join(__dirname, "..", "swift", ".build", "release");

// Helper to calculate relative date string from days offset
function relativeDateString(daysOffset) {
  const date = new Date();
  date.setDate(date.getDate() + daysOffset);
  return date.toISOString().split("T")[0]; // YYYY-MM-DD format
}

// Helper to run CLI commands
async function runCLI(cli, args) {
  return new Promise((resolve, reject) => {
    const cliPath = join(SWIFT_BIN_DIR, cli);
    const proc = spawn(cliPath, args);

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    proc.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    proc.on("close", (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(stdout));
        } catch {
          resolve({ success: true, output: stdout });
        }
      } else {
        reject(new Error(stderr || `CLI exited with code ${code}`));
      }
    });

    proc.on("error", (err) => {
      reject(new Error(`Failed to run CLI: ${err.message}`));
    });
  });
}

// Tool definitions
const tools = [
  // Calendar tools
  {
    name: "calendar_list",
    description: "List all calendars",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "calendar_events",
    description: "List calendar events within a date range",
    inputSchema: {
      type: "object",
      properties: {
        calendar: {
          type: "string",
          description: "Calendar name or ID to filter by (optional)",
        },
        from: {
          type: "string",
          description:
            "Start date (default: today). Accepts ISO dates or natural language like 'today', 'tomorrow'",
        },
        to: {
          type: "string",
          description: "End date (default: 7 days from start)",
        },
        lastDays: {
          type: "number",
          description:
            "Include events from N days ago (alternative to 'from'). E.g., 7 means include events from 7 days ago",
        },
        nextDays: {
          type: "number",
          description:
            "Include events up to N days in the future (alternative to 'to'). E.g., 14 means include events up to 14 days from now",
        },
        limit: {
          type: "number",
          description: "Maximum number of events (default: 100)",
        },
      },
    },
  },
  {
    name: "calendar_get",
    description: "Get a single calendar event by ID",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Event ID",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "calendar_search",
    description: "Search calendar events by title, notes, or location",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        calendar: {
          type: "string",
          description: "Calendar to search in (optional)",
        },
        from: {
          type: "string",
          description: "Start date for search range (default: 30 days ago)",
        },
        to: {
          type: "string",
          description: "End date for search range (default: 1 year from now)",
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 50)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "calendar_create",
    description: "Create a new calendar event",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Event title",
        },
        start: {
          type: "string",
          description: "Start date/time",
        },
        end: {
          type: "string",
          description: "End date/time (default: 1 hour after start)",
        },
        duration: {
          type: "number",
          description: "Duration in minutes (alternative to end)",
        },
        calendar: {
          type: "string",
          description: "Calendar name or ID (default: default calendar)",
        },
        location: {
          type: "string",
          description: "Event location",
        },
        notes: {
          type: "string",
          description: "Event notes",
        },
        allDay: {
          type: "boolean",
          description: "All-day event",
        },
        alarm: {
          type: "array",
          items: { type: "number" },
          description: "Alarm minutes before event",
        },
      },
      required: ["title", "start"],
    },
  },
  {
    name: "calendar_update",
    description: "Update an existing calendar event",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Event ID to update",
        },
        title: {
          type: "string",
          description: "New title",
        },
        start: {
          type: "string",
          description: "New start date/time",
        },
        end: {
          type: "string",
          description: "New end date/time",
        },
        location: {
          type: "string",
          description: "New location",
        },
        notes: {
          type: "string",
          description: "New notes",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "calendar_delete",
    description: "Delete a calendar event",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Event ID to delete",
        },
      },
      required: ["id"],
    },
  },

  // Reminder tools
  {
    name: "reminder_lists",
    description: "List all reminder lists",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "reminder_items",
    description: "List reminders from a list",
    inputSchema: {
      type: "object",
      properties: {
        list: {
          type: "string",
          description: "Reminder list name or ID (optional)",
        },
        completed: {
          type: "boolean",
          description: "Include completed reminders (default: false)",
        },
        lastDays: {
          type: "number",
          description:
            "Include reminders due from N days ago (for HyperContext compatibility). Note: Currently reminders are not filtered by date in the CLI",
        },
        nextDays: {
          type: "number",
          description:
            "Include reminders due up to N days in the future (for HyperContext compatibility). Note: Currently reminders are not filtered by date in the CLI",
        },
        limit: {
          type: "number",
          description: "Maximum number of reminders (default: 100)",
        },
      },
    },
  },
  {
    name: "reminder_get",
    description: "Get a single reminder by ID",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Reminder ID",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "reminder_search",
    description: "Search reminders by title or notes",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        list: {
          type: "string",
          description: "Reminder list to search in (optional)",
        },
        completed: {
          type: "boolean",
          description: "Include completed reminders (default: false)",
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 50)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "reminder_create",
    description: "Create a new reminder",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Reminder title",
        },
        list: {
          type: "string",
          description: "Reminder list name or ID (default: default list)",
        },
        due: {
          type: "string",
          description: "Due date/time",
        },
        notes: {
          type: "string",
          description: "Notes",
        },
        priority: {
          type: "number",
          description: "Priority (0=none, 1=high, 5=medium, 9=low)",
        },
        alarm: {
          type: "array",
          items: { type: "number" },
          description: "Alarm minutes before due",
        },
      },
      required: ["title"],
    },
  },
  {
    name: "reminder_complete",
    description: "Mark a reminder as complete or incomplete",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Reminder ID",
        },
        undo: {
          type: "boolean",
          description: "Mark as incomplete instead (default: false)",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "reminder_update",
    description: "Update an existing reminder",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Reminder ID to update",
        },
        title: {
          type: "string",
          description: "New title",
        },
        due: {
          type: "string",
          description: "New due date/time",
        },
        notes: {
          type: "string",
          description: "New notes",
        },
        priority: {
          type: "number",
          description: "New priority",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "reminder_delete",
    description: "Delete a reminder",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Reminder ID to delete",
        },
      },
      required: ["id"],
    },
  },

  // Contact tools
  {
    name: "contact_groups",
    description: "List all contact groups",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "contact_list",
    description: "List contacts",
    inputSchema: {
      type: "object",
      properties: {
        group: {
          type: "string",
          description: "Group name or ID to filter by (optional)",
        },
        limit: {
          type: "number",
          description: "Maximum number of contacts (default: 100)",
        },
      },
    },
  },
  {
    name: "contact_search",
    description: "Search contacts by name, email, or phone",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 50)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "contact_get",
    description:
      "Get full details for a contact, including base64-encoded photo if available",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Contact ID",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "contact_create",
    description: "Create a new contact",
    inputSchema: {
      type: "object",
      properties: {
        name: {
          type: "string",
          description: "Full name",
        },
        firstName: {
          type: "string",
          description: "First name (alternative to name)",
        },
        lastName: {
          type: "string",
          description: "Last name (alternative to name)",
        },
        email: {
          type: "string",
          description: "Email address",
        },
        phone: {
          type: "string",
          description: "Phone number",
        },
        organization: {
          type: "string",
          description: "Organization/company name",
        },
        jobTitle: {
          type: "string",
          description: "Job title",
        },
        notes: {
          type: "string",
          description: "Notes",
        },
      },
    },
  },
  {
    name: "contact_update",
    description: "Update an existing contact",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Contact ID to update",
        },
        firstName: {
          type: "string",
          description: "New first name",
        },
        lastName: {
          type: "string",
          description: "New last name",
        },
        email: {
          type: "string",
          description: "New email (replaces primary)",
        },
        phone: {
          type: "string",
          description: "New phone (replaces primary)",
        },
        organization: {
          type: "string",
          description: "New organization",
        },
        jobTitle: {
          type: "string",
          description: "New job title",
        },
        notes: {
          type: "string",
          description: "New notes",
        },
      },
      required: ["id"],
    },
  },
  {
    name: "contact_delete",
    description: "Delete a contact",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Contact ID to delete",
        },
      },
      required: ["id"],
    },
  },
];

// Tool handlers
async function handleTool(name, args) {
  const cliArgs = [];

  switch (name) {
    // Calendar tools
    case "calendar_list":
      return await runCLI("calendar-cli", ["list"]);

    case "calendar_events":
      cliArgs.push("events");
      if (args.calendar) cliArgs.push("--calendar", args.calendar);
      // Support both from/to and lastDays/nextDays
      if (args.lastDays !== undefined) {
        cliArgs.push("--from", relativeDateString(-args.lastDays));
      } else if (args.from) {
        cliArgs.push("--from", args.from);
      }
      if (args.nextDays !== undefined) {
        cliArgs.push("--to", relativeDateString(args.nextDays));
      } else if (args.to) {
        cliArgs.push("--to", args.to);
      }
      if (args.limit) cliArgs.push("--limit", String(args.limit));
      return await runCLI("calendar-cli", cliArgs);

    case "calendar_get":
      return await runCLI("calendar-cli", ["get", "--id", args.id]);

    case "calendar_search":
      cliArgs.push("search", args.query);
      if (args.calendar) cliArgs.push("--calendar", args.calendar);
      if (args.from) cliArgs.push("--from", args.from);
      if (args.to) cliArgs.push("--to", args.to);
      if (args.limit) cliArgs.push("--limit", String(args.limit));
      return await runCLI("calendar-cli", cliArgs);

    case "calendar_create":
      cliArgs.push("create", "--title", args.title, "--start", args.start);
      if (args.end) cliArgs.push("--end", args.end);
      if (args.duration) cliArgs.push("--duration", String(args.duration));
      if (args.calendar) cliArgs.push("--calendar", args.calendar);
      if (args.location) cliArgs.push("--location", args.location);
      if (args.notes) cliArgs.push("--notes", args.notes);
      if (args.allDay) cliArgs.push("--all-day");
      if (args.alarm) {
        for (const minutes of args.alarm) {
          cliArgs.push("--alarm", String(minutes));
        }
      }
      return await runCLI("calendar-cli", cliArgs);

    case "calendar_update":
      cliArgs.push("update", "--id", args.id);
      if (args.title) cliArgs.push("--title", args.title);
      if (args.start) cliArgs.push("--start", args.start);
      if (args.end) cliArgs.push("--end", args.end);
      if (args.location) cliArgs.push("--location", args.location);
      if (args.notes) cliArgs.push("--notes", args.notes);
      return await runCLI("calendar-cli", cliArgs);

    case "calendar_delete":
      return await runCLI("calendar-cli", ["delete", "--id", args.id]);

    // Reminder tools
    case "reminder_lists":
      return await runCLI("reminder-cli", ["lists"]);

    case "reminder_items":
      cliArgs.push("items");
      if (args.list) cliArgs.push("--list", args.list);
      if (args.completed) cliArgs.push("--completed");
      if (args.limit) cliArgs.push("--limit", String(args.limit));
      return await runCLI("reminder-cli", cliArgs);

    case "reminder_get":
      return await runCLI("reminder-cli", ["get", "--id", args.id]);

    case "reminder_search":
      cliArgs.push("search", args.query);
      if (args.list) cliArgs.push("--list", args.list);
      if (args.completed) cliArgs.push("--completed");
      if (args.limit) cliArgs.push("--limit", String(args.limit));
      return await runCLI("reminder-cli", cliArgs);

    case "reminder_create":
      cliArgs.push("create", "--title", args.title);
      if (args.list) cliArgs.push("--list", args.list);
      if (args.due) cliArgs.push("--due", args.due);
      if (args.notes) cliArgs.push("--notes", args.notes);
      if (args.priority !== undefined)
        cliArgs.push("--priority", String(args.priority));
      if (args.alarm) {
        for (const minutes of args.alarm) {
          cliArgs.push("--alarm", String(minutes));
        }
      }
      return await runCLI("reminder-cli", cliArgs);

    case "reminder_complete":
      cliArgs.push("complete", "--id", args.id);
      if (args.undo) cliArgs.push("--undo");
      return await runCLI("reminder-cli", cliArgs);

    case "reminder_update":
      cliArgs.push("update", "--id", args.id);
      if (args.title) cliArgs.push("--title", args.title);
      if (args.due) cliArgs.push("--due", args.due);
      if (args.notes) cliArgs.push("--notes", args.notes);
      if (args.priority !== undefined)
        cliArgs.push("--priority", String(args.priority));
      return await runCLI("reminder-cli", cliArgs);

    case "reminder_delete":
      return await runCLI("reminder-cli", ["delete", "--id", args.id]);

    // Contact tools
    case "contact_groups":
      return await runCLI("contacts-cli", ["groups"]);

    case "contact_list":
      cliArgs.push("list");
      if (args.group) cliArgs.push("--group", args.group);
      if (args.limit) cliArgs.push("--limit", String(args.limit));
      return await runCLI("contacts-cli", cliArgs);

    case "contact_search":
      cliArgs.push("search", args.query);
      if (args.limit) cliArgs.push("--limit", String(args.limit));
      return await runCLI("contacts-cli", cliArgs);

    case "contact_get":
      return await runCLI("contacts-cli", ["get", "--id", args.id]);

    case "contact_create":
      cliArgs.push("create");
      if (args.name) cliArgs.push("--name", args.name);
      if (args.firstName) cliArgs.push("--first-name", args.firstName);
      if (args.lastName) cliArgs.push("--last-name", args.lastName);
      if (args.email) cliArgs.push("--email", args.email);
      if (args.phone) cliArgs.push("--phone", args.phone);
      if (args.organization) cliArgs.push("--organization", args.organization);
      if (args.jobTitle) cliArgs.push("--job-title", args.jobTitle);
      if (args.notes) cliArgs.push("--notes", args.notes);
      return await runCLI("contacts-cli", cliArgs);

    case "contact_update":
      cliArgs.push("update", "--id", args.id);
      if (args.firstName) cliArgs.push("--first-name", args.firstName);
      if (args.lastName) cliArgs.push("--last-name", args.lastName);
      if (args.email) cliArgs.push("--email", args.email);
      if (args.phone) cliArgs.push("--phone", args.phone);
      if (args.organization) cliArgs.push("--organization", args.organization);
      if (args.jobTitle) cliArgs.push("--job-title", args.jobTitle);
      if (args.notes) cliArgs.push("--notes", args.notes);
      return await runCLI("contacts-cli", cliArgs);

    case "contact_delete":
      return await runCLI("contacts-cli", ["delete", "--id", args.id]);

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// Create and run server
const server = new Server(
  {
    name: "apple-pim",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const result = await handleTool(name, args || {});
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              success: false,
              error: error.message,
            },
            null,
            2
          ),
        },
      ],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
