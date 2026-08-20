import React from 'react';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { Button } from '../components/Button';
import { QuantityStepper } from '../components/QuantityStepper';
import { TotalsPanel } from '../components/TotalsPanel';
import { colors, spacing } from '../components/theme';
import { useCart } from '../cart/CartContext';
import { lineTotal, MAX_LINE_QUANTITY } from '../cart/reducer';
import { formatMoney } from '../lib/money';
import type { ScreenProps } from '../navigation/types';

export function CartScreen({ navigation }: ScreenProps<'Cart'>) {
  const { state, totals, setQuantity, remove } = useCart();

  if (state.lines.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Your cart is empty.</Text>
        <Button label="Browse the catalog" variant="secondary" onPress={() => navigation.navigate('Catalog')} />
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <FlatList
        contentContainerStyle={styles.list}
        data={state.lines}
        keyExtractor={(line) => line.product.id}
        renderItem={({ item }) => (
          <View style={styles.line}>
            <View style={styles.lineHeader}>
              <Text numberOfLines={1} style={styles.lineName}>
                {item.product.name}
              </Text>
              <Text style={styles.lineTotal}>
                {formatMoney(lineTotal(item), item.product.currency)}
              </Text>
            </View>
            <Text style={styles.unitPrice}>
              {formatMoney(item.product.priceCents, item.product.currency)} each
            </Text>
            <View style={styles.lineControls}>
              <QuantityStepper
                quantity={item.quantity}
                max={Math.min(item.product.stock, MAX_LINE_QUANTITY)}
                onChange={(quantity) => setQuantity(item.product.id, quantity)}
                label={item.product.name}
              />
              <Pressable
                accessibilityRole="button"
                accessibilityLabel={`Remove ${item.product.name} from cart`}
                onPress={() => remove(item.product.id)}
                hitSlop={8}
              >
                <Text style={styles.remove}>Remove</Text>
              </Pressable>
            </View>
          </View>
        )}
      />

      <View style={styles.footer}>
        <TotalsPanel totals={totals} />
        <View style={styles.checkout}>
          <Button label="Checkout" onPress={() => navigation.navigate('Checkout')} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.lg },
  emptyText: { fontSize: 16, color: colors.textMuted, marginBottom: spacing.md },
  list: { padding: spacing.md },
  line: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.md,
  },
  lineHeader: { flexDirection: 'row', justifyContent: 'space-between' },
  lineName: { flex: 1, fontSize: 16, fontWeight: '600', color: colors.text, marginRight: spacing.sm },
  lineTotal: { fontSize: 16, fontWeight: '600', color: colors.text },
  unitPrice: { fontSize: 13, color: colors.textMuted, marginTop: spacing.xs },
  lineControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  remove: { fontSize: 14, color: colors.danger, fontWeight: '600' },
  footer: { padding: spacing.md, borderTopWidth: 1, borderTopColor: colors.border },
  checkout: { marginTop: spacing.md },
});
