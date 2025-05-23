import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ADMIN_ROUTES } from '../../config';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * ProtectedRoute component ensures that only authenticated users can access
 * certain routes. If the user is not authenticated, they are redirected to
 * the login page.
 * 
 * @param {React.ReactNode} children - The components to render if authenticated
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();

  // Check if user is authenticated and has admin privileges
  if (!isAuthenticated || !isAdmin) {
    // Redirect to login page with the return url
    return <Navigate to={ADMIN_ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  // User is authenticated, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
