import { parseCatalog, parseProduct } from '../src/api/parse';

const VALID = {
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
};

describe('parseProduct', () => {
  it('accepts a well-formed product', () => {
    expect(parseProduct(VALID).id).toBe('p1');
  });

  it('rejects a missing field', () => {
    const { name, ...withoutName } = VALID;
    expect(() => parseProduct(withoutName)).toThrow(/name/);
  });

  it('rejects a price that is not an integer', () => {
    expect(() => parseProduct({ ...VALID, priceCents: 18.5 })).toThrow(/priceCents/);
  });

  it('rejects a negative price', () => {
    expect(() => parseProduct({ ...VALID, priceCents: -1 })).toThrow(/negative/);
  });

  it('rejects a non-https image URL', () => {
    expect(() => parseProduct({ ...VALID, imageUrl: 'file:///etc/passwd' })).toThrow(/https/);
    expect(() => parseProduct({ ...VALID, imageUrl: 'javascript:alert(1)' })).toThrow(/https/);
  });

  it('rejects an unsupported currency', () => {
    expect(() => parseProduct({ ...VALID, currency: 'XBT' })).toThrow(/currency/);
  });
});

describe('parseCatalog', () => {
  it('parses an items array', () => {
    expect(parseCatalog({ items: [VALID] })).toHaveLength(1);
  });

  it('rejects a payload without items', () => {
    expect(() => parseCatalog({})).toThrow(/items/);
  });
});
