/**
 * Parcel MCP Server
 *
 * Provides tools for interacting with the Parcel delivery tracking API.
 * API documentation: https://parcelapp.net/help/api.html
 *
 * Environment variables:
 *   PARCEL_API_KEY - Required. Get from Parcel app: Settings > Integrations > API Key
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const PARCEL_API_BASE = "https://api.parcel.app/external";

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
  version: "1.1.0",
});

// Parcel API response types
interface ParcelDelivery {
  carrier_code: string;
  description: string;
  status_code: number;
  tracking_number: string;
  extra_information?: string;
  date_expected?: string;
  date_expected_end?: string;
  events?: Array<{
    event: string;
    date: string;
    location?: string;
  }>;
}

interface ParcelDeliveriesResponse {
  success: boolean;
  error_message?: string;
  deliveries: ParcelDelivery[];
}

interface ParcelAddDeliveryResponse {
  success: boolean;
  error_message?: string;
}

// Helper for API requests
async function parcelRequest(
  endpoint: string,
  method: "GET" | "POST" = "GET",
  body?: unknown
): Promise<unknown> {
  const url = `${PARCEL_API_BASE}${endpoint}`;
  const options: RequestInit = {
    method,
    headers: {
      "api-key": apiKey!,
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

// Carrier codes reference (common ones)
const CARRIERS: Record<string, string> = {
  ups: "UPS",
  fedex: "FedEx",
  usps: "USPS",
  dhl: "DHL",
  "dhl-express": "DHL Express",
  ontrac: "OnTrac",
  lasership: "LaserShip",
  amazon: "Amazon Logistics",
  amzlus: "Amazon US",
  cdl: "CDL Last Mile",
  "ups-mi": "UPS Mail Innovations",
  "fedex-smartpost": "FedEx SmartPost",
  "dhl-global-mail": "DHL Global Mail",
  newgistics: "Newgistics/Pitney Bowes",
  veho: "Veho",
  "ups-surepost": "UPS SurePost",
  pholder: "Placeholder (manual tracking)",
};

// Status codes from Parcel API
const STATUS_CODES: Record<number, string> = {
  0: "Delivered",
  1: "Attempted delivery",
  2: "In transit",
  3: "Out for delivery",
  4: "Info received / Label created",
  5: "Exception / Problem",
  6: "Expired / Unknown",
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
    const response = (await parcelRequest(
      "/deliveries/"
    )) as ParcelDeliveriesResponse;

    if (!response.success) {
      throw new Error(
        `Parcel API error: ${response.error_message || "Unknown error"}`
      );
    }

    let deliveries = response.deliveries;

    // Filter out delivered (status_code 0) if requested
    if (!include_delivered) {
      deliveries = deliveries.filter((d) => d.status_code !== 0);
    }

    // Apply limit
    deliveries = deliveries.slice(0, limit);

    // Format for display
    const formatted = deliveries.map((d) => ({
      tracking_number: d.tracking_number,
      carrier: d.carrier_code,
      carrier_name: CARRIERS[d.carrier_code] || d.carrier_code,
      description: d.description || "No description",
      status_code: d.status_code,
      status: STATUS_CODES[d.status_code] || "Unknown",
      date_expected: d.date_expected || null,
      latest_event: d.events?.[0] || null,
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
      .describe("Description of the package (e.g., 'Amazon order - headphones')"),
  },
  async ({ tracking_number, carrier, description }) => {
    const payload = {
      tracking_number: tracking_number,
      carrier_code: carrier.toLowerCase(),
      description: description || "Package",
    };

    const result = (await parcelRequest(
      "/add-delivery/",
      "POST",
      payload
    )) as ParcelAddDeliveryResponse;

    if (!result.success) {
      throw new Error(
        `Failed to add delivery: ${result.error_message || "Unknown error"}`
      );
    }

    return {
      content: [
        {
          type: "text" as const,
          text: `Successfully added delivery:\n- Tracking: ${tracking_number}\n- Carrier: ${carrier}\n- Description: ${description || "Package"}`,
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
