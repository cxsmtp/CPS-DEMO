import * as Crypto from 'expo-crypto';

/**
 * Generates an idempotency key for a checkout attempt.
 *
 * This is drawn from the platform CSPRNG rather than Math.random: the key is
 * the only thing standing between a retried checkout and a duplicate charge,
 * so a predictable or colliding value is a correctness problem, not just a
 * theoretical one.
 */
export function newIdempotencyKey(): string {
  return Crypto.randomUUID();
}
