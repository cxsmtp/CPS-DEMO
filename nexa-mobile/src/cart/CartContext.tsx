import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  type ReactNode,
} from 'react';

import type { CartTotals, Product } from '../types';
import {
  cartReducer,
  computeTotals,
  countItems,
  EMPTY_CART,
  type CartState,
} from './reducer';
import { clearStoredCart, loadCart, saveCart } from './storage';

interface CartContextValue {
  state: CartState;
  itemCount: number;
  totals: CartTotals;
  add: (product: Product, quantity?: number) => void;
  setQuantity: (productId: string, quantity: number) => void;
  remove: (productId: string) => void;
  clear: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, EMPTY_CART);
  const hydrated = useRef(false);

  useEffect(() => {
    let cancelled = false;
    void loadCart().then((lines) => {
      if (!cancelled && lines.length > 0) {
        dispatch({ type: 'restore', lines });
      }
      hydrated.current = true;
    });
    return () => {
      cancelled = true;
    };
  }, []);

  // Persist after hydration only, so the initial empty state does not
  // overwrite a cart that is still being read off disk.
  useEffect(() => {
    if (!hydrated.current) return;
    void saveCart(state.lines);
  }, [state.lines]);

  const value = useMemo<CartContextValue>(
    () => ({
      state,
      itemCount: countItems(state),
      totals: computeTotals(state),
      add: (product, quantity = 1) => dispatch({ type: 'add', product, quantity }),
      setQuantity: (productId, quantity) => dispatch({ type: 'setQuantity', productId, quantity }),
      remove: (productId) => dispatch({ type: 'remove', productId }),
      clear: () => {
        dispatch({ type: 'clear' });
        void clearStoredCart();
      },
    }),
    [state],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used inside a CartProvider');
  }
  return context;
}
