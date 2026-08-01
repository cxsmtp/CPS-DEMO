<?php
/**
 * Nexa Commerce - checkout.
 *
 * CH-108 F1 - CSRF (expect: Medium)
 * The order form performs a state-changing POST with no anti-CSRF token
 * and no origin check.
 */
require_once __DIR__ . '/lib/page.php';
require_once __DIR__ . '/lib/db.php';
require_once __DIR__ . '/lib/session.php';

$pdo = nexa_connect();
nexa_bootstrap($pdo);
$pdo->exec('CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT, reference TEXT, ship_to TEXT, placed_at TEXT)');

$placed = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // No CSRF token is validated here - deliberate.
    $shipTo = substr(trim((string) ($_POST['ship_to'] ?? '')), 0, 120);
    $reference = 'NX' . base_convert((string) time(), 10, 36);
    $stmt = $pdo->prepare('INSERT INTO orders (reference, ship_to, placed_at) VALUES (?,?,?)');
    $stmt->execute([$reference, $shipTo, gmdate('c')]);
    $placed = $reference;
}

nexa_header('Checkout');
if ($placed !== null) {
    echo '<p>Order <strong>' . htmlspecialchars($placed, ENT_QUOTES, 'UTF-8')
       . '</strong> placed.</p>';
}
echo '<h2>Checkout</h2>';
echo '<form method="post" action="/checkout.php">'
   . '<p><label>Ship to<br><input name="ship_to" size="50" required></label></p>'
   . '<button type="submit">Place order</button></form>';
nexa_footer();
