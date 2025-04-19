import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';

interface PineTimeCardProps {
  title: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export default function PineTimeCard({ title, children, style }: PineTimeCardProps) {
  return (
    <Card style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(46, 125, 50, 0.08)', ...style }}>
      <CardContent>
        <Typography variant="h6" color="primary" gutterBottom>
          {title}
        </Typography>
        {children}
      </CardContent>
    </Card>
  );
}
