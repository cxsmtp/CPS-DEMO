import type { Cents } from '../types';

/** Tax applied at checkout, in basis points (825 = 8.25%). */
export const TAX_RATE_BPS = 825;

/** Flat shipping fee, waived once the subtotal reaches the threshold. */
export const SHIPPING_FLAT_CENTS = 599;
export const FREE_SHIPPING_THRESHOLD_CENTS = 5000;

/**
 * Rounds half away from zero, which is what a storefront's published tax
 * table does. `Math.round` alone rounds half *up*, which disagrees on
 * negative values (refund lines).
 */
export function roundCents(value: number): Cents {
  return value < 0 ? -Math.round(-value) : Math.round(value);
}

export function taxOn(subtotalCents: Cents): Cents {
  return roundCents((subtotalCents * TAX_RATE_BPS) / 10_000);
}

export function shippingFor(subtotalCents: Cents): Cents {
  if (subtotalCents <= 0) return 0;
  return subtotalCents >= FREE_SHIPPING_THRESHOLD_CENTS ? 0 : SHIPPING_FLAT_CENTS;
}

/** Formats minor units as a currency string, e.g. 1999 -> "$19.99". */
export function formatMoney(cents: Cents, currency: 'USD' = 'USD'): string {
  const symbol = currency === 'USD' ? '$' : '';
  const negative = cents < 0;
  const abs = Math.abs(cents);
  const whole = Math.floor(abs / 100);
  const fraction = String(abs % 100).padStart(2, '0');
  const grouped = String(whole).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return `${negative ? '-' : ''}${symbol}${grouped}.${fraction}`;
}
