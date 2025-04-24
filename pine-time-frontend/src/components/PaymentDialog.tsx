import React, { useState, useEffect } from 'react';
import {
  Typography, Box, Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Stack, IconButton, Stepper, Step, StepLabel,
  CircularProgress, TextField, MenuItem, Select, FormControl, InputLabel, FormHelperText
} from '@mui/material';
import { 
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { Event, Registration } from '../types/events';
import { extractErrorMessage } from '../utils/extractErrorMessage';
import { usePayment } from '../contexts/PaymentContext';

// Define the payment steps
const PAYMENT_STEPS = ['Select Method', 'Enter Details', 'Confirm', 'Process'];

interface PaymentDetails {
  amount: string;
}

interface SubmissionResult {
  success: boolean;
  message: string;
}

type PaymentDialogProps = {
  open: boolean;
  onClose: () => void;
  event: Event | null;
  registrations: Registration[];
  onSuccess: () => void;
};

const PaymentDialog: React.FC<PaymentDialogProps> = ({
  open,
  onClose,
  event,
  registrations,
  onSuccess
}) => {
  // Use the payment context for payment operations
  const { submitPayment, loading: paymentLoading, error: paymentError } = usePayment();
  
  // State for the stepper
  const [activeStep, setActiveStep] = useState(0);
  
  // State for payment method and details
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentDetails, setPaymentDetails] = useState<PaymentDetails>({ amount: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  
  // State for submission result
  const [submissionResult, setSubmissionResult] = useState<SubmissionResult | null>(null);

  // Reset state when dialog opens with a new event
  useEffect(() => {
    if (open && event) {
      setActiveStep(0);
      setPaymentMethod('');
      setPaymentDetails({ amount: event.price ? event.price.toString() : '0' });
      setSubmissionResult(null);
    }
  }, [open, event]);

  const handleCloseDialog = () => {
    // If payment was successful, trigger the success callback
    if (submissionResult?.success) {
      onSuccess();
    }
    onClose();
  };

  // Navigation handlers
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  // Handle payment details changes
  const handlePaymentDetailsChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setPaymentDetails(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Validate payment details
  const validatePaymentDetails = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!paymentDetails.amount || isNaN(Number(paymentDetails.amount)) || Number(paymentDetails.amount) <= 0) {
      errors.amount = "Please enter a valid amount";
    }
    
    if (!paymentMethod) {
      errors.method = "Please select a payment method";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  // Handle payment submission
  const handleSubmitPayment = async () => {
    if (!event) {
      setSubmissionResult({
        success: false,
        message: "Missing event information. Please try again."
      });
      return;
    }
    
    // Find the registration for this event
    const registration = registrations.find(r => r.event_id === event.id && r.status === 'pending');
    
    if (!registration) {
      setSubmissionResult({
        success: false,
        message: "Registration not found. Please try again or contact support."
      });
      return;
    }
    
    // Move to processing step
    setActiveStep(3);
    
    try {
      // Submit payment using the context
      const success = await submitPayment({
        registration_id: registration.id,
        user_id: registration.user_id,
        event_id: event.id,
        amount_paid: Number(paymentDetails.amount),
        payment_channel: paymentMethod,
        payment_date: new Date().toISOString()
      });
      
      if (success) {
        setSubmissionResult({
          success: true,
          message: "Your payment has been submitted successfully! An admin will verify your payment shortly."
        });
      } else {
        setSubmissionResult({
          success: false,
          message: paymentError || "There was an error processing your payment. Please try again."
        });
      }
    } catch (err) {
      const errorMessage = extractErrorMessage(err);
      setSubmissionResult({
        success: false,
        message: errorMessage || "An unexpected error occurred. Please try again."
      });
    }
  };

  if (!event) return null;

  return (
    <Dialog 
      open={open} 
      onClose={handleCloseDialog} 
      maxWidth="sm" 
      fullWidth
      aria-labelledby="payment-dialog-title"
    >
      <DialogTitle id="payment-dialog-title">
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Submit Payment</Typography>
          <IconButton aria-label="close" onClick={handleCloseDialog}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 4, mt: 2 }}>
          {PAYMENT_STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {/* Step 0: Select Payment Method */}
        {activeStep === 0 && (
          <Stack spacing={3} sx={{ py: 2 }}>
            <Typography variant="h6" align="center">
              Select Payment Method
            </Typography>
            
            <Typography variant="body2" align="center" color="text.secondary">
              Event: <strong>{event.title}</strong><br />
              Registration Fee: <strong>₱{event.price || 0}</strong>
            </Typography>
            
            <FormControl fullWidth error={!!formErrors.method}>
              <InputLabel id="payment-method-label">Payment Method</InputLabel>
              <Select
                labelId="payment-method-label"
                value={paymentMethod}
                label="Payment Method"
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                <MenuItem value="GCash">GCash</MenuItem>
                <MenuItem value="Maya">Maya</MenuItem>
                <MenuItem value="InstaPay">InstaPay</MenuItem>
                <MenuItem value="Bank Transfer">Bank Transfer</MenuItem>
                <MenuItem value="Cash">Cash</MenuItem>
              </Select>
              {formErrors.method && (
                <FormHelperText>{formErrors.method}</FormHelperText>
              )}
            </FormControl>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <img
                src="/instapay-qr.jpg"
                alt="Payment QR Code"
                style={{ 
                  width: 180, 
                  height: 180, 
                  borderRadius: 8, 
                  border: '1px solid #ccc',
                  display: paymentMethod ? 'block' : 'none'
                }}
              />
            </Box>
          </Stack>
        )}
        
        {/* Step 1: Enter Payment Details */}
        {activeStep === 1 && (
          <Stack spacing={3} sx={{ py: 2 }}>
            <Typography variant="h6" align="center">
              Enter Payment Details
            </Typography>
            
            <Typography variant="body2" align="center" color="text.secondary">
              Method: <strong>{paymentMethod}</strong>
            </Typography>
            
            <TextField
              label="Amount Paid"
              name="amount"
              type="number"
              value={paymentDetails.amount}
              onChange={handlePaymentDetailsChange}
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>₱</Typography>,
              }}
              fullWidth
              error={!!formErrors.amount}
              helperText={formErrors.amount}
            />
            

          </Stack>
        )}
        
        {/* Step 2: Confirm Payment */}
        {activeStep === 2 && (
          <Stack spacing={3} sx={{ py: 2 }}>
            <Typography variant="h6" align="center">
              Confirm Payment Details
            </Typography>
            
            <Box sx={{ 
              border: '1px solid #e0e0e0', 
              borderRadius: 2, 
              p: 2,
              bgcolor: '#f5f5f5'
            }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Event:</Typography>
                  <Typography variant="body2" fontWeight="bold">{event.title}</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Registration Fee:</Typography>
                  <Typography variant="body2" fontWeight="bold">₱{event.price || 0}</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Payment Method:</Typography>
                  <Typography variant="body2" fontWeight="bold">{paymentMethod}</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Amount Paid:</Typography>
                  <Typography variant="body2" fontWeight="bold">₱{paymentDetails.amount}</Typography>
                </Box>
                

              </Stack>
            </Box>
            
            <Typography variant="body2" color="text.secondary" align="center">
              Please confirm that the details above are correct. Once submitted, an admin will verify your payment.
            </Typography>
          </Stack>
        )}
        
        {/* Step 3: Processing/Result */}
        {activeStep === 3 && (
          <Stack spacing={3} sx={{ py: 4, alignItems: 'center' }}>
            {!submissionResult ? (
              <>
                <CircularProgress size={60} />
                <Typography variant="h6" align="center">
                  Processing Payment
                </Typography>
                <Typography variant="body2" align="center" color="text.secondary">
                  Please wait while we process your payment...
                </Typography>
              </>
            ) : submissionResult.success ? (
              <>
                <CheckCircleIcon color="success" sx={{ fontSize: 60 }} />
                <Typography variant="h6" align="center" color="success.main">
                  Payment Submitted Successfully!
                </Typography>
                <Typography variant="body2" align="center">
                  {submissionResult.message}
                </Typography>
              </>
            ) : (
              <>
                <ErrorIcon color="error" sx={{ fontSize: 60 }} />
                <Typography variant="h6" align="center" color="error">
                  Payment Submission Failed
                </Typography>
                <Typography variant="body2" align="center">
                  {submissionResult.message}
                </Typography>
              </>
            )}
          </Stack>
        )}
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3 }}>
        {/* Navigation buttons based on current step */}
        {activeStep === 0 && (
          <Button 
            variant="contained" 
            onClick={() => {
              if (!paymentMethod) {
                setFormErrors({ method: "Please select a payment method" });
                return;
              }
              setActiveStep(1);
            }}
            fullWidth
          >
            Next
          </Button>
        )}
        
        {activeStep === 1 && (
          <>
            <Button onClick={handleBack} sx={{ mr: 1 }}>
              Back
            </Button>
            <Button 
              variant="contained" 
              onClick={() => {
                if (validatePaymentDetails()) {
                  setActiveStep(2);
                }
              }}
            >
              Next
            </Button>
          </>
        )}
        
        {activeStep === 2 && (
          <>
            <Button onClick={handleBack} sx={{ mr: 1 }}>
              Back
            </Button>
            <Button 
              variant="contained" 
              onClick={handleSubmitPayment}
              disabled={paymentLoading}
            >
              {paymentLoading ? 'Submitting...' : 'Submit Payment'}
            </Button>
          </>
        )}
        
        {activeStep === 3 && submissionResult && (
          <Button 
            variant="contained" 
            onClick={handleCloseDialog}
            fullWidth
          >
            Close
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default PaymentDialog;
