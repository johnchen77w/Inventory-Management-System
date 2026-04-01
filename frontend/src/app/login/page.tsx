"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [mode, setMode] = useState<"login" | "signup">("login");

  // Login fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Signup fields
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [role, setRole] = useState("staff");
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupError, setSignupError] = useState("");
  const [signupSuccess, setSignupSuccess] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await api.post("/api/v1/auth/login", { email, password });
      const data = res.data;

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("token_type", data.token_type);

      router.replace("/dashboard");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Login failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    setSignupLoading(true);
    setSignupError("");
    setSignupSuccess("");

    if (!firstName.trim() || !lastName.trim()) {
      setSignupError("First and last name are required.");
      setSignupLoading(false);
      return;
    }

    if (!signupEmail.trim() || !signupPassword.trim()) {
      setSignupError("Email and password are required.");
      setSignupLoading(false);
      return;
    }

    try {
      await api.post("/api/v1/auth/signup", {
        email: signupEmail.trim(),
        password: signupPassword,
        full_name: `${firstName.trim()} ${lastName.trim()}`,
        role,
      });
      setSignupSuccess("Account created! You can now log in.");
      setFirstName("");
      setLastName("");
      setSignupEmail("");
      setSignupPassword("");
      setRole("staff");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Signup failed";
      setSignupError(message);
    } finally {
      setSignupLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-md">
        {mode === "login" ? (
          <>
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

            <p className="text-center text-sm mt-4 text-gray-600">
              Don&apos;t have an account?{" "}
              <button
                onClick={() => setMode("signup")}
                className="text-blue-600 hover:underline font-medium"
              >
                Create Account
              </button>
            </p>
          </>
        ) : (
          <>
            <h1 className="text-2xl font-bold mb-6 text-center">
              Create Account
            </h1>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <input
                type="text"
                placeholder="First Name"
                className="border p-2 rounded"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
              <input
                type="text"
                placeholder="Last Name"
                className="border p-2 rounded"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>

            <input
              type="email"
              placeholder="Email"
              className="w-full border p-2 rounded mb-4"
              value={signupEmail}
              onChange={(e) => setSignupEmail(e.target.value)}
            />

            <input
              type="password"
              placeholder="Password"
              className="w-full border p-2 rounded mb-4"
              value={signupPassword}
              onChange={(e) => setSignupPassword(e.target.value)}
            />

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Role</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="role"
                    value="staff"
                    checked={role === "staff"}
                    onChange={() => setRole("staff")}
                  />
                  <span>Worker</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="role"
                    value="manager"
                    checked={role === "manager"}
                    onChange={() => setRole("manager")}
                  />
                  <span>Manager</span>
                </label>
              </div>
            </div>

            {signupError && (
              <p className="text-red-500 mb-4 text-sm">{signupError}</p>
            )}
            {signupSuccess && (
              <p className="text-green-600 mb-4 text-sm">{signupSuccess}</p>
            )}

            <button
              onClick={handleSignup}
              disabled={signupLoading}
              className="w-full bg-black text-white p-2 rounded"
            >
              {signupLoading ? "Creating..." : "Create Account"}
            </button>

            <p className="text-center text-sm mt-4 text-gray-600">
              Already have an account?{" "}
              <button
                onClick={() => setMode("login")}
                className="text-blue-600 hover:underline font-medium"
              >
                Back to Login
              </button>
            </p>
          </>
        )}
      </div>
    </main>
  );
}
