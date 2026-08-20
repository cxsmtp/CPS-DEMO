import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '../components/Button';
import { TotalsPanel } from '../components/TotalsPanel';
import { colors, radius, spacing } from '../components/theme';
import { formatMoney } from '../lib/money';
import type { ScreenProps } from '../navigation/types';

export function ConfirmationScreen({ route, navigation }: ScreenProps<'Confirmation'>) {
  const { order } = route.params;

  return (
    <ScrollView contentContainerStyle={styles.content} style={styles.screen}>
      <Text style={styles.heading}>Order placed</Text>
      <Text style={styles.reference}>Reference {order.id}</Text>

      <View style={styles.card}>
        {order.lines.map((line) => (
          <View key={line.productId} style={styles.line}>
            <Text style={styles.lineName}>
              {line.quantity} × {line.name}
            </Text>
            <Text style={styles.lineValue}>
              {formatMoney(line.unitPriceCents * line.quantity)}
            </Text>
          </View>
        ))}
      </View>

      <TotalsPanel totals={order.totals} />

      <Text style={styles.subheading}>Shipping to</Text>
      <Text style={styles.address}>
        {order.shipTo.fullName}
        {'\n'}
        {order.shipTo.line1}
        {order.shipTo.line2 ? `\n${order.shipTo.line2}` : ''}
        {'\n'}
        {order.shipTo.city}, {order.shipTo.region} {order.shipTo.postalCode}
        {'\n'}
        {order.shipTo.country}
      </Text>

      <View style={styles.done}>
        <Button label="Keep shopping" onPress={() => navigation.popToTop()} />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xl },
  heading: { fontSize: 24, fontWeight: '700', color: colors.text },
  reference: { fontSize: 14, color: colors.textMuted, marginTop: spacing.xs },
  card: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    marginVertical: spacing.md,
  },
  line: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: spacing.xs },
  lineName: { flex: 1, fontSize: 15, color: colors.text, marginRight: spacing.sm },
  lineValue: { fontSize: 15, color: colors.text },
  subheading: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  address: { fontSize: 15, lineHeight: 22, color: colors.text },
  done: { marginTop: spacing.xl },
});
