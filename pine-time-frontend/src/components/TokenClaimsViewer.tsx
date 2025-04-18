import React from "react";
import { useAuth } from "../contexts/AuthContext";

const TokenClaimsViewer: React.FC = () => {
  const { getTokenClaims } = useAuth();
  const claims = getTokenClaims();

  return (
    <div style={{ margin: "16px 0", background: "#222", color: "#fff", borderRadius: 8, padding: 16 }}>
      <h3 style={{ margin: 0, fontSize: 20 }}>Token Claims</h3>
      <pre style={{ margin: 0, fontSize: 14, background: "#111", padding: 8, borderRadius: 4, overflowX: "auto" }}>
        {claims ? JSON.stringify(claims, null, 2) : "No token found."}
      </pre>
    </div>
  );
};

export default TokenClaimsViewer;
