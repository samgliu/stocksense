import { PayloadAction, createSlice } from '@reduxjs/toolkit';

import { StockState } from './types';

const initialState: StockState = {
  inputText: '',
  result: null,
  loading: false,
  error: null,
};

export const stockSlice = createSlice({
  name: 'stock',
  initialState,
  reducers: {
    setInputText: (state, action: PayloadAction<string>) => {
      state.inputText = action.payload;
      state.result = null;
      state.error = null;
    },
    setResult: (state, action: PayloadAction<string>) => {
      state.result = action.payload;
      state.loading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearResult: (state) => {
      state.result = null;
      state.error = null;
      state.loading = false;
    },
  },
});

export const { setInputText, setResult, setLoading, setError, clearResult } = stockSlice.actions;

export const stockReducer = stockSlice.reducer;
