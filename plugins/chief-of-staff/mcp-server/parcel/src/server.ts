/**
 * Parcel MCP Server
 *
 * Provides tools for interacting with the Parcel delivery tracking API.
 *
 * Environment variables:
 *   PARCEL_API_KEY - Required. Get from Parcel app: Settings > Integrations > API Key
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const PARCEL_API_BASE = "https://api.parcel.app/external/v1";

// Validate API key on startup
const apiKey = process.env.PARCEL_API_KEY;
if (!apiKey) {
  console.error(`
Error: PARCEL_API_KEY environment variable is required.

To get your API key:
1. Open the Parcel app on your Mac
2. Go to Settings > Integrations
3. Enable API access and copy your API key
4. Set it in your environment: export PARCEL_API_KEY="your-key"
`);
  process.exit(1);
}

// Create server instance
const server = new McpServer({
  name: "parcel",
  version: "1.0.0",
});

// Helper for API requests
async function parcelRequest(
  endpoint: string,
  method: "GET" | "POST" | "DELETE" = "GET",
  body?: unknown
): Promise<unknown> {
  const url = `${PARCEL_API_BASE}${endpoint}`;
  const options: RequestInit = {
    method,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Parcel API error (${response.status}): ${errorText}`);
  }

  return response.json();
}

// Carrier codes reference
const CARRIERS = {
  ups: "UPS",
  fedex: "FedEx",
  usps: "USPS",
  dhl: "DHL",
  "dhl-express": "DHL Express",
  ontrac: "OnTrac",
  lasership: "LaserShip",
  amazon: "Amazon Logistics",
  "amazon-us": "Amazon US",
  cdl: "CDL Last Mile",
  "ups-mi": "UPS Mail Innovations",
  "fedex-smartpost": "FedEx SmartPost",
  "dhl-global-mail": "DHL Global Mail",
  newgistics: "Newgistics/Pitney Bowes",
  veho: "Veho",
  "ups-surepost": "UPS SurePost",
};

// Status codes reference
const STATUS_CODES = {
  unknown: "Status unknown",
  "info-received": "Shipping label created, carrier awaiting package",
  "in-transit": "Package in transit",
  "out-for-delivery": "Out for delivery",
  delivered: "Delivered",
  exception: "Delivery exception (delay, failed attempt, etc.)",
  pickup: "Available for pickup",
  returned: "Package returned to sender",
};

// Tool: Get deliveries
server.tool(
  "get_deliveries",
  "Get active and recent deliveries from Parcel. Returns tracking info, status, and estimated delivery dates.",
  {
    include_delivered: z
      .boolean()
      .optional()
      .default(true)
      .describe("Include recently delivered packages (default: true)"),
    limit: z
      .number()
      .optional()
      .default(50)
      .describe("Maximum number of deliveries to return (default: 50)"),
  },
  async ({ include_delivered, limit }) => {
    const deliveries = (await parcelRequest("/deliveries")) as Array<{
      id: string;
      trackingNumber: string;
      carrier: string;
      description: string;
      status: string;
      statusMessage: string;
      estimatedDelivery: string | null;
      deliveredAt: string | null;
      lastUpdate: string;
      events: Array<{
        timestamp: string;
        description: string;
        location: string;
      }>;
    }>;

    let filtered = deliveries;

    // Filter out delivered if requested
    if (!include_delivered) {
      filtered = filtered.filter((d) => d.status !== "delivered");
    }

    // Apply limit
    filtered = filtered.slice(0, limit);

    // Format for display
    const formatted = filtered.map((d) => ({
      id: d.id,
      tracking_number: d.trackingNumber,
      carrier: d.carrier,
      description: d.description || "No description",
      status: d.status,
      status_message: d.statusMessage,
      estimated_delivery: d.estimatedDelivery,
      delivered_at: d.deliveredAt,
      last_update: d.lastUpdate,
      latest_event: d.events?.[0]
        ? {
            time: d.events[0].timestamp,
            description: d.events[0].description,
            location: d.events[0].location,
          }
        : null,
    }));

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(formatted, null, 2),
        },
      ],
    };
  }
);

// Tool: Add delivery
server.tool(
  "add_delivery",
  "Add a new delivery to Parcel for tracking. Provide tracking number and carrier code.",
  {
    tracking_number: z
      .string()
      .describe("The tracking number from the carrier"),
    carrier: z
      .string()
      .describe(
        "Carrier code (e.g., ups, fedex, usps, dhl, amazon). Use get_supported_carriers to see all codes."
      ),
    description: z
      .string()
      .optional()
      .describe("Optional description (e.g., 'Amazon order - headphones')"),
  },
  async ({ tracking_number, carrier, description }) => {
    const payload: {
      trackingNumber: string;
      carrier: string;
      description?: string;
    } = {
      trackingNumber: tracking_number,
      carrier: carrier.toLowerCase(),
    };

    if (description) {
      payload.description = description;
    }

    const result = (await parcelRequest("/deliveries", "POST", payload)) as {
      id: string;
      trackingNumber: string;
      carrier: string;
      status: string;
    };

    return {
      content: [
        {
          type: "text" as const,
          text: `Successfully added delivery:\n- ID: ${result.id}\n- Tracking: ${result.trackingNumber}\n- Carrier: ${result.carrier}\n- Status: ${result.status}`,
        },
      ],
    };
  }
);

// Tool: Get supported carriers
server.tool(
  "get_supported_carriers",
  "Get list of supported carrier codes for adding deliveries",
  {},
  async () => {
    const carrierList = Object.entries(CARRIERS)
      .map(([code, name]) => `${code}: ${name}`)
      .join("\n");

    return {
      content: [
        {
          type: "text" as const,
          text: `Supported carriers:\n\n${carrierList}\n\nUse the code (left side) when adding deliveries.`,
        },
      ],
    };
  }
);

// Tool: Get status codes
server.tool(
  "get_delivery_status_codes",
  "Get reference of delivery status codes and their meanings",
  {},
  async () => {
    const statusList = Object.entries(STATUS_CODES)
      .map(([code, meaning]) => `${code}: ${meaning}`)
      .join("\n");

    return {
      content: [
        {
          type: "text" as const,
          text: `Delivery status codes:\n\n${statusList}`,
        },
      ],
    };
  }
);

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Parcel MCP server running on stdio");
}

main().catch((error) => {
  console.error("Failed to start server:", error);
  process.exit(1);
});
