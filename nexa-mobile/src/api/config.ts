import Constants from 'expo-constants';

const DEFAULT_BASE_URL = 'https://api.nexa.example.com';

/**
 * Resolves the API origin from the Expo config. The value must be an https
 * origin: the app ships with cleartext traffic disabled on both platforms, so
 * an http base URL would fail at the transport layer anyway — rejecting it
 * here turns a confusing runtime error into a clear one at startup.
 */
export function resolveApiBaseUrl(): string {
  const configured = Constants.expoConfig?.extra?.apiBaseUrl;
  const candidate = typeof configured === 'string' && configured.length > 0 ? configured : DEFAULT_BASE_URL;

  let parsed: URL;
  try {
    parsed = new URL(candidate);
  } catch {
    throw new Error('apiBaseUrl in app config is not a valid URL');
  }
  if (parsed.protocol !== 'https:') {
    throw new Error('apiBaseUrl must use https');
  }
  return parsed.origin;
}

/** Milliseconds before an in-flight request is abandoned. */
export const REQUEST_TIMEOUT_MS = 10_000;
