import { PayloadAction, createSlice } from '@reduxjs/toolkit';

import { toast } from 'react-toastify';

type ToastPayload = {
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
};

const toastSlice = createSlice({
  name: 'toast',
  initialState: {},
  reducers: {
    showToast: (_, action: PayloadAction<ToastPayload>) => {
      const { message, type = 'info' } = action.payload;
      toast[type](message);
    },
  },
});

export const { showToast } = toastSlice.actions;
export const toastReducer = toastSlice.reducer;
