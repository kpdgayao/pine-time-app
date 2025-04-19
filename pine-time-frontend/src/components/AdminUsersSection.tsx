import React, { useEffect, useState } from "react";
import api from "../api/client";
import UserPointsBadgesDialog from "./UserPointsBadgesDialog";

import {
  Table, TableHead, TableRow, TableCell, TableBody, TablePagination,
  Paper, Stack, Button, CircularProgress, Alert, IconButton, Typography
} from '@mui/material';
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

  return (
    <Paper sx={{ p: 2, mb: 2 }} elevation={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Users</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => fetchUsers(1)}>
          Refresh Users
        </Button>
      </Stack>
      <Table size="small">
        <TableHead>
          <TableRow>
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
              <TableCell>{user.full_name}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.username}</TableCell>
              <TableCell>{user.user_type}</TableCell>
              <TableCell>{user.is_active ? 'Yes' : 'No'}</TableCell>
              <TableCell>{user.is_superuser ? 'Yes' : 'No'}</TableCell>
              <TableCell align="right">
                <Button size="small" onClick={() => fetchUsers(1)}>
                  Refresh
                </Button>
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
    </Paper>
  );
}

export default AdminUsersSection;
