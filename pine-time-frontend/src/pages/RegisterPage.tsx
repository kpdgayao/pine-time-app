import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, TextField, Button, InputAdornment, IconButton, CircularProgress, Checkbox, FormControlLabel, Link, LinearProgress, Dialog, DialogTitle, DialogContent } from '@mui/material';
import { Visibility, VisibilityOff, Person, Lock, Email as EmailIcon, Close as CloseIcon } from '@mui/icons-material';
// If you see a type error for 'react-markdown', run: npm install react-markdown
import ReactMarkdown from 'react-markdown';
import api from '../api/client';
import { useToast } from '../contexts/ToastContext';

function getPasswordStrength(password: string): { label: string, value: number, color: 'error' | 'warning' | 'success' } {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  if (score === 0) return { label: 'Weak', value: 10, color: 'error' };
  if (score === 1) return { label: 'Weak', value: 25, color: 'error' };
  if (score === 2) return { label: 'Fair', value: 50, color: 'warning' };
  if (score === 3) return { label: 'Good', value: 75, color: 'success' };
  return { label: 'Strong', value: 100, color: 'success' };
}

const RegisterPage: React.FC = () => {
  const { showToast } = useToast();
  // Modal state and markdown content
  const [showLegalModal, setShowLegalModal] = useState<null | 'terms' | 'privacy'>(null);
  const [legalContent, setLegalContent] = useState('');

  // Import the terms and privacy content directly
  const termsAndPrivacyContent = `# Pine Time Experiences — Terms and Privacy Policy

## Consent and Waiver

By participating in Pine Time Experiences events, including trivia nights organized in partnership with our venue providers, you agree to the following:

- **Event Rules**: You agree to abide by all event rules and instructions provided by Pine Time Experiences, our venue providers, their personnel, and partners.
- **Photography**: You understand and consent that photographs and videos taken during the event may be used for promotional purposes by Pine Time Experiences and our venue providers.
- **Assumption of Risk**: You acknowledge the risks and hazards associated with participation in trivia night events. By joining, you voluntarily assume these risks and hazards.
- **Waiver of Claims**: You hereby WAIVE any claim against Pine Time Experiences, our venue providers, their personnel, partners, and affiliates for any untoward incident resulting from your negligence and/or failure to follow the rules set out by the event organizers and their personnel.

## Privacy Policy

- **Data Collection**: We collect only the information necessary for event registration and participation. This may include your name, email, and contact details.
- **Use of Data**: Your information will be used solely for event management, communication, and, where applicable, promotional purposes (such as event photos).
- **Data Sharing**: We do not sell or share your personal data with third parties, except as required for event operations or by law.
- **Photo/Video Consent**: Event media may be shared on social media and promotional materials. If you do not wish to appear in photos or videos, please inform event staff upon arrival.
- **Data Security**: We take reasonable precautions to protect your information. However, no method of transmission over the Internet or electronic storage is 100% secure.
- **Contact**: For questions about this policy, please contact Pine Time Experiences via the official website or event staff.

By registering, you acknowledge that you have read, understood, and agreed to these terms, including the consent and waiver above.`;

  React.useEffect(() => {
    if (showLegalModal) {
      // Use the hardcoded content instead of fetching
      setLegalContent(termsAndPrivacyContent);
    }
  }, [showLegalModal]);
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  // const [msg, setMsg] = useState('');
  // const [error, setError] = useState('');

  const passwordStrength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // setMsg('');
    // setError('');
    if (!fullName || !username || !email || !password || !confirmPassword) {
      showToast('❗ Please fill in all fields, including your full name.', 'warning');
      return;
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      showToast('❗ Please enter a valid email address.', 'warning');
      return;
    }
    if (password !== confirmPassword) {
      showToast('❗ Passwords do not match.', 'warning');
      return;
    }
    if (passwordStrength.value < 50) {
      showToast('❗ Password is too weak.', 'warning');
      return;
    }
    if (!acceptTerms) {
      showToast('❗ You must accept the terms and privacy policy.', 'warning');
      return;
    }
    setLoading(true);
    try {
      // Ensure we're using the correct API path that works in both environments
      // The api.ts utility will handle path normalization
      await api.post('/users/register', { full_name: fullName, username, email, password }, { timeout: 15000 });
      console.log('Registration request successful');
      showToast('✅ Registration successful! You can now log in. 🌲', 'success');
      setUsername('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setAcceptTerms(false);
    } catch (err: any) {
      console.error('Registration error:', err);
      let message = 'Registration failed.';
      const data = err.response?.data;
      if (typeof data === 'string') {
        message = data;
      } else if (Array.isArray(data)) {
        message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
      } else if (typeof data === 'object' && data !== null) {
        message = data.detail || data.msg || JSON.stringify(data);
      }
      showToast(`❌ Registration failed: ${message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" bgcolor="#f7f7f7">
      <Card sx={{ minWidth: 340, boxShadow: 3 }}>
        <CardContent>
          <Typography variant="h5" align="center" gutterBottom>Register</Typography>
          <form onSubmit={handleSubmit} autoComplete="on">
            <TextField
              label="Full Name"
              value={fullName}
              onChange={e => setFullName(e.target.value)}
              fullWidth
              required
              margin="normal"
              autoFocus
            />
            <TextField
              label="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              fullWidth
              required
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              label="Email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              fullWidth
              required
              margin="normal"
              type="email"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              fullWidth
              required
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword((show) => !show)}
                      edge="end"
                      size="large"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              helperText={<span>Password must be at least 8 characters, include a number, uppercase letter, and special character.</span>}
            />
            <Box sx={{ width: '100%', mb: 1 }}>
              <LinearProgress
                variant="determinate"
                value={passwordStrength.value}
                color={passwordStrength.color}
                sx={{ height: 7, borderRadius: 4 }}
              />
              <Typography variant="caption" color={passwordStrength.color === 'error' ? 'error' : passwordStrength.color === 'warning' ? 'warning.main' : 'success.main'}>
                {passwordStrength.label}
              </Typography>
            </Box>
            <TextField
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              fullWidth
              required
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle confirm password visibility"
                      onClick={() => setShowConfirmPassword((show) => !show)}
                      edge="end"
                      size="large"
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              error={!!confirmPassword && password !== confirmPassword}
              helperText={!!confirmPassword && password !== confirmPassword ? 'Passwords do not match' : ''}
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={acceptTerms}
                  onChange={e => setAcceptTerms(e.target.checked)}
                  color="success"
                  required
                />
              }
              label={<span>I accept the <Link href="#" onClick={e => { e.preventDefault(); setShowLegalModal('terms'); }}>terms</Link> and <Link href="#" onClick={e => { e.preventDefault(); setShowLegalModal('privacy'); }}>privacy policy</Link>.</span>}
              sx={{ mt: 1, mb: 1 }}
            />

            <Button
              type="submit"
              variant="contained"
              color="success"
              fullWidth
              disabled={loading}
              sx={{ mt: 1, mb: 1 }}
              aria-label="register"
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Register'}
            </Button>
            <Box display="flex" justifyContent="flex-end" alignItems="center">
              <Link href="/login" underline="hover" fontSize={14}>
                Back to Login
              </Link>
            </Box>
          </form>
        </CardContent>
      </Card>
      {/* Legal Modal Dialog */}
      <Dialog
        open={!!showLegalModal}
        onClose={() => setShowLegalModal(null)}
        maxWidth="sm"
        fullWidth
        aria-labelledby="legal-dialog-title"
      >
        <DialogTitle id="legal-dialog-title">
          {showLegalModal === 'terms' ? 'Terms and Conditions' : 'Privacy Policy'}
          <IconButton
            aria-label="close"
            onClick={() => setShowLegalModal(null)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers sx={{ maxHeight: 500, overflowY: 'auto' }}>
          <ReactMarkdown>{legalContent}</ReactMarkdown>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default RegisterPage;
