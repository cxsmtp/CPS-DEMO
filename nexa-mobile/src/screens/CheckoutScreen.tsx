import React, { useRef, useState } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, View } from 'react-native';

import { placeOrder } from '../api/catalog';
import { Button } from '../components/Button';
import { TextField } from '../components/TextField';
import { TotalsPanel } from '../components/TotalsPanel';
import { colors, spacing } from '../components/theme';
import { useCart } from '../cart/CartContext';
import { newIdempotencyKey } from '../lib/ids';
import {
  emptyAddress,
  hasErrors,
  normalizeSpace,
  validateAddress,
  type FieldErrors,
} from '../lib/validation';
import type { ScreenProps } from '../navigation/types';
import type { ShippingAddress } from '../types';

export function CheckoutScreen({ navigation }: ScreenProps<'Checkout'>) {
  const { state, totals, clear } = useCart();
  const [address, setAddress] = useState<ShippingAddress>(emptyAddress);
  const [errors, setErrors] = useState<FieldErrors<ShippingAddress>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Held across retries so a resubmitted checkout resolves to one order
  // rather than two.
  const idempotencyKey = useRef(newIdempotencyKey());

  const field = (key: keyof ShippingAddress) => (value: string) =>
    setAddress((current) => ({ ...current, [key]: value }));

  const submit = async () => {
    const trimmed: ShippingAddress = {
      fullName: normalizeSpace(address.fullName),
      line1: normalizeSpace(address.line1),
      line2: normalizeSpace(address.line2),
      city: normalizeSpace(address.city),
      region: normalizeSpace(address.region),
      postalCode: normalizeSpace(address.postalCode).toUpperCase(),
      country: normalizeSpace(address.country).toUpperCase(),
    };

    const found = validateAddress(trimmed);
    setErrors(found);
    if (hasErrors(found)) return;

    setSubmitError(null);
    setSubmitting(true);
    try {
      const order = await placeOrder({
        lines: state.lines.map((line) => ({
          productId: line.product.id,
          quantity: line.quantity,
        })),
        shipTo: trimmed,
        idempotencyKey: idempotencyKey.current,
      });
      clear();
      navigation.replace('Confirmation', { order });
    } catch {
      setSubmitError('We could not place your order. Check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={styles.screen}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.heading}>Shipping address</Text>

        <TextField
          label="Full name"
          value={address.fullName}
          onChangeText={field('fullName')}
          error={errors.fullName}
          textContentType="name"
        />
        <TextField
          label="Address"
          value={address.line1}
          onChangeText={field('line1')}
          error={errors.line1}
          textContentType="streetAddressLine1"
        />
        <TextField
          label="Apartment, suite (optional)"
          value={address.line2}
          onChangeText={field('line2')}
          textContentType="streetAddressLine2"
        />
        <TextField
          label="City"
          value={address.city}
          onChangeText={field('city')}
          error={errors.city}
          textContentType="addressCity"
        />
        <TextField
          label="State or region"
          value={address.region}
          onChangeText={field('region')}
          error={errors.region}
          textContentType="addressState"
        />
        <TextField
          label="Postal code"
          value={address.postalCode}
          onChangeText={field('postalCode')}
          error={errors.postalCode}
          autoCapitalize="characters"
          maxLength={10}
          textContentType="postalCode"
        />
        <TextField
          label="Country code"
          value={address.country}
          onChangeText={field('country')}
          error={errors.country}
          autoCapitalize="characters"
          maxLength={2}
          textContentType="countryName"
        />

        <Text style={styles.heading}>Order summary</Text>
        <TotalsPanel totals={totals} />

        <Text style={styles.paymentNote}>
          Payment is collected by the hosted checkout after this step. Card details are never
          entered in, or stored by, this app.
        </Text>

        {submitError ? (
          <Text accessibilityRole="alert" style={styles.error}>
            {submitError}
          </Text>
        ) : null}

        <View style={styles.submit}>
          <Button
            label="Place order"
            onPress={() => void submit()}
            busy={submitting}
            disabled={state.lines.length === 0}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xl },
  heading: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
    marginTop: spacing.sm,
    marginBottom: spacing.md,
  },
  paymentNote: {
    fontSize: 13,
    lineHeight: 19,
    color: colors.textMuted,
    marginTop: spacing.md,
  },
  error: { marginTop: spacing.md, fontSize: 14, color: colors.danger },
  submit: { marginTop: spacing.lg },
});
