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
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardHeader
} from '@mui/material';
import { 
  Add, 
  Edit, 
  TrendingUp, 
  TrendingDown,
  EmojiEvents
} from '@mui/icons-material';
import { AdminLayout } from '../../components/layout/AdminLayout';
import { PointsService, UserService } from '../../api/services';
import { useLoading } from '../../contexts/LoadingContext';
import type { PointsTransaction, User } from '../../types/api';

/**
 * Points management page component
 * Allows admins to view and manage points transactions and adjustments
 */
const PointsPage: React.FC = () => {
  // State for points transactions
  const [transactions, setTransactions] = useState<PointsTransaction[]>([]);
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // State for leaderboard
  const [leaderboard, setLeaderboard] = useState<User[]>([]);
  
  // State for transaction modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [formData, setFormData] = useState({
    userId: '',
    amount: 100,
    reason: '',
    transactionType: 'adjustment'
  });
  
  // Error handling state
  const [error, setError] = useState<string | null>(null);
  
  // Loading context
  const { setLoading, setLoadingMessage } = useLoading();

  /**
   * Fetch points transactions from API
   */
  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setLoadingMessage('Loading points transactions...');
      setError(null);
      
      const response = await PointsService.getPointsHistory();
      
      if (response && Array.isArray(response)) {
        // Sort transactions by date descending
        const sortedTransactions = [...response].sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        
        setTransactions(sortedTransactions);
        setTotalTransactions(sortedTransactions.length);
      } else {
        setError('Failed to fetch points transactions');
        setTransactions([]);
      }
    } catch (err) {
      setError('An error occurred while fetching points transactions');
      console.error('Error fetching points transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch leaderboard data from API
   */
  const fetchLeaderboard = async () => {
    try {
      const response = await PointsService.getLeaderboard(10);
      
      if (response && Array.isArray(response)) {
        setLeaderboard(response);
      }
    } catch (err) {
      console.error('Error fetching leaderboard:', err);
    }
  };

  /**
   * Fetch users for the dropdown
   */
  const fetchUsers = async () => {
    try {
      const response = await UserService.getUsers(1, 100);
      
      if (response && 'items' in response) {
        setUsers(response.items as User[]);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  /**
   * Handle page change
   */
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  /**
   * Handle rows per page change
   */
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  /**
   * Handle form input changes
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<{ name?: string; value: unknown }>) => {
    const name = e.target.name as string;
    const value = e.target.value;
    
    setFormData({
      ...formData,
      [name]: value
    });
    
    // If user ID changed, find the selected user
    if (name === 'userId') {
      const user = users.find(u => u.id === value);
      setSelectedUser(user || null);
    }
  };

  /**
   * Submit points adjustment
   */
  const handleSubmitAdjustment = async () => {
    if (!formData.userId || !formData.amount || !formData.reason) {
      setError('Please fill in all required fields');
      return;
    }
    
    try {
      setLoading(true);
      setLoadingMessage('Submitting points adjustment...');
      
      const result = await UserService.updateUserPoints(
        formData.userId, 
        formData.amount, 
        formData.reason
      );
      
      if (result && result.success) {
        // Refresh transactions after successful adjustment
        await fetchTransactions();
        await fetchLeaderboard();
        setIsModalOpen(false);
        
        // Reset form
        setFormData({
          userId: '',
          amount: 100,
          reason: '',
          transactionType: 'adjustment'
        });
        setSelectedUser(null);
      } else {
        setError('Failed to update points');
      }
    } catch (err) {
      setError('An error occurred while updating points');
      console.error('Error updating points:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get chip color based on transaction type
   */
  const getTransactionTypeChip = (type: string) => {
    switch (type) {
      case 'earned':
        return { color: 'success' as const, icon: <TrendingUp fontSize="small" /> };
      case 'spent':
        return { color: 'error' as const, icon: <TrendingDown fontSize="small" /> };
      case 'adjusted':
      default:
        return { color: 'warning' as const, icon: <Edit fontSize="small" /> };
    }
  };

  // Calculate points metrics
  const calculateMetrics = () => {
    const totalEarned = transactions
      .filter(t => t.transaction_type === 'earned')
      .reduce((sum, t) => sum + t.amount, 0);
    
    const totalSpent = transactions
      .filter(t => t.transaction_type === 'spent')
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    const totalAdjusted = transactions
      .filter(t => t.transaction_type === 'adjusted')
      .reduce((sum, t) => sum + t.amount, 0);
    
    const totalNet = totalEarned - totalSpent + totalAdjusted;
    
    return { totalEarned, totalSpent, totalAdjusted, totalNet };
  };

  // Fetch data on component mount
  useEffect(() => {
    fetchTransactions();
    fetchLeaderboard();
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Calculate current page of transactions
  const paginatedTransactions = transactions.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Calculate points metrics
  const metrics = calculateMetrics();

  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Points Management
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<Add />}
            onClick={() => setIsModalOpen(true)}
          >
            Add Points Adjustment
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Card>
              <CardHeader
                title="Total Net Points"
                titleTypographyProps={{ variant: 'subtitle1' }}
                sx={{ pb: 0 }}
              />
              <CardContent>
                <Typography variant="h3" color="primary">
                  {metrics.totalNet.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Card>
              <CardHeader
                title="Points Earned"
                titleTypographyProps={{ variant: 'subtitle1' }}
                sx={{ pb: 0 }}
              />
              <CardContent>
                <Typography variant="h3" color="success.main">
                  {metrics.totalEarned.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Card>
              <CardHeader
                title="Points Spent"
                titleTypographyProps={{ variant: 'subtitle1' }}
                sx={{ pb: 0 }}
              />
              <CardContent>
                <Typography variant="h3" color="error.main">
                  {metrics.totalSpent.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Card>
              <CardHeader
                title="Points Adjusted"
                titleTypographyProps={{ variant: 'subtitle1' }}
                sx={{ pb: 0 }}
              />
              <CardContent>
                <Typography variant="h3" color="warning.main">
                  {metrics.totalAdjusted.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 8' } }}>
            <Paper sx={{ width: '100%', overflow: 'hidden' }}>
              <Typography variant="h6" sx={{ p: 2, pb: 0 }}>
                Points Transactions
              </Typography>
              <TableContainer sx={{ maxHeight: 'calc(100vh - 350px)' }}>
                <Table stickyHeader aria-label="points transactions table">
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Related To</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paginatedTransactions.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          <Box sx={{ py: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            {totalTransactions === 0 ? (
                              <Typography>No transactions found</Typography>
                            ) : (
                              <CircularProgress size={32} />
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ) : (
                      paginatedTransactions.map((transaction) => {
                        const typeChip = getTransactionTypeChip(transaction.transaction_type);
                        return (
                          <TableRow key={transaction.id} hover>
                            <TableCell>
                              {transaction.user?.username || transaction.user_id}
                            </TableCell>
                            <TableCell>
                              {new Date(transaction.created_at).toLocaleString()}
                            </TableCell>
                            <TableCell>
                              <Typography
                                sx={{
                                  color: transaction.amount >= 0 ? 'success.main' : 'error.main',
                                  fontWeight: 'bold'
                                }}
                              >
                                {transaction.amount >= 0 ? '+' : ''}{transaction.amount}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                icon={typeChip.icon}
                                label={transaction.transaction_type} 
                                color={typeChip.color}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>{transaction.reason}</TableCell>
                            <TableCell>
                              {transaction.event_id && (
                                <Chip 
                                  label={transaction.event?.title || `Event: ${transaction.event_id}`}
                                  size="small"
                                  variant="outlined"
                                  color="primary"
                                />
                              )}
                              {transaction.badge_id && (
                                <Chip 
                                  label={transaction.badge?.name || `Badge: ${transaction.badge_id}`}
                                  size="small"
                                  variant="outlined"
                                  color="secondary"
                                  icon={<EmojiEvents fontSize="small" />}
                                />
                              )}
                              {!transaction.event_id && !transaction.badge_id && (
                                <Typography variant="body2" color="text.secondary">
                                  Manual adjustment
                                </Typography>
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={totalTransactions}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </Paper>
          </Grid>
          
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Leaderboard
              </Typography>
              
              {leaderboard.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
                  <CircularProgress size={32} />
                </Box>
              ) : (
                <Box>
                  {leaderboard.map((user, index) => (
                    <Box 
                      key={user.id} 
                      sx={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        p: 1,
                        mb: 1,
                        borderRadius: 1,
                        bgcolor: index === 0 ? 'rgba(46, 125, 50, 0.1)' : 'transparent',
                        border: index === 0 ? '1px solid #2E7D32' : '1px solid #e0e0e0',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography 
                          sx={{ 
                            width: 24, 
                            height: 24, 
                            borderRadius: '50%', 
                            bgcolor: index < 3 ? ['#FFD700', '#C0C0C0', '#CD7F32'][index] : '#9e9e9e',
                            color: index < 3 ? (index === 0 ? '#000' : '#fff') : '#fff',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mr: 1,
                            fontWeight: 'bold'
                          }}
                        >
                          {index + 1}
                        </Typography>
                        <Box>
                          <Typography variant="body1">{user.username}</Typography>
                          <Typography variant="body2" color="text.secondary">{user.email}</Typography>
                        </Box>
                      </Box>
                      <Typography variant="h6" color="primary">
                        {user.points?.toLocaleString() || 0}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Points Adjustment Dialog */}
        <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            Add Points Adjustment
          </DialogTitle>
          <DialogContent dividers>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <FormControl fullWidth required>
                <InputLabel id="user-select-label">User</InputLabel>
                <Select
                  labelId="user-select-label"
                  name="userId"
                  value={formData.userId}
                  onChange={(e) => handleInputChange(e as React.ChangeEvent<HTMLInputElement>)}
                  label="User"
                >
                  {users.map((user) => (
                    <MenuItem key={user.id} value={user.id}>
                      {user.username} ({user.email})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                label="Amount"
                name="amount"
                type="number"
                value={formData.amount}
                onChange={(e) => handleInputChange(e)}
                fullWidth
                variant="outlined"
                required
                helperText="Positive value to add points, negative to subtract"
                InputProps={{
                  startAdornment: (
                    <Typography sx={{ mr: 1 }}>
                      {formData.amount >= 0 ? '+' : ''}
                    </Typography>
                  ),
                }}
              />
              
              <TextField
                label="Reason"
                name="reason"
                value={formData.reason}
                onChange={(e) => handleInputChange(e)}
                fullWidth
                variant="outlined"
                required
                multiline
                rows={3}
                placeholder="Explain why points are being adjusted"
              />
              
              {selectedUser && (
                <Alert severity="info" sx={{ mt: 1 }}>
                  <Typography variant="body2">
                    <strong>Current points:</strong> {selectedUser.points || 0}
                  </Typography>
                  <Typography variant="body2">
                    <strong>After adjustment:</strong> {(selectedUser.points || 0) + formData.amount}
                  </Typography>
                </Alert>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleSubmitAdjustment} 
              variant="contained" 
              color="primary"
              disabled={!formData.userId || !formData.reason}
            >
              Submit Adjustment
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default PointsPage;
