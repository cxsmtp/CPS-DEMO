import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';

import { formatMoney } from '../lib/money';
import type { Product } from '../types';
import { colors, radius, spacing } from './theme';

interface ProductCardProps {
  product: Product;
  onPress: (product: Product) => void;
}

export function ProductCard({ product, onPress }: ProductCardProps) {
  const soldOut = product.stock === 0;

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${product.name}, ${formatMoney(product.priceCents, product.currency)}`}
      onPress={() => onPress(product)}
      style={({ pressed }) => [styles.card, pressed ? styles.pressed : null]}
    >
      <Image
        accessibilityIgnoresInvertColors
        source={{ uri: product.imageUrl }}
        style={styles.image}
        resizeMode="cover"
      />
      <View style={styles.body}>
        <Text numberOfLines={1} style={styles.name}>
          {product.name}
        </Text>
        <Text numberOfLines={2} style={styles.blurb}>
          {product.blurb}
        </Text>
        <View style={styles.footer}>
          <Text style={styles.price}>{formatMoney(product.priceCents, product.currency)}</Text>
          {soldOut ? <Text style={styles.soldOut}>Sold out</Text> : null}
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  pressed: { opacity: 0.9 },
  image: { width: 96, height: 96, backgroundColor: colors.surface },
  body: { flex: 1, padding: spacing.md, justifyContent: 'space-between' },
  name: { fontSize: 16, fontWeight: '600', color: colors.text },
  blurb: { fontSize: 13, color: colors.textMuted, marginTop: spacing.xs },
  footer: { flexDirection: 'row', alignItems: 'center', marginTop: spacing.sm },
  price: { fontSize: 15, fontWeight: '600', color: colors.text },
  soldOut: { marginLeft: spacing.sm, fontSize: 12, color: colors.danger, fontWeight: '600' },
});
