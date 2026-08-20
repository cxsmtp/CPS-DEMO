import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from 'react-native';

import { fetchCatalog } from '../api/catalog';
import { ProductCard } from '../components/ProductCard';
import { colors, spacing } from '../components/theme';
import { useCart } from '../cart/CartContext';
import type { ScreenProps } from '../navigation/types';
import type { Product } from '../types';

export function CatalogScreen({ navigation }: ScreenProps<'Catalog'>) {
  const [products, setProducts] = useState<Product[]>([]);
  const [offline, setOffline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { itemCount } = useCart();

  const load = useCallback(async (signal?: AbortSignal) => {
    const result = await fetchCatalog(signal);
    if (signal?.aborted) return;
    setProducts(result.products);
    setOffline(result.offline);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [load]);

  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Cart, ${itemCount} item${itemCount === 1 ? '' : 's'}`}
          onPress={() => navigation.navigate('Cart')}
          hitSlop={8}
        >
          <Text style={styles.cartLink}>Cart ({itemCount})</Text>
        </Pressable>
      ),
    });
  }, [navigation, itemCount]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    void load().finally(() => setRefreshing(false));
  }, [load]);

  const openProduct = useCallback(
    (product: Product) => navigation.navigate('Product', { product }),
    [navigation],
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator accessibilityLabel="Loading catalog" color={colors.accent} />
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      {offline ? (
        <Text accessibilityRole="alert" style={styles.notice}>
          Showing the offline catalog — prices and stock may be out of date.
        </Text>
      ) : null}
      <FlatList
        contentContainerStyle={styles.list}
        data={products}
        keyExtractor={(product) => product.id}
        onRefresh={onRefresh}
        refreshing={refreshing}
        renderItem={({ item }) => <ProductCard product={item} onPress={openProduct} />}
        ListEmptyComponent={<Text style={styles.empty}>No products available right now.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  centered: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  list: { padding: spacing.md },
  notice: {
    backgroundColor: colors.surface,
    color: colors.warning,
    fontSize: 13,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: spacing.xl },
  cartLink: { color: colors.accent, fontSize: 16, fontWeight: '600' },
});
