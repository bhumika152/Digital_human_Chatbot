// type Props = {
//   label: string;
//   type?: string;
//   placeholder: string;
// };

// export default function Input({
//   label,
//   type = "text",
//   placeholder,
// }: Props) {
//   return (
//     <div className="auth-field">
//       <label>{label}</label>
//       <input type={type} placeholder={placeholder} />
//     </div>
//   );
// }

type Props = {
  label: string;
  type?: string;
  placeholder: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export default function Input({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
}: Props) {
  return (
    <div className="auth-field">
      <label>{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
      />
    </div>
  );
}
