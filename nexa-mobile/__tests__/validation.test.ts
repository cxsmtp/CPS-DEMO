import { emptyAddress, hasErrors, normalizeSpace, validateAddress } from '../src/lib/validation';
import type { ShippingAddress } from '../src/types';

const GOOD: ShippingAddress = {
  fullName: 'Ada Lovelace',
  line1: '12 Analytical Way',
  line2: '',
  city: 'London',
  region: 'Greater London',
  postalCode: 'NW1 4RY',
  country: 'GB',
};

describe('normalizeSpace', () => {
  it('trims and collapses internal runs of whitespace', () => {
    expect(normalizeSpace('  Ada   Lovelace  ')).toBe('Ada Lovelace');
  });
});

describe('validateAddress', () => {
  it('accepts a complete address', () => {
    expect(hasErrors(validateAddress(GOOD))).toBe(false);
  });

  it('flags every empty required field', () => {
    const errors = validateAddress({ ...emptyAddress(), country: '' });
    expect(Object.keys(errors).sort()).toEqual(
      ['city', 'country', 'fullName', 'line1', 'postalCode', 'region'].sort(),
    );
  });

  it('rejects a malformed postal code', () => {
    expect(validateAddress({ ...GOOD, postalCode: '!!' }).postalCode).toBeDefined();
  });

  it('requires a two-letter country code', () => {
    expect(validateAddress({ ...GOOD, country: 'United Kingdom' }).country).toBeDefined();
  });

  it('treats line2 as optional', () => {
    expect(hasErrors(validateAddress({ ...GOOD, line2: '' }))).toBe(false);
  });
});
