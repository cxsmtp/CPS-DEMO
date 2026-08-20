import type { ShippingAddress } from '../types';

export type FieldErrors<T> = Partial<Record<keyof T, string>>;

const POSTAL_CODE = /^[A-Za-z0-9][A-Za-z0-9 -]{2,9}$/;

/** Trims and collapses runs of whitespace, so " Ada   Lovelace " is one name. */
export function normalizeSpace(value: string): string {
  return value.trim().replace(/\s+/g, ' ');
}

export function emptyAddress(): ShippingAddress {
  return {
    fullName: '',
    line1: '',
    line2: '',
    city: '',
    region: '',
    postalCode: '',
    country: 'US',
  };
}

/**
 * Validates a shipping address for shape only. The server revalidates and is
 * the authority; this exists so the customer sees the problem before the
 * round trip, not instead of it.
 */
export function validateAddress(address: ShippingAddress): FieldErrors<ShippingAddress> {
  const errors: FieldErrors<ShippingAddress> = {};

  if (normalizeSpace(address.fullName).length < 2) {
    errors.fullName = 'Enter the recipient’s full name.';
  }
  if (normalizeSpace(address.line1).length < 3) {
    errors.line1 = 'Enter a street address.';
  }
  if (normalizeSpace(address.city).length < 2) {
    errors.city = 'Enter a city.';
  }
  if (normalizeSpace(address.region).length < 2) {
    errors.region = 'Enter a state or region.';
  }
  if (!POSTAL_CODE.test(normalizeSpace(address.postalCode))) {
    errors.postalCode = 'Enter a valid postal code.';
  }
  if (normalizeSpace(address.country).length !== 2) {
    errors.country = 'Use a two-letter country code.';
  }

  return errors;
}

export function hasErrors<T>(errors: FieldErrors<T>): boolean {
  return Object.keys(errors).length > 0;
}
