import { toast } from "react-toastify";

export const confirmToast = (
  message: string,
  onConfirm: () => void
) => {
  toast(
    ({ closeToast }) => (
      <div>
        <p className="mb-2">{message}</p>

        <div className="flex justify-end gap-2">
          <button
            onClick={() => {
              onConfirm();
              closeToast();
            }}
            className="bg-red-600 text-white px-3 py-1 rounded text-sm"
          >
            Delete
          </button>

          <button
            onClick={closeToast}
            className="bg-gray-700 text-white px-3 py-1 rounded text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    ),
    {
      autoClose: false,
      closeOnClick: false,
    }
  );
};
