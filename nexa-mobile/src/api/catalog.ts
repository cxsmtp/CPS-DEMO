import { FALLBACK_CATALOG } from '../data/catalog';
import type { Order, Product, ShippingAddress } from '../types';
import { apiRequest } from './client';
import { parseCatalog, parseOrder } from './parse';

export interface CatalogResult {
  products: Product[];
  /** True when the network call failed and the bundled list is being shown. */
  offline: boolean;
}

export async function fetchCatalog(signal?: AbortSignal): Promise<CatalogResult> {
  try {
    const products = await apiRequest('/v1/catalog', parseCatalog, { signal });
    return { products, offline: false };
  } catch {
    return { products: FALLBACK_CATALOG, offline: true };
  }
}

export interface PlaceOrderRequest {
  lines: { productId: string; quantity: number }[];
  shipTo: ShippingAddress;
  /**
   * Idempotency key. A checkout retried after a timeout must not create a
   * second order, so the client generates the key once per checkout attempt
   * and the server dedupes on it.
   */
  idempotencyKey: string;
}

export function placeOrder(request: PlaceOrderRequest, signal?: AbortSignal): Promise<Order> {
  return apiRequest('/v1/orders', parseOrder, { method: 'POST', body: request, signal });
}
