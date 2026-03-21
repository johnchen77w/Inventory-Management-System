"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type User = {
  email: string;
  full_name: string;
  role: string;
};

type ItemsResponse = {
  items: unknown[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
};

type Category = {
  id: number;
  name: string;
};

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [totalItems, setTotalItems] = useState(0);
  const [totalCategories, setTotalCategories] = useState(0);
  const [lowStockCount, setLowStockCount] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.replace("/login");
      return;
    }

    const fetchDashboardData = async () => {
      try {
        const [userRes, itemsRes, categoriesRes, lowStockRes] = await Promise.all([
          api.get("/api/v1/auth/me"),
          api.get("/api/v1/items", {
            params: {
              page: 1,
              per_page: 20,
              sort_by: "updated_at",
              order: "desc",
              below_threshold: false,
            },
          }),
          api.get("/api/v1/categories"),
          api.get("/api/v1/items", {
            params: {
              page: 1,
              per_page: 20,
              sort_by: "updated_at",
              order: "desc",
              below_threshold: true,
            },
          }),
        ]);

        const itemsData: ItemsResponse = itemsRes.data;
        const lowStockData: ItemsResponse = lowStockRes.data;
        const categoriesData: Category[] = categoriesRes.data;

        setUser(userRes.data);
        setTotalItems(itemsData.total || 0);
        setTotalCategories(Array.isArray(categoriesData) ? categoriesData.length : 0);
        setLowStockCount(lowStockData.total || 0);
      } catch (err: unknown) {
        console.error(err);

        let message = "Failed to load dashboard.";

        if (typeof err === "object" && err !== null && "response" in err) {
          const response = (
            err as { response?: { data?: { detail?: string } } }
          ).response;

          if (response?.data?.detail) {
            message = response.data.detail;
          }
        }

        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("token_type");
    router.replace("/login");
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p>Loading dashboard...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-black text-white px-4 py-2 rounded-lg"
          >
            Logout
          </button>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-red-600">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <button
          onClick={handleLogout}
          className="bg-black text-white px-4 py-2 rounded-lg"
        >
          Logout
        </button>
      </div>

      {user && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-2">User Info</h2>
          <p><b>Email:</b> {user.email}</p>
          <p><b>Name:</b> {user.full_name}</p>
          <p><b>Role:</b> {user.role}</p>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Total Items</h2>
          <p className="text-3xl font-bold">{totalItems}</p>
        </div>

        <div
          onClick={() => router.push("/inventory?lowStock=true")}
          className="bg-white rounded-xl shadow p-6 cursor-pointer hover:shadow-md transition"
        >
          <h2 className="text-lg font-semibold mb-2">Low Stock Alerts</h2>
          <p className="text-3xl font-bold">{lowStockCount}</p>
          <p className="text-sm text-gray-500 mt-2">Click to view low stock items</p>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Categories</h2>
          <p className="text-3xl font-bold">{totalCategories}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>

        <div className="flex gap-3">
          <button
            onClick={() => router.push("/inventory")}
            className="border px-4 py-2 rounded-lg bg-white"
          >
            Go to Inventory
          </button>
        </div>
      </div>
    </main>
  );
}