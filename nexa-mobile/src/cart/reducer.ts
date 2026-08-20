import { roundCents, shippingFor, taxOn } from '../lib/money';
import type { CartLine, CartTotals, Product } from '../types';

/** Upper bound per line, matching the storefront's per-order limit. */
export const MAX_LINE_QUANTITY = 10;

export interface CartState {
  lines: CartLine[];
}

export type CartAction =
  | { type: 'add'; product: Product; quantity: number }
  | { type: 'setQuantity'; productId: string; quantity: number }
  | { type: 'remove'; productId: string }
  | { type: 'clear' }
  | { type: 'restore'; lines: CartLine[] };

export const EMPTY_CART: CartState = { lines: [] };

/**
 * Clamps a requested quantity into [0, min(stock, MAX_LINE_QUANTITY)].
 * Callers can pass anything a text input produced, including NaN.
 */
function clampQuantity(requested: number, stock: number): number {
  if (!Number.isFinite(requested)) return 0;
  const ceiling = Math.min(stock, MAX_LINE_QUANTITY);
  return Math.max(0, Math.min(Math.floor(requested), ceiling));
}

export function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'add': {
      const existing = state.lines.find((line) => line.product.id === action.product.id);
      const desired = (existing?.quantity ?? 0) + action.quantity;
      const quantity = clampQuantity(desired, action.product.stock);
      if (quantity === 0) return state;

      if (!existing) {
        return { lines: [...state.lines, { product: action.product, quantity }] };
      }
      return {
        lines: state.lines.map((line) =>
          line.product.id === action.product.id ? { ...line, quantity } : line,
        ),
      };
    }

    case 'setQuantity': {
      const target = state.lines.find((line) => line.product.id === action.productId);
      if (!target) return state;
      const quantity = clampQuantity(action.quantity, target.product.stock);
      if (quantity === 0) {
        return { lines: state.lines.filter((line) => line.product.id !== action.productId) };
      }
      return {
        lines: state.lines.map((line) =>
          line.product.id === action.productId ? { ...line, quantity } : line,
        ),
      };
    }

    case 'remove':
      return { lines: state.lines.filter((line) => line.product.id !== action.productId) };

    case 'clear':
      return EMPTY_CART;

    case 'restore':
      return { lines: action.lines };

    default:
      return state;
  }
}

export function lineTotal(line: CartLine): number {
  return line.product.priceCents * line.quantity;
}

export function countItems(state: CartState): number {
  return state.lines.reduce((sum, line) => sum + line.quantity, 0);
}

/**
 * Totals shown in the UI. The server recomputes these when the order is
 * placed and its numbers win; these exist so the customer is not waiting on a
 * round trip to see what a quantity change costs.
 */
export function computeTotals(state: CartState): CartTotals {
  const subtotalCents = state.lines.reduce((sum, line) => sum + lineTotal(line), 0);
  const shippingCents = shippingFor(subtotalCents);
  const taxCents = taxOn(subtotalCents);
  return {
    subtotalCents,
    shippingCents,
    taxCents,
    totalCents: roundCents(subtotalCents + shippingCents + taxCents),
  };
}
