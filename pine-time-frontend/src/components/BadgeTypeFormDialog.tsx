import React, { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Stack, MenuItem } from '@mui/material';
import PineTimeTextField from './PineTimeTextField';
import PineTimeButton from './PineTimeButton';
// Removed custom CSS; all styling is now via MUI theme and components.

export interface BadgeTypeFormValues {
  badge_type: string; // Added field
  name: string;
  description: string;
  level: string;
  criteria_type: string;
  criteria_threshold: number;
  event_type?: string;
  image_url?: string;
}

interface BadgeTypeFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (values: BadgeTypeFormValues) => void;
  initialValues?: Partial<BadgeTypeFormValues>;
  isEdit?: boolean;
  loading: boolean;
}

const BadgeTypeFormDialog: React.FC<BadgeTypeFormDialogProps> = ({
  open,
  onClose,
  onSubmit,
  initialValues = {},
  isEdit = false
}) => {
  const [values, setValues] = useState<BadgeTypeFormValues>({
    badge_type: "", // Added field
    name: "",
    description: "",
    level: "bronze",
    criteria_type: "event_type",
    criteria_threshold: 1,
    event_type: "",
    image_url: ""
  });

  useEffect(() => {
    if (open) {
      setValues({
        badge_type: initialValues.badge_type || "", // Added field
        name: initialValues.name || "",
        description: initialValues.description || "",
        level: initialValues.level || "bronze",
        criteria_type: initialValues.criteria_type || "event_type",
        criteria_threshold: initialValues.criteria_threshold || 1,
        event_type: initialValues.event_type || "",
        image_url: initialValues.image_url || ""
      });
    }
  }, [open, initialValues]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues(v => ({ ...v, [name]: name === "criteria_threshold" ? Number(value) : value }));
  };

  const handleSubmit = () => {
    onSubmit(values);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEdit ? "Edit Badge Type" : "Add Badge Type"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <PineTimeTextField
            label="Badge Type"
            name="badge_type"
            value={values.badge_type}
            onChange={handleChange}
            fullWidth
            required
          />
          <PineTimeTextField
            label="Name"
            name="name"
            value={values.name}
            onChange={handleChange}
            fullWidth
            required
          />
          <PineTimeTextField label="Description" name="description" value={values.description} onChange={handleChange} fullWidth multiline rows={2} variant="outlined" />
          <PineTimeTextField label="Level" name="level" value={values.level} onChange={handleChange} fullWidth select variant="outlined">
            <MenuItem value="bronze">Bronze</MenuItem>
            <MenuItem value="silver">Silver</MenuItem>
            <MenuItem value="gold">Gold</MenuItem>
          </PineTimeTextField>
          <PineTimeTextField label="Criteria Type" name="criteria_type" value={values.criteria_type} onChange={handleChange} fullWidth select variant="outlined">
            <MenuItem value="event_type">Event Type</MenuItem>
            <MenuItem value="attendance">Attendance</MenuItem>
            <MenuItem value="points">Points</MenuItem>
          </PineTimeTextField>
          <PineTimeTextField label="Criteria Threshold" name="criteria_threshold" value={values.criteria_threshold} onChange={handleChange} fullWidth type="number" variant="outlined" />
          <PineTimeTextField label="Event Type (optional)" name="event_type" value={values.event_type} onChange={handleChange} fullWidth variant="outlined" />
          <PineTimeTextField label="Image URL (optional)" name="image_url" value={values.image_url} onChange={handleChange} fullWidth variant="outlined" />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 1, p: 2 }}>
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <PineTimeButton onClick={onClose} variant="outlined">Cancel</PineTimeButton>
          <PineTimeButton onClick={handleSubmit} variant="contained" color="primary">{isEdit ? "Update" : "Create"}</PineTimeButton>
        </Stack>
      </DialogActions>
    </Dialog>
  );
};

export default BadgeTypeFormDialog;
