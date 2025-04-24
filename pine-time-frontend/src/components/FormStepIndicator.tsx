import React from 'react';
import { Stepper, Step, StepLabel } from '@mui/material';

interface FormStepIndicatorProps {
  steps: string[];
  activeStep: number;
}

const FormStepIndicator: React.FC<FormStepIndicatorProps> = ({ steps, activeStep }) => (
  <Stepper activeStep={activeStep} alternativeLabel sx={{ my: 2 }}>
    {steps.map((label, idx) => (
      <Step key={label} completed={activeStep > idx}>
        <StepLabel>{label}</StepLabel>
      </Step>
    ))}
  </Stepper>
);

export default FormStepIndicator;
