import React, { useState } from "react";
import { useAdminEventRegistrations } from "../hooks/useAdminEventRegistrations";

interface Props {
  eventId: number | undefined;
  open: boolean;
  onClose: () => void;
}

const PAGE_SIZE = 10;

const AdminEventRegistrationsModal: React.FC<Props> = ({ eventId, open, onClose }) => {
  const [page, setPage] = useState(1);
  const { items, total, approved, attendance_rate, revenue, loading, error, refetch } = useAdminEventRegistrations(eventId, page, PAGE_SIZE);

  const totalPages = total ? Math.ceil(total / PAGE_SIZE) : 1;

  if (!open) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Event Registrations</h2>
        <div className="summary-row">
          <span><b>Total Registrations:</b> {total ?? 0}</span>
          <span><b>Approved:</b> {approved ?? 0}</span>
          <span><b>Attendance Rate:</b> {attendance_rate ?? 0}%</span>
          <span><b>Revenue:</b> ₱{revenue?.toLocaleString() ?? 0}</span>
        </div>
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && (
          <>
            <table className="registrations-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Status</th>
                  <th>Payment</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {items && items.length > 0 ? (
                  items.map((reg) => (
                    <tr key={reg.id}>
                      <td>{reg.id}</td>
                      <td>{reg.user?.full_name || reg.user_id}</td>
                      <td>{reg.status}</td>
                      <td>{reg.payment_status}</td>
                      <td>{new Date(reg.registration_date).toLocaleString()}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} style={{ textAlign: "center" }}>
                      No registrations found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            <div className="pagination-row">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>Prev</button>
              <span>Page {page} of {totalPages}</span>
              <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</button>
            </div>
          </>
        )}
        <div className="modal-actions">
          <button onClick={refetch}>Refresh</button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
      <style>{`
        .modal-overlay {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .modal-content {
          background: #fff;
          border-radius: 8px;
          max-width: 800px;
          width: 90vw;
          padding: 2rem;
          box-shadow: 0 2px 16px rgba(0,0,0,0.15);
        }
        .summary-row {
          display: flex;
          gap: 2rem;
          margin-bottom: 1rem;
        }
        .registrations-table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 1rem;
        }
        .registrations-table th, .registrations-table td {
          border: 1px solid #ddd;
          padding: 0.5rem 0.75rem;
        }
        .registrations-table th {
          background: #f6f6f6;
        }
        .loading {
          text-align: center;
          margin: 2rem 0;
        }
        .error {
          color: #c00;
          margin-bottom: 1rem;
        }
        .pagination-row {
          display: flex;
          align-items: center;
          gap: 1rem;
          justify-content: center;
          margin-bottom: 1rem;
        }
        .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
        }
      `}</style>
    </div>
  );
};

export default AdminEventRegistrationsModal;
