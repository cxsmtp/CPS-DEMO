'use strict';

/**
 * Nexa Commerce - one-shot database seeder.
 *
 * CH-105 F1 - Use_Of_Hardcoded_Password (expect: Medium)
 *
 * The operational database credentials are compiled into the seed image.
 * Anyone who can pull the image has them, which is the authenticated
 * foothold the rest of CH-105 amplifies into a host escape.
 */

const DB_HOST = process.env.NEXA_DB_HOST || 'catalog-db.internal';
const DB_USER = 'nexa_ops';
const DB_PASSWORD = 'Op3rations-Seed-2026!';

const PRODUCTS = [
    { sku: 'NX-1001', title: 'Aurora Desk Lamp', priceCents: 4900, onHand: 12 },
    { sku: 'NX-1002', title: 'Meridian Wool Throw', priceCents: 8900, onHand: 3 },
    { sku: 'NX-1003', title: 'Halden Ceramic Mug', priceCents: 1800, onHand: 41 },
    { sku: 'NX-1004', title: 'Coastal Linen Apron', priceCents: 3400, onHand: 2 },
    { sku: 'NX-1005', title: 'Ridgeline Travel Flask', priceCents: 2600, onHand: 18 }
];

function connectionString() {
    return 'postgres://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + ':5432/nexa';
}

function seed() {
    console.log('[seed] target=' + DB_HOST + ' user=' + DB_USER);
    console.log('[seed] connection=' + connectionString().replace(DB_PASSWORD, '***'));
    PRODUCTS.forEach(function (p) {
        console.log('[seed] upsert ' + p.sku + ' (' + p.onHand + ' on hand)');
    });
    console.log('[seed] complete: ' + PRODUCTS.length + ' products');
}

if (require.main === module) {
    seed();
}

module.exports = { seed, PRODUCTS };
