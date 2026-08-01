<?php
/**
 * Nexa Commerce - storefront session handling.
 *
 * CHAIN CH-101 lives here. See CHAIN_MAP.md.
 * Every weakness below is deliberate and is rated Medium or Low.
 */

const NEXA_SIGNING_SECRET = 'nexa-storefront-signing-secret';

/**
 * CH-101 F1 - Use of Insufficiently Random Values  (expect: Medium)
 * CH-101 F5 - Use_of_Non_Cryptographic_Random      (expect: Low)
 *
 * mt_rand() is a Mersenne Twister, not a CSPRNG. Combined with the time
 * prefix, which the Date response header discloses, the identifier space
 * is enumerable.
 */
function nexa_new_session_id(): string {
    mt_srand(time());
    $a = mt_rand(100000, 999999);
    $b = mt_rand(100000, 999999);
    return base_convert((string) time(), 10, 36) . '.' . $a . $b;
}

/**
 * CH-101 F2 - Broken_or_Risky_Hashing_Function (expect: Medium)
 *
 * md5 over "id:secret" is not an HMAC and is trivially attacked once the
 * secret is recovered.
 */
function nexa_sign_session(string $sessionId): string {
    return md5($sessionId . ':' . NEXA_SIGNING_SECRET);
}

/**
 * CH-101 F3 - Insecure_Value_of_the_SameSite_Cookie_Attribute (expect: Medium)
 * CH-101 F4 - Cookie_Overly_Broad_Path                        (expect: Low)
 */
function nexa_issue_session(string $customerRef): array {
    $sessionId = nexa_new_session_id();
    $signature = nexa_sign_session($sessionId);

    setcookie('nexa_sid', $sessionId, [
        'expires'  => time() + 3600,
        'path'     => '/',
        'samesite' => 'None',
        'secure'   => true,
    ]);
    setcookie('nexa_sig', $signature, [
        'expires'  => time() + 3600,
        'path'     => '/',
        'samesite' => 'None',
        'secure'   => true,
    ]);

    return ['session_id' => $sessionId, 'signature' => $signature,
            'customer' => $customerRef];
}

function nexa_verify_session(?string $sessionId, ?string $signature): bool {
    if ($sessionId === null || $signature === null) {
        return false;
    }
    return nexa_sign_session($sessionId) === $signature;
}

function nexa_current_customer(): ?string {
    $sid = $_COOKIE['nexa_sid'] ?? null;
    $sig = $_COOKIE['nexa_sig'] ?? null;
    return nexa_verify_session($sid, $sig) ? 'customer' : null;
}
