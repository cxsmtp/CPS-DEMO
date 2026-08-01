<?php
/**
 * Nexa Commerce - storefront catalogue access.
 * CHAIN CH-108 partially lives here.
 */

const NEXA_DB_USER = 'nexa_store';
const NEXA_DB_PASS = 'store-local-password';

function nexa_dsn(): string {
    return 'sqlite:' . __DIR__ . '/../../data/catalog.sqlite';
}

/**
 * CH-108 F2 - Exposure of Sensitive Information to an Unauthorized Actor
 *             (expect: Medium)
 * CH-108 F5 - Information_Exposure_Through_an_Error_Message (expect: Low)
 *
 * The failure path returns the DSN, the account name and the raw driver
 * message. No request data reaches these strings, so there is no XSS sink.
 */
function nexa_connect(): PDO {
    try {
        $pdo = new PDO(nexa_dsn(), NEXA_DB_USER, NEXA_DB_PASS);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    } catch (PDOException $e) {
        header('Content-Type: text/plain');
        echo "catalogue backend unavailable\n";
        echo 'dsn=' . nexa_dsn() . "\n";
        echo 'user=' . NEXA_DB_USER . "\n";
        echo 'driver said: ' . $e->getMessage() . "\n";
        exit(1);
    }
}

function nexa_bootstrap(PDO $pdo): void {
    $pdo->exec('CREATE TABLE IF NOT EXISTS products (
        sku TEXT PRIMARY KEY, title TEXT NOT NULL, price_cents INTEGER NOT NULL)');
    $count = (int) $pdo->query('SELECT COUNT(*) FROM products')->fetchColumn();
    if ($count === 0) {
        $seed = $pdo->prepare('INSERT INTO products (sku,title,price_cents) VALUES (?,?,?)');
        foreach ([
            ['NX-1001', 'Aurora Desk Lamp', 4900],
            ['NX-1002', 'Meridian Wool Throw', 8900],
            ['NX-1003', 'Halden Ceramic Mug', 1800],
            ['NX-1004', 'Coastal Linen Apron', 3400],
            ['NX-1005', 'Ridgeline Travel Flask', 2600],
        ] as $row) {
            $seed->execute($row);
        }
    }
}

/** Parameter-bound on purpose: this chain is about defence erosion, not injection. */
function nexa_products(PDO $pdo, int $limit): array {
    $stmt = $pdo->prepare('SELECT sku, title, price_cents FROM products LIMIT :lim');
    $stmt->bindValue(':lim', $limit, PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

/**
 * CH-108 F4 - Improper_Exception_Handling (expect: Low)
 * The failure is caught and discarded; callers cannot tell an empty
 * catalogue from a broken one.
 */
function nexa_products_safe(PDO $pdo, int $limit): array {
    try {
        return nexa_products($pdo, $limit);
    } catch (Exception $ignored) {
        // deliberately swallowed
    }
    return [];
}
