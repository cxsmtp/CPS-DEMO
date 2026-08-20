import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { formatMoney } from '../lib/money';
import type { CartTotals } from '../types';
import { colors, radius, spacing } from './theme';

function Row({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <View style={styles.row}>
      <Text style={strong ? styles.strongLabel : styles.label}>{label}</Text>
      <Text style={strong ? styles.strongValue : styles.value}>{value}</Text>
    </View>
  );
}

export function TotalsPanel({ totals }: { totals: CartTotals }) {
  return (
    <View style={styles.panel}>
      <Row label="Subtotal" value={formatMoney(totals.subtotalCents)} />
      <Row
        label="Shipping"
        value={totals.shippingCents === 0 ? 'Free' : formatMoney(totals.shippingCents)}
      />
      <Row label="Tax" value={formatMoney(totals.taxCents)} />
      <View style={styles.divider} />
      <Row label="Total" value={formatMoney(totals.totalCents)} strong />
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: spacing.xs },
  label: { fontSize: 14, color: colors.textMuted },
  value: { fontSize: 14, color: colors.text },
  strongLabel: { fontSize: 16, fontWeight: '700', color: colors.text },
  strongValue: { fontSize: 16, fontWeight: '700', color: colors.text },
  divider: { height: 1, backgroundColor: colors.border, marginVertical: spacing.sm },
});
