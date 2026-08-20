import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing } from './theme';

interface QuantityStepperProps {
  quantity: number;
  max: number;
  onChange: (quantity: number) => void;
  label: string;
}

export function QuantityStepper({ quantity, max, onChange, label }: QuantityStepperProps) {
  return (
    <View style={styles.row}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Decrease quantity of ${label}`}
        disabled={quantity <= 0}
        onPress={() => onChange(quantity - 1)}
        style={[styles.step, quantity <= 0 ? styles.stepDisabled : null]}
      >
        <Text style={styles.stepGlyph}>−</Text>
      </Pressable>

      <Text accessibilityLabel={`Quantity ${quantity}`} style={styles.count}>
        {quantity}
      </Text>

      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Increase quantity of ${label}`}
        disabled={quantity >= max}
        onPress={() => onChange(quantity + 1)}
        style={[styles.step, quantity >= max ? styles.stepDisabled : null]}
      >
        <Text style={styles.stepGlyph}>+</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center' },
  step: {
    width: 40,
    height: 40,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepDisabled: { opacity: 0.35 },
  stepGlyph: { fontSize: 20, color: colors.text },
  count: {
    minWidth: 40,
    textAlign: 'center',
    fontSize: 16,
    color: colors.text,
    paddingHorizontal: spacing.xs,
  },
});
