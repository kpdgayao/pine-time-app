import React from 'react';
import Card, { CardProps } from '@mui/material/Card';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: theme.shadows[2],
  background: theme.palette.background.paper,
  transition: 'box-shadow 0.3s',
  padding: theme.spacing(3),
}));

const PineTimeCard: React.FC<CardProps> = ({ children, ...props }) => {
  return <StyledCard {...props}>{children}</StyledCard>;
};

export default PineTimeCard;
