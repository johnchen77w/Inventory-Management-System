"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type Employee = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
};

export default function EmployeesPage() {
  const router = useRouter();

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [userRole, setUserRole] = useState("");
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isManager = userRole === "manager";

  const fetchData = async () => {
    try {
      const meRes = await api.get("/api/v1/auth/me");
      setUserRole(meRes.data.role);
      setCurrentUserId(meRes.data.id);

      if (meRes.data.role === "manager") {
        const usersRes = await api.get("/api/v1/users");
        setEmployees(usersRes.data);
      } else {
        setError("Only managers can view the employee list.");
      }
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Failed to load data.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    fetchData();
  }, [router]);

  const handleDelete = async (emp: Employee) => {
    if (emp.id === currentUserId) {
      alert("You cannot remove yourself.");
      return;
    }
    if (
      !window.confirm(
        `Are you sure you want to remove ${emp.full_name} (${emp.email})?`
      )
    )
      return;

    try {
      await api.delete(`/api/v1/users/${emp.id}`);
      fetchData();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Failed to remove employee.";
      alert(message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("token_type");
    router.replace("/login");
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Employees</h1>
        <div className="flex gap-3">
          <button
            onClick={() => router.push("/dashboard")}
            className="border px-4 py-2 rounded-lg bg-white"
          >
            Back to Dashboard
          </button>
          <button
            onClick={handleLogout}
            className="bg-black text-white px-4 py-2 rounded-lg"
          >
            Logout
          </button>
        </div>
      </div>

      {error ? (
        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-red-600">{error}</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">All Employees</h2>
            <p className="text-sm text-gray-600 mt-1">
              {employees.length} total
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-4">ID</th>
                  <th className="p-4">Name</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Joined</th>
                  {isManager && <th className="p-4">Actions</th>}
                </tr>
              </thead>
              <tbody>
                {employees.length > 0 ? (
                  employees.map((emp) => (
                    <tr key={emp.id} className="border-t">
                      <td className="p-4">{emp.id}</td>
                      <td className="p-4">{emp.full_name}</td>
                      <td className="p-4">{emp.email}</td>
                      <td className="p-4">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            emp.role === "manager"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {emp.role === "staff" ? "Worker" : "Manager"}
                        </span>
                      </td>
                      <td className="p-4">
                        {emp.is_active ? (
                          <span className="text-green-600 font-medium">
                            Active
                          </span>
                        ) : (
                          <span className="text-red-600 font-medium">
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="p-4 text-sm text-gray-600">
                        {new Date(emp.created_at).toLocaleDateString()}
                      </td>
                      {isManager && (
                        <td className="p-4">
                          {emp.id !== currentUserId ? (
                            <button
                              onClick={() => handleDelete(emp)}
                              className="bg-red-600 text-white px-3 py-1 rounded"
                            >
                              Remove
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm">You</span>
                          )}
                        </td>
                      )}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="p-4" colSpan={7}>
                      No employees found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  );
}
