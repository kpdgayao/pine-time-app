import React, { useState, ReactNode, FormEvent } from 'react';
import { Box, Button, CircularProgress, Alert } from '@mui/material';

export interface PineTimeFormProps<T> {
  initialValues: T;
  validate: (values: T) => Partial<Record<keyof T, string>>;
  onSubmit: (values: T) => Promise<void>;
  children: (form: {
    values: T;
    errors: Partial<Record<keyof T, string>>;
    touched: Partial<Record<keyof T, boolean>>;
    handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | { name?: string; value: unknown }>) => void;
    handleBlur: (e: React.FocusEvent<any>) => void;
    setFieldValue: (field: keyof T, value: any) => void;
    isSubmitting: boolean;
  }) => ReactNode;
  submitLabel?: string;
  loading?: boolean;
  error?: string | null;
  success?: string | null;
}

export function PineTimeForm<T extends Record<string, any>>({
  initialValues,
  validate,
  onSubmit,
  children,
  submitLabel = 'Submit',
  loading = false,
  error,
  success,
}: PineTimeFormProps<T>) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name as keyof T]: value }));
    setTouched((prev) => ({ ...prev, [name as keyof T]: true }));
    setErrors((prev) => ({ ...prev, [name as keyof T]: undefined }));
  };

  const handleBlur = (e: React.FocusEvent<any>) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name as keyof T]: true }));
    const validationErrors = validate(values);
    setErrors((prev) => ({ ...prev, [name as keyof T]: validationErrors[name as keyof T] }));
  };

  const setFieldValue = (field: keyof T, value: any) => {
    setValues((prev) => ({ ...prev, [field]: value }));
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    // Validate form values
    const validationErrors = validate(values);
    setErrors(validationErrors);
    // Mark all fields as touched
    setTouched(Object.keys(values).reduce((acc, k) => ({ ...acc, [k]: true }), {}));
    
    // Don't submit if there are validation errors
    if (Object.keys(validationErrors).length > 0) {
      console.log('Form validation failed:', validationErrors);
      return;
    }
    
    // Set submitting state
    setIsSubmitting(true);
    
    try {
      // Wait for the submission to complete
      await onSubmit(values);
      console.log('Form submitted successfully');
    } catch (error) {
      // Log the error but let the parent component handle it via the error prop
      console.error('Form submission error:', error);
      // The error will be displayed through the error prop
    } finally {
      // Always reset the submitting state
      setIsSubmitting(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%', maxWidth: 480, mx: 'auto', p: 2 }}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      {children({ values, errors, touched, handleChange, handleBlur, setFieldValue, isSubmitting })}
      <Button
        type="submit"
        variant="contained"
        color="primary"
        disabled={isSubmitting || loading}
        sx={{ mt: 2, minWidth: 120 }}
        aria-busy={isSubmitting || loading}
      >
        {(isSubmitting || loading) ? <CircularProgress size={24} /> : submitLabel}
      </Button>
    </Box>
  );
}

export default PineTimeForm;
