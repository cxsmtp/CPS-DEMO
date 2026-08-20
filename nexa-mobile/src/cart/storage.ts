import AsyncStorage from '@react-native-async-storage/async-storage';

import { parseProduct } from '../api/parse';
import type { CartLine } from '../types';
import { MAX_LINE_QUANTITY } from './reducer';

const CART_KEY = 'nexa.cart.v1';

/**
 * The cart is convenience state, not secrets, so AsyncStorage is the right
 * home for it. It is still untrusted on read: the file is user-writable on a
 * rooted device, and a stale entry can outlive a schema change.
 */
export async function loadCart(): Promise<CartLine[]> {
  const raw = await AsyncStorage.getItem(CART_KEY);
  if (!raw) return [];

  try {
    const decoded: unknown = JSON.parse(raw);
    if (!Array.isArray(decoded)) return [];

    return decoded.flatMap((entry): CartLine[] => {
      if (typeof entry !== 'object' || entry === null) return [];
      const { product, quantity } = entry as { product?: unknown; quantity?: unknown };
      if (typeof quantity !== 'number' || !Number.isInteger(quantity) || quantity <= 0) return [];
      try {
        const parsed = parseProduct(product);
        return [{ product: parsed, quantity: Math.min(quantity, MAX_LINE_QUANTITY) }];
      } catch {
        return [];
      }
    });
  } catch {
    // Corrupt payload: drop it rather than wedging every launch on a bad read.
    await AsyncStorage.removeItem(CART_KEY);
    return [];
  }
}

export async function saveCart(lines: CartLine[]): Promise<void> {
  await AsyncStorage.setItem(CART_KEY, JSON.stringify(lines));
}

export async function clearStoredCart(): Promise<void> {
  await AsyncStorage.removeItem(CART_KEY);
}
