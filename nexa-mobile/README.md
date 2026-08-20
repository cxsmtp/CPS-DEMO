# Nexa Mobile

A small React Native storefront for the Nexa Commerce catalog: browse
products, open one, adjust quantities in a cart that survives app restarts,
and place an order behind client-side address validation.

It is written as ordinary production-shaped application code. Unlike
[`../nexa-commerce/`](../nexa-commerce/), which is a controlled specimen with
ten deliberately planted vulnerability chains, **nothing here is seeded**. It
is in this repository to give the CPS work a mobile surface to scan whose
findings are whatever a scanner genuinely finds.

## Stack

| Piece | Choice |
|---|---|
| Runtime | React Native 0.86 on Expo SDK 57, React 19 |
| Language | TypeScript 5.9, `strict` plus `noUncheckedIndexedAccess` |
| Navigation | `@react-navigation/native-stack` |
| State | `useReducer` + context, no external store |
| Cart persistence | AsyncStorage, revalidated on read |
| Session token | `expo-secure-store` (Keychain / EncryptedSharedPreferences) |
| Tests | Jest + ts-jest over the pure logic |

## Layout

```
App.tsx                     provider stack and navigator mount
src/api/          config.ts        https-only base URL resolution
                  client.ts        fetch wrapper: timeout, auth header, URL pinning
                  parse.ts         runtime validation of every network payload
                  catalog.ts       catalog fetch (offline fallback) and order placement
                  session.ts       session token in the platform keystore
src/cart/         reducer.ts       add/remove/quantity, stock and per-line clamping
                  storage.ts       AsyncStorage round-trip, untrusted on read
                  CartContext.tsx  hydration, persistence, derived totals
src/lib/          money.ts         integer-cent arithmetic and formatting
                  validation.ts    shipping address checks
                  ids.ts           CSPRNG idempotency keys
src/components/   Button, ProductCard, QuantityStepper, TextField, TotalsPanel
src/screens/      Catalog, Product, Cart, Checkout, Confirmation
src/data/         catalog.ts       bundled fallback catalog
__tests__/        money, cart reducer, response parsing, address validation
```

## Notes on the parts that are easy to get wrong

**Money is never a float.** Prices, totals and tax are integer cents
throughout; `formatMoney` is the only place a decimal point is produced. Tax
rounds half away from zero, which is what a published tax table does and what
`Math.round` alone gets wrong on refund lines.

**Client totals are advisory.** `computeTotals` exists so a quantity change
updates the screen without a round trip. The server recomputes on order
placement and its numbers are authoritative.

**Everything crossing the network boundary is parsed.** `response.json()`
returns `any`. `src/api/parse.ts` checks every field, so a malformed catalog
fails at the edge with a clear message instead of three screens later. Image
URLs must be https — the `<Image>` renderer will follow whatever scheme it is
handed.

**Stored cart state is untrusted.** The AsyncStorage file is user-writable on
a rooted device and can outlive a schema change, so `loadCart` runs entries
through the same product parser as the network path and drops what fails.

**Checkout is idempotent.** The idempotency key is drawn from the platform
CSPRNG once per checkout attempt and held across retries, so a resubmit after
a timeout resolves to one order rather than two.

**No card data.** Payment is handed to a hosted checkout after order
placement. Card details are never entered in, or stored by, this app.

## Running it

```bash
cd nexa-mobile
npm install
npm start          # then press i / a, or scan the QR with Expo Go
```

Point the app at a different backend by editing `expo.extra.apiBaseUrl` in
`app.json`. It must be an https origin: cleartext traffic is disabled on both
platforms, and `resolveApiBaseUrl` rejects anything else at startup rather
than failing opaquely at the first request.

With no backend reachable, the catalog screen falls back to the bundled list
in `src/data/catalog.ts` and shows an offline notice. Browsing and the cart
work fully offline; placing an order does not.

## Checks

```bash
npm run typecheck   # tsc --noEmit
npm test            # jest
```

Both pass clean: 31 tests across money arithmetic, the cart reducer's clamping
rules, response parsing rejections, and address validation.

## Scanning

The app is scanned as part of the repository-wide Checkmarx scan. `node_modules/`
is excluded via `.cxignore` and the root `.gitignore`.

### What the first scan found, and what was done about it

The initial pin was Expo SDK 51 / React Native 0.74. Checkmarx SCA flagged
**CVE-2025-11953** against it — CVSS 9.8, CWE-78 OS command injection, in
`@react-native-community/cli-server-api@13.6.9`, reached transitively through
`react-native`. The Metro development server binds to external interfaces by
default and exposes an endpoint that runs arbitrary executables for an
unauthenticated caller on the same network.

It is a development-time exposure rather than something that ships in the app
bundle, which is exactly the shape of finding a severity-ordered backlog
defers. It is also a remote code execution path on every developer machine
running `npm start`, so it was fixed rather than deferred: the app moved to
Expo SDK 57 / React Native 0.86 / React 19, which drops the
`@react-native-community/cli` chain altogether. That took the tree from 1283
packages to 737, and from 1 critical / 19 high to **0 critical / 8 high**.

The 8 that remain are the Metro bundler chain (`metro`, `@expo/cli`,
`@expo/metro-config`) reached through `expo` itself, all tracing to
`image-size`, whose advisory has no fixed version at any Expo SDK. Nothing in
this repository can pin them away; they are recorded here rather than hidden.

### Verified result

A second scan after the upgrade (`64dd83a9`, SAST + SCA) confirms the fix:
CVE-2025-11953 is absent, and across the whole repository the 1 remaining
Critical and all 18 High findings are `RECURRENT` and live in
`nexa-commerce/` or `cps_project/`. Enumerating every Critical, High and
Medium finding in that scan gives, for `nexa-mobile/`:

| Severity | Count in `nexa-mobile/` |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 5 — all one query in one file, see below |

### A known false positive

Checkmarx SAST reports `Secret_Leak_in_Error_Messages` (Low) five times
against `src/api/parse.ts`, at every `throw new TypeError(...)` that names the
field it rejected.

Those messages interpolate the *field name* and never the *field value* —
`expected string at "priceCents"`, never the contents of `priceCents`. The
names are hardcoded string literals at each call site, so no request or
response data reaches the message. The finding is not real.

It is deliberately left unsuppressed. This directory exists to show what a
scanner reports on unplanted code, and a false positive is part of that
picture; editing the code to quiet a heuristic would remove the evidence.
