import { showToast } from '@/features/toast/store/slice';
import { useAppDispatch } from './useAppDispatch';

export const useToast = () => {
  const dispatch = useAppDispatch();
  return {
    success: (msg: string) => dispatch(showToast({ message: msg, type: 'success' })),
    error: (msg: string) => dispatch(showToast({ message: msg, type: 'error' })),
    info: (msg: string) => dispatch(showToast({ message: msg, type: 'info' })),
    warn: (msg: string) => dispatch(showToast({ message: msg, type: 'warning' })),
  };
};
