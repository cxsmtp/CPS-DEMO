import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'nexa.session.token';

/**
 * The session token lives in the platform keystore (Keychain on iOS,
 * EncryptedSharedPreferences on Android) rather than AsyncStorage, which is
 * plain unencrypted JSON on disk.
 */
export async function readSessionToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch {
    return null;
  }
}

export async function writeSessionToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token, {
    keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  });
}

export async function clearSessionToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}
