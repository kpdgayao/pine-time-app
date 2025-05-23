import React, { useEffect, useState } from "react";
import api from "../api/client";
import UserEditDialog from "./UserEditDialog";
import {
  Table, TableHead, TableRow, TableCell, TableBody, TablePagination,
  Stack, Alert, Typography
} from '@mui/material';
import PineTimeButton from './PineTimeButton';
import PineTimeCard from './PineTimeCard';
// import { useTheme } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  user_type: string;
}

const PAGE_SIZE = 10;

const AdminUsersSection: React.FC = () => {
  // Remove unused theme variable
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);

  // TODO: Replace with secure token retrieval
  const token: string | null = localStorage.getItem("admin_token");

  const fetchUsers = async (pageVal = page) => {
    try {
      const params: any = { skip: (pageVal - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      const res = await api.get('/users/', {
        params,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (Array.isArray(res.data)) {
        setUsers(res.data);
      } else if (res.data && Array.isArray(res.data.items)) {
        setUsers(res.data.items);
      } else {
        setUsers([]);
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line
  }, [page]);

  // --- UI State ---
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<{[key:number]:boolean}>({});

  // --- Handlers ---
  const handleActivateToggle = async (user: User) => {
    setActionLoading(l => ({ ...l, [user.id]: true }));
    setError(null);
    try {
      // Use the general user update endpoint instead of the specific status endpoint
      await api.put(`/users/${user.id}`, { is_active: !user.is_active }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      fetchUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update user status.');
    } finally {
      setActionLoading(l => ({ ...l, [user.id]: false }));
    }
  };

  const handleEditRole = (user: User) => {
    setSelectedUser(user);
    setEditDialogOpen(true);
  };
  const handleEditDialogSave = () => {
    setEditDialogOpen(false);
    setSelectedUser(null);
    fetchUsers();
  };

  const handleSelectRow = (userId: number) => {
    setSelectedIds(ids => ids.includes(userId) ? ids.filter(id => id !== userId) : [...ids, userId]);
  };
  const handleSelectAll = () => {
    if (selectedIds.length === users.length) setSelectedIds([]);
    else setSelectedIds(users.map(u => u.id));
  };
  const handleBulkAction = async (action: string) => {
    if (!selectedIds.length) return;
    setBulkLoading(true); setError(null);
    try {
      await api.post('/users/bulk_update', { user_ids: selectedIds, action }, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setSelectedIds([]);
      fetchUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Bulk action failed.');
    } finally {
      setBulkLoading(false);
    }
  };

  return (
    <PineTimeCard sx={{ p: 2, mb: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Users</Typography>
        <PineTimeButton variantType="primary" startIcon={<AddIcon />} onClick={() => fetchUsers(1)}>
          Refresh Users
        </PineTimeButton>
      </Stack>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Stack direction="row" spacing={2} mb={2}>
        <PineTimeButton size="small" disabled={bulkLoading || !selectedIds.length} onClick={() => handleBulkAction('activate')}>Bulk Activate</PineTimeButton>
        <PineTimeButton size="small" disabled={bulkLoading || !selectedIds.length} onClick={() => handleBulkAction('deactivate')}>Bulk Deactivate</PineTimeButton>
        <PineTimeButton size="small" color="error" disabled={bulkLoading || !selectedIds.length} onClick={() => handleBulkAction('delete')}>Bulk Delete</PineTimeButton>
        <PineTimeButton size="small" disabled={bulkLoading || !selectedIds.length} onClick={() => handleBulkAction('promote')}>Bulk Promote</PineTimeButton>
        <PineTimeButton size="small" disabled={bulkLoading || !selectedIds.length} onClick={() => handleBulkAction('demote')}>Bulk Demote</PineTimeButton>
      </Stack>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <input
                type="checkbox"
                checked={selectedIds.length === users.length && users.length > 0}
                onChange={handleSelectAll}
                style={{ cursor: 'pointer' }}
              />
            </TableCell>
            <TableCell>Full Name</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Username</TableCell>
            <TableCell>User Type</TableCell>
            <TableCell>Active</TableCell>
            <TableCell>Superuser</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {users.map(user => (
            <TableRow key={user.id} hover>
              <TableCell padding="checkbox">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(user.id)}
                  onChange={() => handleSelectRow(user.id)}
                  style={{ cursor: 'pointer' }}
                />
              </TableCell>
              <TableCell>{user.full_name}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.username}</TableCell>
              <TableCell>{user.user_type}</TableCell>
              <TableCell>{user.is_active ? 'Yes' : 'No'}</TableCell>
              <TableCell>{user.is_superuser ? 'Yes' : 'No'}</TableCell>
              <TableCell align="right">
                <PineTimeButton
                  size="small"
                  variantType={user.is_active ? 'text' : 'primary'}
                  color={user.is_active ? 'warning' : 'success'}
                  disabled={!!actionLoading[user.id]}
                  onClick={() => handleActivateToggle(user)}
                  sx={{ minWidth: 90 }}
                >
                  {actionLoading[user.id] ? '...' : user.is_active ? 'Deactivate' : 'Activate'}
                </PineTimeButton>
                <PineTimeButton
                  size="small"
                  variantType="text"
                  sx={{ ml: 1, minWidth: 90 }}
                  onClick={() => handleEditRole(user)}
                >
                  Edit Role
                </PineTimeButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={users.length}
        page={page - 1}
        onPageChange={(_, newPage) => setPage(newPage + 1)}
        rowsPerPage={PAGE_SIZE}
        rowsPerPageOptions={[PAGE_SIZE]}
      />
      <UserEditDialog
        user={selectedUser}
        open={editDialogOpen}
        onClose={() => { setEditDialogOpen(false); setSelectedUser(null); }}
        onSave={handleEditDialogSave}
      />
    </PineTimeCard>
  );
}

export default AdminUsersSection;
