import {
  cartReducer,
  computeTotals,
  countItems,
  EMPTY_CART,
  MAX_LINE_QUANTITY,
  type CartState,
} from '../src/cart/reducer';
import type { Product } from '../src/types';

function product(overrides: Partial<Product> = {}): Product {
  return {
    id: 'p1',
    name: 'Mug',
    blurb: 'A mug',
    description: 'A mug.',
    priceCents: 1800,
    currency: 'USD',
    category: 'Kitchen',
    imageUrl: 'https://cdn.example.com/p1.jpg',
    stock: 5,
    rating: 4.5,
    ...overrides,
  };
}

describe('cartReducer', () => {
  it('adds a new line', () => {
    const next = cartReducer(EMPTY_CART, { type: 'add', product: product(), quantity: 2 });
    expect(next.lines).toHaveLength(1);
    expect(next.lines[0]?.quantity).toBe(2);
  });

  it('merges a repeat add into the existing line', () => {
    let state = cartReducer(EMPTY_CART, { type: 'add', product: product(), quantity: 2 });
    state = cartReducer(state, { type: 'add', product: product(), quantity: 1 });
    expect(state.lines).toHaveLength(1);
    expect(state.lines[0]?.quantity).toBe(3);
  });

  it('never exceeds available stock', () => {
    const state = cartReducer(EMPTY_CART, {
      type: 'add',
      product: product({ stock: 3 }),
      quantity: 9,
    });
    expect(state.lines[0]?.quantity).toBe(3);
  });

  it('never exceeds the per-line maximum', () => {
    const state = cartReducer(EMPTY_CART, {
      type: 'add',
      product: product({ stock: 500 }),
      quantity: 99,
    });
    expect(state.lines[0]?.quantity).toBe(MAX_LINE_QUANTITY);
  });

  it('ignores an add for a sold-out product', () => {
    const state = cartReducer(EMPTY_CART, {
      type: 'add',
      product: product({ stock: 0 }),
      quantity: 1,
    });
    expect(state.lines).toHaveLength(0);
  });

  it('drops the line when the quantity is set to zero', () => {
    const seeded = cartReducer(EMPTY_CART, { type: 'add', product: product(), quantity: 2 });
    const next = cartReducer(seeded, { type: 'setQuantity', productId: 'p1', quantity: 0 });
    expect(next.lines).toHaveLength(0);
  });

  it('ignores a non-numeric quantity rather than corrupting the line', () => {
    const seeded = cartReducer(EMPTY_CART, { type: 'add', product: product(), quantity: 2 });
    const next = cartReducer(seeded, { type: 'setQuantity', productId: 'p1', quantity: Number.NaN });
    expect(next.lines).toHaveLength(0);
  });

  it('removes and clears', () => {
    const seeded = cartReducer(EMPTY_CART, { type: 'add', product: product(), quantity: 2 });
    expect(cartReducer(seeded, { type: 'remove', productId: 'p1' }).lines).toHaveLength(0);
    expect(cartReducer(seeded, { type: 'clear' }).lines).toHaveLength(0);
  });
});

describe('totals', () => {
  it('adds shipping below the free threshold', () => {
    const state: CartState = { lines: [{ product: product({ priceCents: 1800 }), quantity: 1 }] };
    const totals = computeTotals(state);
    expect(totals.subtotalCents).toBe(1800);
    expect(totals.shippingCents).toBe(599);
    expect(totals.taxCents).toBe(149);
    expect(totals.totalCents).toBe(1800 + 599 + 149);
  });

  it('waives shipping at the threshold', () => {
    const state: CartState = { lines: [{ product: product({ priceCents: 6400 }), quantity: 1 }] };
    expect(computeTotals(state).shippingCents).toBe(0);
  });

  it('counts every unit, not every line', () => {
    const state: CartState = {
      lines: [
        { product: product({ id: 'a' }), quantity: 2 },
        { product: product({ id: 'b' }), quantity: 3 },
      ],
    };
    expect(countItems(state)).toBe(5);
  });
});
