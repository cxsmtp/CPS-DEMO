<?php
/** Nexa Commerce - catalogue page. */
require_once __DIR__ . '/lib/page.php';
require_once __DIR__ . '/lib/db.php';
require_once __DIR__ . '/lib/session.php';

$pdo = nexa_connect();
nexa_bootstrap($pdo);
$products = nexa_products_safe($pdo, 20);

nexa_header('Catalogue');
echo '<h2>Catalogue</h2><table><tr><th>SKU</th><th>Product</th><th>Price</th><th></th></tr>';
foreach ($products as $p) {
    $sku   = htmlspecialchars($p['sku'], ENT_QUOTES, 'UTF-8');
    $title = htmlspecialchars($p['title'], ENT_QUOTES, 'UTF-8');
    $price = number_format(((int) $p['price_cents']) / 100, 2);
    echo "<tr><td>{$sku}</td><td>{$title}</td><td>&pound;{$price}</td>"
       . "<td><form method=\"post\" action=\"/cart.php\">"
       . "<input type=\"hidden\" name=\"sku\" value=\"{$sku}\">"
       . "<button type=\"submit\">Add to cart</button></form></td></tr>";
}
echo '</table>';
nexa_footer();
