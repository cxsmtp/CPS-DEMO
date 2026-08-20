import type { Order, Product } from '../types';

/**
 * Hand-rolled runtime validation for anything crossing the network boundary.
 * `response.json()` returns `any`; TypeScript will happily let that flow into
 * a `Product` and blow up three screens later. Every field is checked here so
 * a malformed payload fails at the edge with a clear message.
 */

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function str(source: Record<string, unknown>, key: string): string {
  const value = source[key];
  if (typeof value !== 'string') throw new TypeError(`expected string at "${key}"`);
  return value;
}

function int(source: Record<string, unknown>, key: string): number {
  const value = source[key];
  if (typeof value !== 'number' || !Number.isInteger(value)) {
    throw new TypeError(`expected integer at "${key}"`);
  }
  return value;
}

function num(source: Record<string, unknown>, key: string): number {
  const value = source[key];
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(`expected number at "${key}"`);
  }
  return value;
}

/**
 * Product images are rendered by <Image source={{ uri }} />, which will follow
 * whatever scheme it is handed. Restricting to https keeps a hostile catalog
 * response from pointing the renderer at a local file or a custom scheme.
 */
function httpsUrl(source: Record<string, unknown>, key: string): string {
  const raw = str(source, key);
  let parsed: URL;
  try {
    parsed = new URL(raw);
  } catch {
    throw new TypeError(`expected a URL at "${key}"`);
  }
  if (parsed.protocol !== 'https:') throw new TypeError(`expected an https URL at "${key}"`);
  return parsed.toString();
}

export function parseProduct(value: unknown): Product {
  if (!isRecord(value)) throw new TypeError('expected a product object');
  const priceCents = int(value, 'priceCents');
  if (priceCents < 0) throw new TypeError('priceCents must not be negative');
  const stock = int(value, 'stock');
  if (stock < 0) throw new TypeError('stock must not be negative');
  const currency = str(value, 'currency');
  if (currency !== 'USD') throw new TypeError(`unsupported currency "${currency}"`);

  return {
    id: str(value, 'id'),
    name: str(value, 'name'),
    blurb: str(value, 'blurb'),
    description: str(value, 'description'),
    priceCents,
    currency,
    category: str(value, 'category'),
    imageUrl: httpsUrl(value, 'imageUrl'),
    stock,
    rating: num(value, 'rating'),
  };
}

export function parseCatalog(value: unknown): Product[] {
  if (!isRecord(value)) throw new TypeError('expected a catalog object');
  const items = value.items;
  if (!Array.isArray(items)) throw new TypeError('expected "items" to be an array');
  return items.map(parseProduct);
}

export function parseOrder(value: unknown): Order {
  if (!isRecord(value)) throw new TypeError('expected an order object');
  const totals = value.totals;
  if (!isRecord(totals)) throw new TypeError('expected "totals" to be an object');
  const shipTo = value.shipTo;
  if (!isRecord(shipTo)) throw new TypeError('expected "shipTo" to be an object');
  const lines = value.lines;
  if (!Array.isArray(lines)) throw new TypeError('expected "lines" to be an array');

  return {
    id: str(value, 'id'),
    placedAt: str(value, 'placedAt'),
    lines: lines.map((line) => {
      if (!isRecord(line)) throw new TypeError('expected an order line object');
      return {
        productId: str(line, 'productId'),
        name: str(line, 'name'),
        quantity: int(line, 'quantity'),
        unitPriceCents: int(line, 'unitPriceCents'),
      };
    }),
    totals: {
      subtotalCents: int(totals, 'subtotalCents'),
      shippingCents: int(totals, 'shippingCents'),
      taxCents: int(totals, 'taxCents'),
      totalCents: int(totals, 'totalCents'),
    },
    shipTo: {
      fullName: str(shipTo, 'fullName'),
      line1: str(shipTo, 'line1'),
      line2: str(shipTo, 'line2'),
      city: str(shipTo, 'city'),
      region: str(shipTo, 'region'),
      postalCode: str(shipTo, 'postalCode'),
      country: str(shipTo, 'country'),
    },
  };
}
