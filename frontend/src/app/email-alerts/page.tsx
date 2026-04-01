"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type Subscription = {
  id: number;
  user_id: number;
  email: string;
  notify_restock: boolean;
  notify_withdraw: boolean;
  notify_low_stock: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user_name: string | null;
  user_role: string | null;
};

export default function EmailAlertsPage() {
  const router = useRouter();

  const [userRole, setUserRole] = useState("");
  const [mySubs, setMySubs] = useState<Subscription[]>([]);
  const [allSubs, setAllSubs] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Form state
  const [email, setEmail] = useState("");
  const [notifyRestock, setNotifyRestock] = useState(true);
  const [notifyWithdraw, setNotifyWithdraw] = useState(true);
  const [notifyLowStock, setNotifyLowStock] = useState(true);
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");

  const isManager = userRole === "manager";

  const fetchData = async () => {
    try {
      const [meRes, mySubsRes] = await Promise.all([
        api.get("/api/v1/auth/me"),
        api.get("/api/v1/email-subscriptions/me"),
      ]);
      setUserRole(meRes.data.role);
      setMySubs(mySubsRes.data);

      if (meRes.data.role === "manager") {
        const allRes = await api.get("/api/v1/email-subscriptions");
        setAllSubs(allRes.data);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setFormSuccess("");

    if (!email.trim()) {
      setFormError("Please enter an email address.");
      return;
    }

    if (!notifyRestock && !notifyWithdraw && !notifyLowStock) {
      setFormError("Please select at least one notification type.");
      return;
    }

    try {
      await api.post("/api/v1/email-subscriptions", {
        email: email.trim(),
        notify_restock: notifyRestock,
        notify_withdraw: notifyWithdraw,
        notify_low_stock: notifyLowStock,
      });
      setFormSuccess("Email subscription added successfully!");
      setEmail("");
      setNotifyRestock(true);
      setNotifyWithdraw(true);
      setNotifyLowStock(true);
      fetchData();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Failed to create subscription.";
      setFormError(message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Remove this email subscription?")) return;
    try {
      await api.delete(`/api/v1/email-subscriptions/${id}`);
      fetchData();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Failed to delete subscription.";
      alert(message);
    }
  };

  const handleToggle = async (sub: Subscription, field: string) => {
    try {
      await api.put(`/api/v1/email-subscriptions/${sub.id}`, {
        [field]: !(sub as unknown as Record<string, boolean>)[field],
      });
      fetchData();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Failed to update subscription.";
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

  if (error) {
    return (
      <main className="min-h-screen p-8 bg-gray-50">
        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-red-600">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Email Alert Subscriptions</h1>
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

      {/* Subscribe Form */}
      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Add Email Subscription</h2>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">
                Email Address
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border rounded-lg px-3 py-2 w-full"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">
                Notification Types
              </label>
              <div className="flex flex-wrap gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifyRestock}
                    onChange={(e) => setNotifyRestock(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span>Restock Notifications</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifyWithdraw}
                    onChange={(e) => setNotifyWithdraw(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span>Withdraw Notifications</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifyLowStock}
                    onChange={(e) => setNotifyLowStock(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span>Low Stock Alerts</span>
                </label>
              </div>
            </div>
          </div>

          {formError && (
            <p className="text-red-600 text-sm mt-3">{formError}</p>
          )}
          {formSuccess && (
            <p className="text-green-600 text-sm mt-3">{formSuccess}</p>
          )}

          <button
            type="submit"
            className="bg-black text-white px-6 py-2 rounded-lg mt-4"
          >
            Subscribe
          </button>
        </form>
      </div>

      {/* My Subscriptions */}
      <div className="bg-white rounded-xl shadow overflow-hidden mb-6">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">My Subscriptions</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-4">Email</th>
                <th className="p-4 text-center">Restock</th>
                <th className="p-4 text-center">Withdraw</th>
                <th className="p-4 text-center">Low Stock</th>
                <th className="p-4 text-center">Active</th>
                <th className="p-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mySubs.length > 0 ? (
                mySubs.map((sub) => (
                  <tr key={sub.id} className="border-t">
                    <td className="p-4">{sub.email}</td>
                    <td className="p-4 text-center">
                      <input
                        type="checkbox"
                        checked={sub.notify_restock}
                        onChange={() => handleToggle(sub, "notify_restock")}
                        className="w-4 h-4 cursor-pointer"
                      />
                    </td>
                    <td className="p-4 text-center">
                      <input
                        type="checkbox"
                        checked={sub.notify_withdraw}
                        onChange={() => handleToggle(sub, "notify_withdraw")}
                        className="w-4 h-4 cursor-pointer"
                      />
                    </td>
                    <td className="p-4 text-center">
                      <input
                        type="checkbox"
                        checked={sub.notify_low_stock}
                        onChange={() => handleToggle(sub, "notify_low_stock")}
                        className="w-4 h-4 cursor-pointer"
                      />
                    </td>
                    <td className="p-4 text-center">
                      <input
                        type="checkbox"
                        checked={sub.is_active}
                        onChange={() => handleToggle(sub, "is_active")}
                        className="w-4 h-4 cursor-pointer"
                      />
                    </td>
                    <td className="p-4">
                      <button
                        onClick={() => handleDelete(sub.id)}
                        className="bg-red-600 text-white px-3 py-1 rounded"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="p-4" colSpan={6}>
                    No subscriptions yet. Add one above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manager: All Subscriptions */}
      {isManager && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">
              All Subscriptions (Manager View)
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {allSubs.length} total subscriptions
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-4">User</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Email</th>
                  <th className="p-4 text-center">Restock</th>
                  <th className="p-4 text-center">Withdraw</th>
                  <th className="p-4 text-center">Low Stock</th>
                  <th className="p-4 text-center">Active</th>
                  <th className="p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {allSubs.length > 0 ? (
                  allSubs.map((sub) => (
                    <tr key={sub.id} className="border-t">
                      <td className="p-4">{sub.user_name || "-"}</td>
                      <td className="p-4">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            sub.user_role === "manager"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {sub.user_role || "-"}
                        </span>
                      </td>
                      <td className="p-4">{sub.email}</td>
                      <td className="p-4 text-center">
                        {sub.notify_restock ? "Yes" : "No"}
                      </td>
                      <td className="p-4 text-center">
                        {sub.notify_withdraw ? "Yes" : "No"}
                      </td>
                      <td className="p-4 text-center">
                        {sub.notify_low_stock ? "Yes" : "No"}
                      </td>
                      <td className="p-4 text-center">
                        {sub.is_active ? (
                          <span className="text-green-600 font-medium">
                            Yes
                          </span>
                        ) : (
                          <span className="text-red-600 font-medium">No</span>
                        )}
                      </td>
                      <td className="p-4">
                        <button
                          onClick={() => handleDelete(sub.id)}
                          className="bg-red-600 text-white px-3 py-1 rounded"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="p-4" colSpan={8}>
                      No subscriptions found.
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
