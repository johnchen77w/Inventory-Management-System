"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type Item = {
  id: number | string;
  name: string;
  sku?: string;
  quantity?: number;
  price?: number;
  category_id?: number | string;
  location_id?: number | string;
};

type ItemsResponse = {
  items: Item[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
};

type Category = {
  id: number;
  name: string;
};

type Location = {
  id: number;
  name: string;
};

export default function InventoryPage() {
  const router = useRouter();

  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(20);
  const [pages, setPages] = useState(0);

  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [locationId, setLocationId] = useState("");
  const [minQuantity, setMinQuantity] = useState("");
  const [maxQuantity, setMaxQuantity] = useState("");
  const [belowThreshold, setBelowThreshold] = useState(false);
  const [sortBy, setSortBy] = useState("updated_at");
  const [order, setOrder] = useState("desc");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ⭐ Add Item states
  const [showForm, setShowForm] = useState(false);

  const [form, setForm] = useState({
    sku: "",
    name: "",
    description: "",
    category_id: "",
    location_id: "",
    quantity: "",
    unit: "pcs",
    price: "",
    low_stock_threshold: "10",
  });

  const [editingId, setEditingId] = useState<number | string | null>(null);

  const [categories, setCategories] = useState<Category[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const getCategoryName = (id?: number | string) => {
    const category = categories.find((c) => c.id === Number(id));
    return category ? category.name : id ?? "-";
  };

  const getLocationName = (id?: number | string) => {
    const location = locations.find((l) => l.id === Number(id));
    return location ? location.name : id ?? "-";
  };

  const fetchItems = () => {
    setLoading(true);
    setError("");

    const params: Record<string, string | number | boolean> = {
      page,
      per_page: perPage,
      sort_by: sortBy,
      order,
      below_threshold: belowThreshold,
    };

    if (search.trim()) params.search = search.trim();
    if (categoryId.trim()) params.category_id = Number(categoryId);
    if (locationId.trim()) params.location_id = Number(locationId);
    if (minQuantity.trim()) params.min_quantity = Number(minQuantity);
    if (maxQuantity.trim()) params.max_quantity = Number(maxQuantity);

    api
      .get("/api/v1/items", { params })
      .then((res) => {
        const data: ItemsResponse = res.data;
        setItems(data.items || []);
        setTotal(data.total || 0);
        setPages(data.pages || 0);
      })
      .catch((err: unknown) => {
        console.error(err);

        let message = "Failed to load inventory.";

        if (typeof err === "object" && err !== null && "response" in err) {
          const response = (
            err as { response?: { data?: { detail?: string } } }
          ).response;

          if (response?.data?.detail) {
            message = response.data.detail;
          }
        }

        setError(message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const fetchCategories = async () => {
    try {
      const res = await api.get("/api/v1/categories");
      setCategories(res.data || []);
    } catch (err) {
      console.error("Failed to load categories:", err);
    }
  };

  const fetchLocations = async () => {
    try {
      const res = await api.get("/api/v1/locations");
      setLocations(res.data || []);
    } catch (err) {
      console.error("Failed to load locations:", err);
    }
  };

  // const handleCreate = async () => {
  //   try {
  //     await api.post("/api/v1/items", {
  //       ...form,
  //       category_id: Number(form.category_id),
  //       location_id: Number(form.location_id),
  //       quantity: Number(form.quantity),
  //       price: Number(form.price),
  //       low_stock_threshold: Number(form.low_stock_threshold),
  //     });

  //     setShowForm(false);
  //     fetchItems(); // ⭐刷新列表
  //   } catch (err) {
  //     console.error(err);
  //     alert("Create failed");
  //   }
  // };

  const handleCreateOrUpdate = async () => {
    try {
      if (editingId !== null) {
        await api.put(`/api/v1/items/${editingId}`, {
          sku: form.sku,
          name: form.name,
          description: form.description,
          category_id: Number(form.category_id),
          location_id: Number(form.location_id),
          unit: form.unit,
          price: Number(form.price),
          low_stock_threshold: Number(form.low_stock_threshold),
        });
      } else {
        await api.post("/api/v1/items", {
          sku: form.sku,
          name: form.name,
          description: form.description,
          category_id: Number(form.category_id),
          location_id: Number(form.location_id),
          quantity: Number(form.quantity),
          unit: form.unit,
          price: Number(form.price),
          low_stock_threshold: Number(form.low_stock_threshold),
        });
      }

      setShowForm(false);
      setEditingId(null);
      setForm({
        sku: "",
        name: "",
        description: "",
        category_id: "",
        location_id: "",
        quantity: "",
        unit: "pcs",
        price: "",
        low_stock_threshold: "10",
      });

      fetchItems();
    } catch (err: unknown) {
      console.error(err);

      let message = editingId !== null ? "Update failed" : "Create failed";

      if (typeof err === "object" && err !== null && "response" in err) {
        const response = (
          err as { response?: { data?: { detail?: string } } }
        ).response;

        if (response?.data?.detail) {
          message = response.data.detail;
        }
      }

      alert(message);
    }
  };

  const handleDelete = async (id: number | string) => {
    const confirmed = window.confirm("Are you sure you want to delete this item?");
    if (!confirmed) return;

    try {
      await api.delete(`/api/v1/items/${id}`);
      fetchItems();
    } catch (err: unknown) {
      console.error(err);

      let message = "Delete failed";

      if (typeof err === "object" && err !== null && "response" in err) {
        const response = (
          err as { response?: { data?: { detail?: string } } }
        ).response;

        if (response?.data?.detail) {
          message = response.data.detail;
        }
      }

      alert(message);
    }
  };

  const handleEditClick = (item: Item) => {
    setEditingId(item.id);
    setShowForm(true);

    setForm({
      sku: item.sku ?? "",
      name: item.name ?? "",
      description: "",
      category_id: item.category_id ? String(item.category_id) : "",
      location_id: item.location_id ? String(item.location_id) : "",
      quantity: item.quantity !== undefined ? String(item.quantity) : "",
      unit: "pcs",
      price: item.price !== undefined ? String(item.price) : "",
      low_stock_threshold: "10",
    });
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const lowStock = params.get("lowStock");

    if (lowStock === "true") {
      setBelowThreshold(true);
      setPage(1);
    } else {
      setBelowThreshold(false);
    }
  }, []);
  
  
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.replace("/login");
      return;
    }

    fetchItems();
    fetchCategories();
    fetchLocations();
  }, [router, page, belowThreshold]);

  const handleSearch = () => {
    setPage(1);
    fetchItems();
  };

  const handleReset = () => {
    setSearch("");
    setCategoryId("");
    setLocationId("");
    setMinQuantity("");
    setMaxQuantity("");
    setBelowThreshold(false);
    setSortBy("updated_at");
    setOrder("desc");
    setPage(1);

    setTimeout(() => {
      api
        .get("/api/v1/items", {
          params: {
            page: 1,
            per_page: 20,
            sort_by: "updated_at",
            order: "desc",
            below_threshold: false,
          },
        })
        .then((res) => {
          const data: ItemsResponse = res.data;
          setItems(data.items || []);
          setTotal(data.total || 0);
          setPages(data.pages || 0);
        })
        .catch((err: unknown) => {
          console.error(err);
          setError("Failed to reset inventory.");
        })
        .finally(() => {
          setLoading(false);
        });
    }, 0);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("token_type");
    router.replace("/login");
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Inventory</h1>

        <div className="flex gap-3">
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-black text-white px-4 py-2 rounded-lg"
          >
            Add Item
          </button>
          
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


      {showForm && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">
            {editingId !== null ? "Edit Item" : "Create Item"}
          </h2>

          <div className="grid gap-4 md:grid-cols-2">
            <input
              type="text"
              placeholder="SKU"
              value={form.sku}
              onChange={(e) => setForm({ ...form, sku: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />

            <input
              type="text"
              placeholder="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />

            <input
              type="text"
              placeholder="Description"
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              className="border rounded-lg px-3 py-2 md:col-span-2"
            />

            <select
              value={form.category_id}
              onChange={(e) =>
                setForm({ ...form, category_id: e.target.value })
              }
              className="border rounded-lg px-3 py-2"
            >
              <option value="">Select Category</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>

            <select
              value={form.location_id}
              onChange={(e) =>
                setForm({ ...form, location_id: e.target.value })
              }
              className="border rounded-lg px-3 py-2"
            >
              <option value="">Select Location</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>

            <input
              type="number"
              placeholder="Quantity"
              value={form.quantity}
              onChange={(e) =>
                setForm({ ...form, quantity: e.target.value })
              }
              disabled={editingId !== null}
              className="border rounded-lg px-3 py-2 disabled:bg-gray-100 disabled:text-gray-500"
            />

            <input
              type="text"
              placeholder="Unit"
              value={form.unit}
              onChange={(e) => setForm({ ...form, unit: e.target.value })}
              className="border rounded-lg px-3 py-2"
            />

            <input
              type="number"
              placeholder="Price"
              value={form.price}
              onChange={(e) =>
                setForm({ ...form, price: e.target.value })
              }
              className="border rounded-lg px-3 py-2"
            />

            <input
              type="number"
              placeholder="Low Stock Threshold"
              value={form.low_stock_threshold}
              onChange={(e) =>
                setForm({
                  ...form,
                  low_stock_threshold: e.target.value,
                })
              }
              className="border rounded-lg px-3 py-2"
            />
          </div>

          <div className="flex gap-3 mt-4">
            <button
              onClick={handleCreateOrUpdate}
              className="bg-black text-white px-4 py-2 rounded-lg"
            >
              {editingId !== null ? "Save Changes" : "Create"}
            </button>

            <button
              onClick={() => {
                setShowForm(false);
                setEditingId(null);
                setForm({
                  sku: "",
                  name: "",
                  description: "",
                  category_id: "",
                  location_id: "",
                  quantity: "",
                  unit: "pcs",
                  price: "",
                  low_stock_threshold: "10",
                });
              }}
              className="border px-4 py-2 rounded-lg bg-white"
            >
              Cancel
            </button>
          </div>
        </div>
      )}


      {belowThreshold && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-xl p-4 mb-6">
          Showing low stock items only.
        </div>
      )}


      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Search & Filters</h2>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <input
            type="text"
            placeholder="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border rounded-lg px-3 py-2"
          />

          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          <select
            value={locationId}
            onChange={(e) => setLocationId(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Locations</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>

          <input
            type="number"
            placeholder="Min Quantity"
            value={minQuantity}
            onChange={(e) => setMinQuantity(e.target.value)}
            className="border rounded-lg px-3 py-2"
          />

          <input
            type="number"
            placeholder="Max Quantity"
            value={maxQuantity}
            onChange={(e) => setMaxQuantity(e.target.value)}
            className="border rounded-lg px-3 py-2"
          />

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="updated_at">updated_at</option>
            <option value="created_at">created_at</option>
            <option value="name">name</option>
            <option value="sku">sku</option>
            <option value="quantity">quantity</option>
            <option value="price">price</option>
          </select>

          <select
            value={order}
            onChange={(e) => setOrder(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="desc">desc</option>
            <option value="asc">asc</option>
          </select>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={belowThreshold}
              onChange={(e) => setBelowThreshold(e.target.checked)}
            />
            Below Threshold
          </label>
        </div>

        <div className="flex gap-3 mt-4">
          <button
            onClick={handleSearch}
            className="bg-black text-white px-4 py-2 rounded-lg"
          >
            Apply Filters
          </button>

          <button
            onClick={handleReset}
            className="border px-4 py-2 rounded-lg bg-white"
          >
            Reset
          </button>
        </div>
      </div>

      {loading && (
        <div className="bg-white rounded-xl shadow p-6">
          <p>Loading inventory...</p>
        </div>
      )}

      {!loading && error && (
        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Inventory Items</h2>
            <p className="text-sm text-gray-600 mt-1">
              Total items: {total}
            </p>
            <p className="text-sm text-gray-600">
              Page: {page} / {pages || 1}
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-4">ID</th>
                  <th className="p-4">Name</th>
                  <th className="p-4">SKU</th>
                  <th className="p-4">Quantity</th>
                  <th className="p-4">Price</th>
                  <th className="p-4">Category ID</th>
                  <th className="p-4">Location ID</th>
                  <th className="p-4">Actions</th>
                </tr>
              </thead>

              <tbody>
                {items.length > 0 ? (
                  items.map((item) => (
                    <tr key={item.id} className="border-t">
                      <td className="p-4">{item.id}</td>
                      <td className="p-4">{item.name}</td>
                      <td className="p-4">{item.sku ?? "-"}</td>
                      <td className="p-4">{item.quantity ?? "-"}</td>
                      <td className="p-4">
                        {item.price !== undefined ? item.price : "-"}
                      </td>

                      <td className="p-4">{getCategoryName(item.category_id)}</td>
                      <td className="p-4">{getLocationName(item.location_id)}</td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditClick(item)}
                            className="border px-3 py-1 rounded bg-white"
                          >
                            Edit
                          </button>

                          <button
                            onClick={() => handleDelete(item.id)}
                            className="bg-red-600 text-white px-3 py-1 rounded"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="p-4" colSpan={8}>
                      No inventory items found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="flex justify-between p-4 border-t">
            <button
              onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
              disabled={page <= 1}
              className="border px-4 py-2 rounded-lg bg-white disabled:opacity-50"
            >
              Previous
            </button>

            <button
              onClick={() => setPage((prev) => prev + 1)}
              disabled={pages !== 0 && page >= pages}
              className="border px-4 py-2 rounded-lg bg-white disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </main>
  );
}