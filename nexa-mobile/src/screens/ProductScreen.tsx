import React, { useState } from 'react';
import { Image, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '../components/Button';
import { QuantityStepper } from '../components/QuantityStepper';
import { colors, radius, spacing } from '../components/theme';
import { useCart } from '../cart/CartContext';
import { MAX_LINE_QUANTITY } from '../cart/reducer';
import { formatMoney } from '../lib/money';
import type { ScreenProps } from '../navigation/types';

export function ProductScreen({ route, navigation }: ScreenProps<'Product'>) {
  const { product } = route.params;
  const { add } = useCart();
  const orderable = Math.min(product.stock, MAX_LINE_QUANTITY);
  const [quantity, setQuantity] = useState(orderable > 0 ? 1 : 0);

  const addToCart = () => {
    add(product, quantity);
    navigation.navigate('Cart');
  };

  return (
    <ScrollView contentContainerStyle={styles.content} style={styles.screen}>
      <Image
        accessibilityIgnoresInvertColors
        source={{ uri: product.imageUrl }}
        style={styles.hero}
        resizeMode="cover"
      />

      <Text style={styles.name}>{product.name}</Text>
      <Text style={styles.category}>{product.category}</Text>
      <Text style={styles.price}>{formatMoney(product.priceCents, product.currency)}</Text>
      <Text style={styles.description}>{product.description}</Text>

      <View style={styles.stockRow}>
        {product.stock === 0 ? (
          <Text style={styles.soldOut}>Sold out</Text>
        ) : (
          <Text style={styles.stock}>{product.stock} in stock</Text>
        )}
        <Text style={styles.rating}>{product.rating.toFixed(1)} / 5</Text>
      </View>

      {orderable > 0 ? (
        <View style={styles.controls}>
          <QuantityStepper
            quantity={quantity}
            max={orderable}
            onChange={setQuantity}
            label={product.name}
          />
          <View style={styles.addButton}>
            <Button
              label={`Add to cart · ${formatMoney(product.priceCents * quantity, product.currency)}`}
              onPress={addToCart}
              disabled={quantity <= 0}
            />
          </View>
        </View>
      ) : (
        <Button label="Sold out" onPress={() => undefined} disabled />
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xl },
  hero: {
    width: '100%',
    height: 240,
    borderRadius: radius.md,
    backgroundColor: colors.surface,
    marginBottom: spacing.md,
  },
  name: { fontSize: 22, fontWeight: '700', color: colors.text },
  category: { fontSize: 13, color: colors.textMuted, marginTop: spacing.xs },
  price: { fontSize: 20, fontWeight: '600', color: colors.text, marginTop: spacing.sm },
  description: { fontSize: 15, lineHeight: 22, color: colors.text, marginTop: spacing.md },
  stockRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.md,
    marginBottom: spacing.lg,
  },
  stock: { fontSize: 13, color: colors.textMuted },
  soldOut: { fontSize: 13, color: colors.danger, fontWeight: '600' },
  rating: { fontSize: 13, color: colors.textMuted },
  controls: { flexDirection: 'row', alignItems: 'center' },
  addButton: { flex: 1, marginLeft: spacing.md },
});
