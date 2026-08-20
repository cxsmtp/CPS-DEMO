import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import type { Order, Product } from '../types';

export type RootStackParamList = {
  Catalog: undefined;
  Product: { product: Product };
  Cart: undefined;
  Checkout: undefined;
  Confirmation: { order: Order };
};

export type ScreenProps<Route extends keyof RootStackParamList> = NativeStackScreenProps<
  RootStackParamList,
  Route
>;
