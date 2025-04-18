import React from "react";
import { useAuth } from "../contexts/AuthContext";
import { Navigate } from "react-router-dom";

const AdminOnly: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  if (!user || !(user.is_superuser || user.user_type === "admin")) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
};

export default AdminOnly;
