
import Button, { ButtonProps } from '@mui/material/Button';

export default function PineTimeButton(props: ButtonProps) {
  return (
    <Button
      variant="contained"
      color="primary"
      style={{ borderRadius: 8, textTransform: 'none', fontWeight: 600 }}
      {...props}
    />
  );
}
