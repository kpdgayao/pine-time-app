import React from 'react';
import Button, { ButtonProps } from '@mui/material/Button';
import { styled } from '@mui/material/styles';

const StyledButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius * 1.5,
  fontWeight: 600,
  boxShadow: 'none',
  textTransform: 'none',
  padding: theme.spacing(1.25, 3),
  transition: 'background 0.3s, color 0.3s',
  '&.Mui-disabled': {
    opacity: 0.7,
  },
}));

export type PineTimeButtonVariant = 'primary' | 'secondary' | 'text';

interface PineTimeButtonProps extends ButtonProps {
  variantType?: PineTimeButtonVariant;
}

const PineTimeButton: React.FC<PineTimeButtonProps> = ({ variantType = 'primary', ...props }) => {
  let color: ButtonProps['color'] = 'primary';
  let variant: ButtonProps['variant'] = 'contained';
  if (variantType === 'secondary') color = 'secondary';
  if (variantType === 'text') variant = 'text';
  return <StyledButton color={color} variant={variant} {...props} />;
};

export default PineTimeButton;
