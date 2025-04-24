import React from 'react';
import { 
  Typography, Box, TextField, Select, MenuItem,
  FormControl, InputLabel, Slider
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import dayjs from 'dayjs';

export type EventFilterProps = {
  search: string;
  setSearch: (value: string) => void;
  eventType: string;
  setEventType: (value: string) => void;
  location: string;
  setLocation: (value: string) => void;
  dateRange: [dayjs.Dayjs | null, dayjs.Dayjs | null];
  setDateRange: (range: [dayjs.Dayjs | null, dayjs.Dayjs | null]) => void;
  priceRange: [number, number];
  setPriceRange: (range: [number, number]) => void;
  sortBy: string;
  setSortBy: (value: string) => void;
  eventTypes: string[];
  minPrice: number;
  maxPrice: number;
};

const EventFilters: React.FC<EventFilterProps> = ({
  search, setSearch,
  eventType, setEventType,
  location, setLocation,
  dateRange, setDateRange,
  priceRange, setPriceRange,
  sortBy, setSortBy,
  eventTypes,
  minPrice,
  maxPrice
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: { xs: 'wrap', sm: 'nowrap' },
        gap: { xs: 1.5, sm: 2 },
        mb: { xs: 2, sm: 3 },
        alignItems: 'center',
        background: { xs: 'transparent', sm: 'background.surface' },
        px: { xs: 0, sm: 2 },
        py: { xs: 0, sm: 1 },
        borderRadius: { xs: 0, sm: 2 },
        boxShadow: { xs: 'none', sm: 1 },
        position: 'relative',
      }}
    >
      <TextField
        label="Search"
        value={search}
        onChange={e => setSearch(e.target.value)}
        size="small"
        sx={{ flex: { xs: '1 1 100%', sm: '0 1 180px' } }}
      />
      <Select
        value={eventType}
        onChange={e => setEventType(e.target.value as string)}
        displayEmpty
        size="small"
        sx={{ minWidth: 120 }}
      >
        <MenuItem value="">All Types</MenuItem>
        {eventTypes.map(type => (
          <MenuItem key={type} value={type}>{type}</MenuItem>
        ))}
      </Select>
      <DatePicker
        label="Start Date"
        value={dateRange[0]}
        onChange={date => setDateRange([date, dateRange[1]])}
        slotProps={{ textField: { size: 'small' } }}
      />
      <DatePicker
        label="End Date"
        value={dateRange[1]}
        onChange={date => setDateRange([dateRange[0], date])}
        slotProps={{ textField: { size: 'small' } }}
      />
      <TextField
        label="Location"
        value={location}
        onChange={e => setLocation(e.target.value)}
        size="small"
        sx={{ flex: { xs: '1 1 100%', sm: '0 1 160px' } }}
      />
      <Box sx={{ minWidth: 160, px: { xs: 0, sm: 1 } }}>
        <Typography variant="body2" sx={{ mb: 0.5 }}>Price Range</Typography>
        <Slider
          value={priceRange}
          min={minPrice}
          max={maxPrice}
          step={10}
          onChange={(_, val) => {
            if (Array.isArray(val) && val.length === 2) {
              setPriceRange([val[0], val[1]]);
            }
          }}
          valueLabelDisplay="auto"
          size="small"
        />
      </Box>
      <FormControl size="small" sx={{ minWidth: 140 }}>
        <InputLabel id="sort-by-label">Sort By</InputLabel>
        <Select
          labelId="sort-by-label"
          value={sortBy}
          label="Sort By"
          onChange={e => setSortBy(e.target.value as string)}
        >
          <MenuItem value="start-soonest">Start Date (Soonest)</MenuItem>
          <MenuItem value="start-latest">Start Date (Latest)</MenuItem>
          <MenuItem value="title-az">Event Title (A-Z)</MenuItem>
          <MenuItem value="price-low">Price (Low to High)</MenuItem>
          <MenuItem value="price-high">Price (High to Low)</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );
};

export default EventFilters;
