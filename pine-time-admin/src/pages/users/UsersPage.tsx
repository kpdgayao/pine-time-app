import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress
} from '@mui/material';
import { Edit, Add } from '@mui/icons-material';
import AdminLayout from '../../components/layout/AdminLayout';
import { UserService } from '../../api/services';
import { useLoading } from '../../contexts/LoadingContext';
import type { User } from '../../types/api';

/**
 * Users management page component
 * Allows admins to view, edit, and manage user accounts
 */
const UsersPage: React.FC = () => {
  // State for users data and pagination
  const [users, setUsers] = useState<User[]>([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // State for user edit modal
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [userFormData, setUserFormData] = useState<Partial<User>>({});
  
  // Error handling state
  const [error, setError] = useState<string | null>(null);
  
  // Loading context for managing loading states
  const { setLoading, setLoadingMessage } = useLoading();

  /**
   * Fetch users data from API
   */
  const fetchUsers = async () => {
    try {
      setLoading(true);
      setLoadingMessage('Loading users...');
      setError(null);
      
      const response = await UserService.getUsers(page + 1, rowsPerPage);
      
      if (response && 'items' in response) {
        setUsers(response.items as User[]);
        setTotalUsers(response.total);
      } else {
        setError('Failed to fetch users data');
        setUsers([]);
      }
    } catch (err) {
      setError('An error occurred while fetching users data');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle page change in pagination
   */
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  /**
   * Handle rows per page change in pagination
   */
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  /**
   * Open edit modal for a user
   */
  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setUserFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      is_active: user.is_active,
      is_superuser: user.is_superuser,
      role: user.role
    });
    setIsEditModalOpen(true);
  };

  /**
   * Handle form input changes
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked, type } = e.target;
    setUserFormData({
      ...userFormData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  /**
   * Submit user edit form
   */
  const handleSubmitUserEdit = async () => {
    if (!selectedUser) return;
    
    try {
      setLoading(true);
      setLoadingMessage('Updating user...');
      
      const updatedUser = await UserService.updateUser(selectedUser.id, userFormData);
      
      if (updatedUser) {
        setUsers(users.map(user => 
          user.id === selectedUser.id ? { ...user, ...updatedUser } : user
        ));
        setIsEditModalOpen(false);
        setSelectedUser(null);
      } else {
        setError('Failed to update user');
      }
    } catch (err) {
      setError('An error occurred while updating user');
      console.error('Error updating user:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch users when page or rowsPerPage changes
  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage]);

  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Users Management
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<Add />}
            onClick={() => {
              setSelectedUser(null);
              setUserFormData({});
              setIsEditModalOpen(true);
            }}
          >
            Add User
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: 'calc(100vh - 280px)' }}>
            <Table stickyHeader aria-label="users table">
              <TableHead>
                <TableRow>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Full Name</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell>Points</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Box sx={{ py: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        {totalUsers === 0 ? (
                          <Typography>No users found</Typography>
                        ) : (
                          <CircularProgress size={32} />
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  users.map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.full_name || '-'}</TableCell>
                      <TableCell>
                        <Chip 
                          label={user.role} 
                          color={user.is_superuser ? 'secondary' : 'primary'} 
                          size="small" 
                          variant={user.is_superuser ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={user.is_active ? 'Active' : 'Inactive'} 
                          color={user.is_active ? 'success' : 'error'} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(user.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{user.points || 0}</TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={() => handleEditUser(user)}>
                          <Edit fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={totalUsers}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>

        {/* User Edit Dialog */}
        <Dialog open={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {selectedUser ? 'Edit User' : 'Create New User'}
          </DialogTitle>
          <DialogContent dividers>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <TextField
                label="Username"
                name="username"
                value={userFormData.username || ''}
                onChange={handleInputChange}
                fullWidth
                variant="outlined"
                required
              />
              <TextField
                label="Email"
                name="email"
                type="email"
                value={userFormData.email || ''}
                onChange={handleInputChange}
                fullWidth
                variant="outlined"
                required
              />
              <TextField
                label="Full Name"
                name="full_name"
                value={userFormData.full_name || ''}
                onChange={handleInputChange}
                fullWidth
                variant="outlined"
              />
              <TextField
                label="Role"
                name="role"
                value={userFormData.role || ''}
                onChange={handleInputChange}
                fullWidth
                variant="outlined"
              />
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      name="is_active"
                      checked={userFormData.is_active || false}
                      onChange={handleInputChange}
                      color="success"
                    />
                  }
                  label="Active"
                />
                <FormControlLabel
                  control={
                    <Switch
                      name="is_superuser"
                      checked={userFormData.is_superuser || false}
                      onChange={handleInputChange}
                      color="secondary"
                    />
                  }
                  label="Admin"
                />
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleSubmitUserEdit} 
              variant="contained" 
              color="primary"
            >
              {selectedUser ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default UsersPage;
