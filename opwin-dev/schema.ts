import { z } from "zod";
import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

// NOTE: This schema persists customer data (name, email, phone, city, issue) to SQLite tables (bookings, quotes, payment_invoices, users). User-facing claims of privacy must reflect actual persistence.
export const consultationSchema = z.object({
  name: z.string().trim().min(2, "Please enter your name.").max(100),
  email: z.string().trim().email("Please enter a valid email address.").max(200),
  phone: z.string().trim().min(7, "Please enter a contact number.").max(30),
  location: z.enum(["california", "elsewhere"]),
  city: z.string().trim().min(2, "Please enter your city.").max(100),
  issue: z.string().trim().min(10, "Please add at least 10 characters.").max(1500),
});
export type Consultation = z.infer<typeof consultationSchema>;
export type BookingMode = "pay" | "quote";
export type Billing = "flat" | "hourly";
export const rates = { pay: { flat: 800, hourly: 500 }, quote: { flat: 500, hourly: 300 } } as const;

/** Persisted booking. One active reservation per Pacific calendar day. */
export const bookings = sqliteTable("bookings", {
  id: text("id").primaryKey(),
  date: text("date").notNull().unique(),
  mode: text("mode", { enum: ["pay", "quote"] }).notNull(),
  billing: text("billing", { enum: ["flat", "hourly"] }).notNull(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  phone: text("phone").notNull(),
  city: text("city").notNull(),
  location: text("location", { enum: ["california", "elsewhere"] }).notNull(),
  issue: text("issue").notNull(),
  rate: integer("rate").notNull(),
  status: text("status", { enum: ["pending", "confirmed", "cancelled"] }).notNull().default("pending"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull(),
});

/** Quote request. Rate to be confirmed after scope discussion. */
export const quotes = sqliteTable("quotes", {
  id: text("id").primaryKey(),
  date: text("date").notNull(),
  billing: text("billing", { enum: ["flat", "hourly"] }).notNull(),
  name: text("name").notNull(),
  email: text("email").notNull(),
  phone: text("phone").notNull(),
  city: text("city").notNull(),
  location: text("location", { enum: ["california", "elsewhere"] }).notNull(),
  issue: text("issue").notNull(),
  status: text("status", { enum: ["pending", "approved", "rejected"] }).notNull().default("pending"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull(),
});

export type InsertBooking = typeof bookings.$inferInsert;
export type SelectBooking = typeof bookings.$inferSelect;
export type InsertQuote = typeof quotes.$inferInsert;
export type SelectQuote = typeof quotes.$inferSelect;

/** Payment invoice. One invoice per booking, payable in Bitcoin. */
export const paymentInvoices = sqliteTable("payment_invoices", {
  id: text("id").primaryKey(),
  bookingId: text("booking_id").notNull().references(() => bookings.id),
  amountUsd: integer("amount_usd").notNull(),
  amountBtc: text("amount_btc").notNull(),
  btcAddress: text("btc_address").notNull(),
  status: text("status", { enum: ["pending", "paid", "expired"] }).notNull().default("pending"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull(),
  expiresAt: integer("expires_at", { mode: "timestamp" }).notNull(),
});

/** Auth users - owner and customers. */
export const users = sqliteTable("users", {
  id: text("id").primaryKey(),
  email: text("email").notNull().unique(),
  passwordHash: text("password_hash").notNull(),
  role: text("role", { enum: ["owner", "customer"] }).notNull().default("customer"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull(),
});

export type InsertPaymentInvoice = typeof paymentInvoices.$inferInsert;
export type SelectPaymentInvoice = typeof paymentInvoices.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
export type SelectUser = typeof users.$inferSelect;
