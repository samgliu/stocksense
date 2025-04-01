import 'react-toastify/dist/ReactToastify.css';

import { ToastContainer } from 'react-toastify';

export const ToastContainerWrapper = () => {
  return (
    <ToastContainer
      position="top-right"
      autoClose={4000}
      hideProgressBar={false}
      newestOnTop
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="light"
    />
  );
};
