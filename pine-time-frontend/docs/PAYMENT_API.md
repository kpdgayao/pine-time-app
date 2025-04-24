# Pine Time Payment API Reference

## Overview

This document provides a technical reference for the Pine Time payment system's API interactions, hook usage, and component props. Use this as a developer reference when maintaining or extending the payment functionality.

## API Endpoints

### Submit Payment

```http
POST /payments/payments/register
```

**Request Body:**

```typescript
interface PaymentRequest {
  registration_id: number;  // ID of the registration being paid for
  user_id: number;          // ID of the user making the payment
  event_id: number;         // ID of the event being paid for
  amount_paid: number;      // Amount paid (numeric)
  payment_channel: string;  // Payment method/channel used
  payment_date?: string;    // Optional payment date (ISO format)
}
```

**Headers:**

- `Authorization: Bearer ${token}` - User authentication token

**Response:**

- `200 OK` - Payment successfully registered
- `400 Bad Request` - Invalid payment details
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Registration not found
- `500 Server Error` - Internal server error

**Error Response Format:**

```json
{
  "error": "Error message describing the issue"
}
```

## Hook Reference

### usePayment

Provides payment-related functionality through a dedicated hook and context.

**Payment-Related Functions:**

```typescript
/**
 * Fetch payment records for a specific user
 * @param userId - The ID of the user to fetch payments for
 */
fetchPaymentRecords(userId: number): Promise<void>;

/**
 * Submit a new payment
 * @param paymentData - Payment submission data
 * @returns Promise resolving to success status
 */
submitPayment(paymentData: PaymentSubmission): Promise<boolean>;

/**
 * Check if a registration has been paid
 * @param eventId - The event ID
 * @param registrationId - The registration ID
 * @returns Boolean indicating if the registration is paid
 */
isRegistrationPaid(eventId: number, registrationId: number): boolean;

/**
 * Get payment details for a specific registration
 * @param eventId - The event ID
 * @param registrationId - The registration ID
 * @returns Payment record if found, null otherwise
 */
getPaymentDetails(eventId: number, registrationId: number): PaymentRecord | null;
```

**Data Types:**

```typescript
// Payment record structure matching database schema
interface PaymentRecord {
  id: number;
  registration_id: number;
  user_id: number;
  event_id: number;
  amount_paid: number;
  payment_channel: string;
  payment_date: string;
}

// Payment submission data
interface PaymentSubmission {
  registration_id: number;
  user_id: number;
  event_id: number;
  amount_paid: number;
  payment_channel: string;
  payment_date?: string;
}
```

### useEventRegistration

Handles registration, unregistration, and payment-related operations.

```typescript
/**
 * Returns registration state and functions
 */
interface EventRegistrationHook {
  state: {
    loading: number | null; // Event ID currently loading or null
    error: string | null;   // Error message if any
  };
  register: (eventId: number) => Promise<boolean>; // Returns success status
  unregister: (eventId: number) => Promise<boolean>;
  cancelPending: (eventId: number) => Promise<boolean>;
}
```

## Component Props Reference

### PaymentDialog

```typescript
interface PaymentDialogProps {
  open: boolean;        // Whether dialog is open
  onClose: () => void;  // Handler for close event
  event: Event | null;  // Event being paid for
  registrations: Registration[]; // All user registrations
  onSuccess: () => void; // Callback after successful payment
}
```

### EventCard

```typescript
interface EventCardProps {
  event: Event;
  registration?: Registration;
  loading?: number | null;
  onRegister: (id: number) => void;
  onUnregister: (id: number) => void;
  onCancelPending: (id: number) => void;
  onPayNow?: (id: number) => void;
  handleOpenDialog?: (event: Event) => void;
  highlight?: boolean;
  dimmed?: boolean;
  sx?: any;
}
```

### EventList

```typescript
interface EventListProps {
  title: string;
  events: Event[];
  getRegistration: (event: Event) => Registration | undefined;
  loading: number | null;
  onRegister: (eventId: number) => void;
  onUnregister: (eventId: number) => void;
  onCancelPending: (eventId: number) => void;
  onPayNow: (eventId: number) => void;
  onOpenDetails: (event: Event) => void;
  highlight?: boolean;
  dimmed?: boolean;
}
```

## Type Definitions

### Event

```typescript
interface Event {
  id: number;
  title: string;
  description: string;
  start_time: string; // ISO date string
  end_time: string;   // ISO date string
  location: string;
  max_participants: number;
  registration_count?: number;
  registration_deadline?: string;
  event_type: string;
  price: number;
  host?: string;
  image_url?: string;
}
```

### Registration

```typescript
interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  registration_date: string; // ISO date string
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  payment_status: 'pending' | 'paid';
  amount_paid?: number;
}
```

### PaymentDetails

```typescript
interface PaymentDetails {
  id: number;
  registration_id: number;
  amount_paid: number;
  payment_date: string; // ISO date string
  payment_channel: string;
  verification_status: 'pending' | 'verified' | 'rejected';
}
```

## Best Practices

1. **Type Safety**:

   ```typescript
   // Always use optional chaining when accessing potentially undefined properties
   const price = event?.price ?? 0;
   
   // Use type guards to ensure objects exist before operations
   if (registration && eventId) {
     markRegistrationAsPaid(eventId, registration.id);
   }
   ```

2. **Error Handling**:

   ```typescript
   try {
     await api.post('/payments/payments/register', paymentData);
     // Success handling
   } catch (error) {
     // Extract meaningful error message
     const errorMessage = extractErrorMessage(error);
     setPaymentMsg(`❌ ${errorMessage}`);
   }
   ```

3. **Proper State Management**:

   ```typescript
   // Close dialog first, then clear state to prevent UI flicker
   const handleClosePaymentDialog = () => {
     setShowPaymentDialog(false);
     setTimeout(() => {
       setLastRegisteredEventId(null);
       setPaymentEvent(null);
     }, 100);
   };
   ```

## Testing Guide

### Unit Testing Payment Status

```typescript
test('isRegistrationPaid returns correct payment status', () => {
  // Setup
  localStorage.setItem('pine-time-paid-registrations', JSON.stringify({
    '1-2': true,
    '3-4': true
  }));
  
  const { isRegistrationPaid } = useEvents();
  
  // Test
  expect(isRegistrationPaid(1, 2)).toBe(true);
  expect(isRegistrationPaid(3, 4)).toBe(true);
  expect(isRegistrationPaid(5, 6)).toBe(false);
});
```

### Integration Testing Payment Flow

```typescript
test('Pay Now button disappears after payment submission', async () => {
  // Setup component with mock data
  render(<EventCard event={mockEvent} isPaid={false} />);
  
  // Initial state check
  expect(screen.getByText('Pay Now')).toBeInTheDocument();
  
  // Simulate payment
  fireEvent.click(screen.getByText('Pay Now'));
  // Complete payment dialog actions
  
  // After payment check
  render(<EventCard event={mockEvent} isPaid={true} />);
  expect(screen.queryByText('Pay Now')).not.toBeInTheDocument();
  expect(screen.getByText('Payment Submitted')).toBeInTheDocument();
});
```
