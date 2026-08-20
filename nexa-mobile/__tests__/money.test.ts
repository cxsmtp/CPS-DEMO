import { formatMoney, roundCents, shippingFor, taxOn } from '../src/lib/money';

describe('formatMoney', () => {
  it('renders minor units with two decimal places', () => {
    expect(formatMoney(1999)).toBe('$19.99');
    expect(formatMoney(1800)).toBe('$18.00');
    expect(formatMoney(5)).toBe('$0.05');
    expect(formatMoney(0)).toBe('$0.00');
  });

  it('groups thousands', () => {
    expect(formatMoney(123456789)).toBe('$1,234,567.89');
  });

  it('keeps the sign outside the symbol', () => {
    expect(formatMoney(-250)).toBe('-$2.50');
  });
});

describe('roundCents', () => {
  it('rounds half away from zero in both directions', () => {
    expect(roundCents(2.5)).toBe(3);
    expect(roundCents(-2.5)).toBe(-3);
  });
});

describe('taxOn', () => {
  it('applies 8.25% and rounds to whole cents', () => {
    expect(taxOn(10_000)).toBe(825);
    expect(taxOn(1_800)).toBe(149); // 148.5 rounds away from zero
  });
});

describe('shippingFor', () => {
  it('charges the flat fee below the threshold and nothing at or above it', () => {
    expect(shippingFor(0)).toBe(0);
    expect(shippingFor(4_999)).toBe(599);
    expect(shippingFor(5_000)).toBe(0);
  });
});
