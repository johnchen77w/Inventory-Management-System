"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await api.post("/api/v1/auth/login", {
        email,
        password,
      });

      const data = res.data;

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("token_type", data.token_type);

      router.replace("/dashboard");
    } catch (err: unknown) {
      console.error(err);

      let message = "Login failed";

      if (typeof err === "object" && err !== null && "response" in err) {
        const response = (err as {
          response?: { data?: { detail?: string } };
        }).response;

        if (response?.data?.detail) {
          message = response.data.detail;
        }
      }

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full border p-2 rounded mb-4"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full border p-2 rounded mb-4"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}

        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full bg-black text-white p-2 rounded"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </div>
    </main>
  );
}