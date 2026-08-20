import { REQUEST_TIMEOUT_MS, resolveApiBaseUrl } from './config';
import { readSessionToken } from './session';

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST';
  body?: unknown;
  signal?: AbortSignal;
}

/**
 * Joins a caller-supplied path onto the configured origin. Building the URL
 * through the URL constructor keeps a path such as `//evil.example.com` from
 * resolving to a different host than the one we configured.
 */
function buildUrl(path: string): string {
  const base = resolveApiBaseUrl();
  const url = new URL(path.startsWith('/') ? path : `/${path}`, base);
  if (url.origin !== base) {
    throw new Error(`refusing to call a host outside ${base}`);
  }
  return url.toString();
}

export async function apiRequest<T>(
  path: string,
  parse: (value: unknown) => T,
  options: RequestOptions = {},
): Promise<T> {
  const { method = 'GET', body, signal } = options;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  if (signal) {
    signal.addEventListener('abort', () => controller.abort(), { once: true });
  }

  const headers: Record<string, string> = { Accept: 'application/json' };
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  const token = await readSessionToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(buildUrl(path), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });

    if (!response.ok) {
      // The server's error body is not echoed to the UI; it can carry
      // backend detail that does not belong on a customer's screen.
      throw new ApiError(response.status, `request to ${path} failed`);
    }
    return parse(await response.json());
  } finally {
    clearTimeout(timeout);
  }
}
