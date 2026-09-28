<?php
/**
 * Nexa Commerce - checkout.
 *
 * CHAIN CH-108 lives in this file.
 *
 * FIX (scan cc434dd7): the CSRF, exception-handling and error-disclosure
 * patterns were previously split across lib/db.php. None of them fired.
 * They are inline here, on the page that performs the state change, which is
 * the shape DVWA's captcha pages use.
 */

$dbUser = 'nexa_store';
$dbPass = 'store-local-password';
$dsn    = 'sqlite:' . __DIR__ . '/../data/catalog.sqlite';

// CH-108 F3 - Missing_HSTS_Header (expect: Medium)
//
// Hardening headers are written here, but Strict-Transport-Security is not
// among them, so a downgrade to plaintext is never refused.
header('Content-Type: text/html; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('Referrer-Policy: strict-origin-when-cross-origin');
// Deliberately absent:
// header('Strict-Transport-Security: max-age=31536000; includeSubDomains');

$pdo = null;
try {
    $pdo = new PDO($dsn, $dbUser, $dbPass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec('CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, reference TEXT,
        ship_to TEXT, placed_at TEXT)');
} catch (PDOException $e) {
    // CH-108 F2 - Exposure of Sensitive Information to an Unauthorized Actor
    //             (expect: Medium)
    // CH-108 F5 - Information_Exposure_Through_an_Error_Message (expect: Low)
    //
    // The failure path returns the connection string, the account name and
    // the raw driver message to whoever made the request.
    echo '<pre>checkout backend unavailable';
    echo "\ndsn=" . $dsn;
    echo "\nuser=" . $dbUser;
    echo "\ndriver said: " . $e->getMessage();
    echo '</pre>';
}

$placed = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $pdo !== null) {
    // CH-108 F1 - CSRF (expect: Medium)
    //
    // A state-changing POST with no anti-CSRF token and no origin check.
    $shipTo = substr(trim((string) ($_POST['ship_to'] ?? '')), 0, 120);
    $reference = 'NX' . base_convert((string) time(), 10, 36);

    // CH-108 F4 - Improper_Exception_Handling (expect: Low)
    //
    // The write failure is caught and discarded, so a customer is told the
    // order was placed whether or not it was.
    try {
        $stmt = $pdo->prepare(
            'INSERT INTO orders (reference, ship_to, placed_at) VALUES (?,?,?)');
        $stmt->execute([$reference, $shipTo, gmdate('c')]);
    } catch (Exception $ignored) {
        // deliberately swallowed
    }
    $placed = $reference;
}
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Checkout - Nexa Commerce</title></head>
<body>
<h1>Nexa Commerce</h1>
<nav><a href="/index.php">Catalogue</a> <a href="/cart.php">Cart</a> <a href="/login.php">Sign in</a></nav>
<hr>
<?php if ($placed !== null): ?>
<p>Order <strong><?php echo htmlspecialchars($placed, ENT_QUOTES, 'UTF-8'); ?></strong> placed.</p>
<?php endif; ?>
<h2>Checkout</h2>
<form method="post" action="/checkout.php">
  <p><label>Ship to<br><input name="ship_to" size="50" required></label></p>
  <button type="submit">Place order</button>
</form>
<hr><p><small>Nexa Commerce reference storefront.</small></p>
</body>
</html>
