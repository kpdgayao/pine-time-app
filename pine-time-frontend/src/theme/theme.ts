import { createTheme, ThemeOptions, Theme } from '@mui/material/styles';

// Pine Time Green
const PRIMARY_MAIN = '#2E7D32';
const PRIMARY_LIGHT = '#60ad5e';
const PRIMARY_DARK = '#005005';
const PRIMARY_CONTRAST = '#fff';

// Accent Yellow
const SECONDARY_MAIN = '#FFC107';
const SECONDARY_LIGHT = '#FFF350';
const SECONDARY_DARK = '#C79100';
const SECONDARY_CONTRAST = '#222';

// Other colors
const ERROR_MAIN = '#D32F2F';
const WARNING_MAIN = '#FFA000';
const INFO_MAIN = '#0288D1';
const SUCCESS_MAIN = '#388E3C';

// Greys
const GREY_50 = '#FAFAFA';
const GREY_100 = '#F5F5F5';
const GREY_200 = '#EEEEEE';
const GREY_300 = '#E0E0E0';
const GREY_800 = '#222';
const GREY_900 = '#111';

// Spacing scale (multiples of 4)
export const spacing = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48];

// Elevation (Material style)
export const elevation = [
  'none',
  '0px 1px 3px rgba(46, 125, 50, 0.12)',
  '0px 2px 8px rgba(46, 125, 50, 0.18)',
  '0px 4px 16px rgba(46, 125, 50, 0.20)',
  '0px 8px 32px rgba(46, 125, 50, 0.22)',
];

// Typography
const typography = {
  fontFamily: 'Roboto, Arial, sans-serif',
  fontWeightRegular: 400,
  fontWeightMedium: 500,
  fontWeightBold: 700,
  h1: { fontWeight: 700, fontSize: '2.5rem', letterSpacing: '-0.01562em' },
  h2: { fontWeight: 600, fontSize: '2rem', letterSpacing: '-0.00833em' },
  h3: { fontWeight: 500, fontSize: '1.5rem' },
  h4: { fontWeight: 500, fontSize: '1.25rem' },
  h5: { fontWeight: 500, fontSize: '1.125rem' },
  h6: { fontWeight: 500, fontSize: '1rem' },
  subtitle1: { fontSize: '1rem', fontWeight: 400 },
  subtitle2: { fontSize: '0.875rem', fontWeight: 400 },
  body1: { fontSize: '1rem' },
  body2: { fontSize: '0.875rem' },
  button: { textTransform: 'none' as const, fontWeight: 500 },
  caption: { fontSize: '0.75rem', fontWeight: 400 },
  overline: { fontSize: '0.75rem', fontWeight: 400, letterSpacing: '0.08em', textTransform: 'uppercase' as const },
};

const lightPalette = {
  mode: 'light' as const,
  primary: {
    main: PRIMARY_MAIN,
    light: PRIMARY_LIGHT,
    dark: PRIMARY_DARK,
    contrastText: PRIMARY_CONTRAST,
  },
  secondary: {
    main: SECONDARY_MAIN,
    light: SECONDARY_LIGHT,
    dark: SECONDARY_DARK,
    contrastText: SECONDARY_CONTRAST,
  },
  error: { main: ERROR_MAIN },
  warning: { main: WARNING_MAIN },
  info: { main: INFO_MAIN },
  success: { main: SUCCESS_MAIN },
  background: {
    default: GREY_50,
    paper: '#fff',
    surface: GREY_100,
  },
  text: {
    primary: GREY_800,
    secondary: '#1b3a2b',
    disabled: GREY_300,
  },
  divider: GREY_200,
};

const darkPalette = {
  mode: 'dark' as const,
  primary: {
    main: PRIMARY_MAIN,
    light: PRIMARY_LIGHT,
    dark: PRIMARY_DARK,
    contrastText: PRIMARY_CONTRAST,
  },
  secondary: {
    main: SECONDARY_MAIN,
    light: SECONDARY_LIGHT,
    dark: SECONDARY_DARK,
    contrastText: SECONDARY_CONTRAST,
  },
  error: { main: ERROR_MAIN },
  warning: { main: WARNING_MAIN },
  info: { main: INFO_MAIN },
  success: { main: SUCCESS_MAIN },
  background: {
    default: GREY_900,
    paper: '#232323',
    surface: '#181818',
  },
  text: {
    primary: '#fff',
    secondary: GREY_300,
    disabled: GREY_800,
  },
  divider: GREY_800,
};

// Component variants and overrides
const componentOverrides: ThemeOptions['components'] = {
  MuiButton: {
    styleOverrides: {
      root: {
        textTransform: 'none',
        borderRadius: 8,
        fontWeight: 600,
        boxShadow: 'none',
        transition: 'background 0.3s, color 0.3s',
      },
      containedPrimary: {
        backgroundColor: PRIMARY_MAIN,
        color: PRIMARY_CONTRAST,
        '&:hover': {
          backgroundColor: PRIMARY_DARK,
        },
      },
      containedSecondary: {
        backgroundColor: SECONDARY_MAIN,
        color: SECONDARY_CONTRAST,
        '&:hover': {
          backgroundColor: SECONDARY_DARK,
        },
      },
      text: {
        color: PRIMARY_MAIN,
        '&:hover': {
          backgroundColor: 'rgba(46,125,50,0.08)',
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 16,
        boxShadow: elevation[2],
        transition: 'box-shadow 0.3s',
      },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 16,
        padding: spacing[5],
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        background: '#fff',
        borderRadius: 8,
        '& .MuiOutlinedInput-root': {
          '& fieldset': {
            borderColor: PRIMARY_MAIN,
          },
          '&:hover fieldset': {
            borderColor: PRIMARY_DARK,
          },
          '&.Mui-focused fieldset': {
            borderColor: SECONDARY_MAIN,
          },
        },
      },
    },
  },
};

// Export light and dark themes
export const lightTheme: Theme = createTheme({
  palette: lightPalette,
  typography,
  spacing: 4,
  shape: { borderRadius: 8 },
  components: componentOverrides,
});

export const darkTheme: Theme = createTheme({
  palette: darkPalette,
  typography,
  spacing: 4,
  shape: { borderRadius: 8 },
  components: componentOverrides,
});

// Helper to get theme by mode
export const getTheme = (mode: 'light' | 'dark'): Theme => (mode === 'dark' ? darkTheme : lightTheme);


