/**
 * NAJD Orders Google Sheets Webhook
 *
 * Deploy this as a Google Apps Script Web App:
 *   Extensions > Apps Script > Deploy > New Deployment > Web app
 *   - Execute as: Me
 *   - Who has access: Anyone
 *
 * Copy the deployment URL to SHEET_WEBHOOK_URL in your .env.
 * Set SHEET_WEBHOOK_SECRET to match the backend secret.
 *
 * Sheet columns (row 1 = headers):
 *   A: order_number  B: created_at  C: customer_name  D: phone_e164
 *   E: status  F: confirmation_status  G: total_sar  H: currency
 *   I: items_summary  J: upsell_items_summary
 *   K: utm_source  L: utm_medium  M: utm_campaign
 *   N: landing_page  O: referrer  P: client_ip  Q: user_agent  R: notes
 */

var SHEET_NAME = "Orders";
var SECRET = ""; // Set this to match SHEET_WEBHOOK_SECRET in .env

var HEADERS = [
  "order_number",
  "created_at",
  "customer_name",
  "phone_e164",
  "status",
  "confirmation_status",
  "total_sar",
  "currency",
  "items_summary",
  "upsell_items_summary",
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "landing_page",
  "referrer",
  "client_ip",
  "user_agent",
  "notes",
];

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    // Validate secret if configured
    if (SECRET && data.secret !== SECRET) {
      return jsonResponse({ error: "Unauthorized" }, 401);
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME);

    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
      sheet.setFrozenRows(1);
    }

    // Check if order already exists by order_number (column A)
    var lastRow = sheet.getLastRow();
    var existingRow = null;

    if (lastRow > 1) {
      var orderNumbers = sheet
        .getRange(2, 1, lastRow - 1, 1)
        .getValues()
        .flat();
      var idx = orderNumbers.indexOf(data.order_number);
      if (idx !== -1) {
        existingRow = idx + 2; // +2 because array is 0-indexed and sheet has header row
      }
    }

    var row = [
      data.order_number || "",
      data.created_at || "",
      data.customer_name || "",
      data.phone_e164 || "",
      data.status || "",
      data.confirmation_status || "",
      data.total_sar || 0,
      data.currency || "SAR",
      data.items_summary || "",
      data.upsell_items_summary || "",
      data.utm_source || "",
      data.utm_medium || "",
      data.utm_campaign || "",
      data.landing_page || "",
      data.referrer || "",
      data.client_ip || "",
      data.user_agent || "",
      data.notes || "",
    ];

    if (existingRow) {
      sheet.getRange(existingRow, 1, 1, row.length).setValues([row]);
    } else {
      sheet.appendRow(row);
    }

    return jsonResponse({ ok: true, order_number: data.order_number });
  } catch (err) {
    Logger.log("NAJD Webhook Error: " + err.toString());
    return jsonResponse({ error: err.toString() }, 500);
  }
}

function doGet(e) {
  return jsonResponse({ ok: true, service: "NAJD Orders Webhook" });
}

function jsonResponse(obj, statusCode) {
  var output = ContentService.createTextOutput(JSON.stringify(obj));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
