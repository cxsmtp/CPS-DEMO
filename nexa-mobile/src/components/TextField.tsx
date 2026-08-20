import React from 'react';
import { StyleSheet, Text, TextInput, View, type KeyboardTypeOptions } from 'react-native';

import { colors, radius, spacing } from './theme';

interface TextFieldProps {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  error?: string | undefined;
  placeholder?: string;
  autoCapitalize?: 'none' | 'words' | 'characters';
  keyboardType?: KeyboardTypeOptions;
  maxLength?: number;
  textContentType?: 'name' | 'streetAddressLine1' | 'streetAddressLine2' | 'addressCity' | 'addressState' | 'postalCode' | 'countryName';
}

export function TextField({
  label,
  value,
  onChangeText,
  error,
  placeholder,
  autoCapitalize = 'words',
  keyboardType = 'default',
  maxLength = 120,
  textContentType,
}: TextFieldProps) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        autoCapitalize={autoCapitalize}
        autoCorrect={false}
        keyboardType={keyboardType}
        maxLength={maxLength}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.textMuted}
        style={[styles.input, error ? styles.inputError : null]}
        textContentType={textContentType}
        value={value}
      />
      {error ? (
        <Text accessibilityRole="alert" style={styles.error}>
          {error}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  field: { marginBottom: spacing.md },
  label: { fontSize: 13, color: colors.textMuted, marginBottom: spacing.xs },
  input: {
    minHeight: 48,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.md,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.background,
  },
  inputError: { borderColor: colors.danger },
  error: { marginTop: spacing.xs, fontSize: 12, color: colors.danger },
});
