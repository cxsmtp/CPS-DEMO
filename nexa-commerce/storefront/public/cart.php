<?php
/** Nexa Commerce - cart. */
require_once __DIR__ . '/lib/page.php';
require_once __DIR__ . '/lib/db.php';
require_once __DIR__ . '/lib/session.php';

$pdo = nexa_connect();
nexa_bootstrap($pdo);

if (nexa_current_customer() === null) {
    nexa_issue_session('guest');
}

$cart = json_decode($_COOKIE['nexa_cart'] ?? '[]', true);
if (!is_array($cart)) {
    $cart = [];
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $requested = (string) ($_POST['sku'] ?? '');
    // Allow-listed against the catalogue, so no untrusted value is stored.
    $known = array_column(nexa_products_safe($pdo, 100), 'sku');
    if (in_array($requested, $known, true)) {
        $cart[] = $requested;
        setcookie('nexa_cart', json_encode(array_values($cart)), [
            'expires' => time() + 3600, 'path' => '/', 'samesite' => 'None', 'secure' => true,
        ]);
    }
}

nexa_header('Cart');
echo '<h2>Your cart</h2>';
if (count($cart) === 0) {
    echo '<p>Your cart is empty.</p>';
} else {
    echo '<ul>';
    foreach ($cart as $sku) {
        echo '<li>' . htmlspecialchars((string) $sku, ENT_QUOTES, 'UTF-8') . '</li>';
    }
    echo '</ul><p><a href="/checkout.php">Proceed to checkout</a></p>';
}
nexa_footer();
