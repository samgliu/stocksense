import { RootState } from '@/app/store';

export const selectStockInput = (state: RootState) => state.stock.inputText;
export const selectStockResult = (state: RootState) => state.stock.result;
export const selectStockLoading = (state: RootState) => state.stock.loading;
export const selectStockError = (state: RootState) => state.stock.error;
