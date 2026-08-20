/** Domain types shared across the app. */

/**
 * All money is carried as an integer number of minor units (cents) so that
 * totals never accumulate binary floating-point error. Formatting to a
 * human-readable string is the only place a decimal point appears.
 */
export type Cents = number;

export interface Product {
  id: string;
  name: string;
  /** Short line shown under the name in the catalog list. */
  blurb: string;
  description: string;
  priceCents: Cents;
  currency: 'USD';
  category: string;
  imageUrl: string;
  /** Units on hand; 0 means the product is listed but not orderable. */
  stock: number;
  rating: number;
}

export interface CartLine {
  product: Product;
  quantity: number;
}

export interface CartTotals {
  subtotalCents: Cents;
  shippingCents: Cents;
  taxCents: Cents;
  totalCents: Cents;
}

export interface ShippingAddress {
  fullName: string;
  line1: string;
  line2: string;
  city: string;
  region: string;
  postalCode: string;
  country: string;
}

export interface OrderLine {
  productId: string;
  name: string;
  quantity: number;
  unitPriceCents: Cents;
}

export interface Order {
  id: string;
  placedAt: string;
  lines: OrderLine[];
  totals: CartTotals;
  shipTo: ShippingAddress;
}
