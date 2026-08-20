import type { Product } from '../types';

/**
 * Bundled catalog. The app prefers the live catalog endpoint and falls back
 * to this list when the device is offline, so a cold start on a plane still
 * renders something browsable.
 */
export const FALLBACK_CATALOG: Product[] = [
  {
    id: 'nx-mug-01',
    name: 'Kiln Ceramic Mug',
    blurb: 'Stoneware, 12 oz, dishwasher safe',
    description:
      'A heavy-bottomed stoneware mug fired at 1250C. The glaze is food-safe ' +
      'and the handle is sized for a full hand rather than two fingers.',
    priceCents: 1800,
    currency: 'USD',
    category: 'Kitchen',
    imageUrl: 'https://cdn.nexa.example.com/products/nx-mug-01.jpg',
    stock: 42,
    rating: 4.6,
  },
  {
    id: 'nx-lamp-02',
    name: 'Ridge Desk Lamp',
    blurb: 'Warm LED, three brightness steps',
    description:
      'An aluminium desk lamp with a 2700K LED array and a weighted base. ' +
      'Draws 7W at full brightness and holds its angle without a spring.',
    priceCents: 6400,
    currency: 'USD',
    category: 'Lighting',
    imageUrl: 'https://cdn.nexa.example.com/products/nx-lamp-02.jpg',
    stock: 12,
    rating: 4.3,
  },
  {
    id: 'nx-tote-03',
    name: 'Harbour Canvas Tote',
    blurb: '18 oz cotton canvas, leather straps',
    description:
      'Cut from 18 oz canvas with bridle leather handles and a flat base ' +
      'panel, so it stands up on its own when loaded.',
    priceCents: 4200,
    currency: 'USD',
    category: 'Bags',
    imageUrl: 'https://cdn.nexa.example.com/products/nx-tote-03.jpg',
    stock: 7,
    rating: 4.8,
  },
  {
    id: 'nx-note-04',
    name: 'Field Notebook, 3-pack',
    blurb: '64 pages, dot grid, sewn spine',
    description:
      'Three pocket notebooks with sewn spines that open flat. 90gsm dot ' +
      'grid paper that takes fountain ink without feathering.',
    priceCents: 1450,
    currency: 'USD',
    category: 'Stationery',
    imageUrl: 'https://cdn.nexa.example.com/products/nx-note-04.jpg',
    stock: 88,
    rating: 4.5,
  },
  {
    id: 'nx-press-05',
    name: 'Anvil French Press',
    blurb: 'Borosilicate, 800ml, steel filter',
    description:
      'An 800ml borosilicate press with a double steel mesh filter and a ' +
      'replaceable beaker. Brews four cups without grounds in the cup.',
    priceCents: 3900,
    currency: 'USD',
    category: 'Kitchen',
    imageUrl: 'https://cdn.nexa.example.com/products/nx-press-05.jpg',
    stock: 0,
    rating: 4.1,
  },
  {
    id: 'nx-cable-06',
    name: 'Braided USB-C Cable, 2m',
    blurb: '100W PD, nylon braid',
    description:
      'A two-metre USB-C cable rated for 100W power delivery and 480Mbps ' +
      'data, with a nylon braid and moulded strain relief at both ends.',
    priceCents: 1600,
    currency: 'USD',
    category: 'Accessories',
    imageUrl: 'https://cdn.nexa.example.com/products/nx-cable-06.jpg',
    stock: 130,
    rating: 4.2,
  },
];
