import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Fixed port: http://localhost:5173 must be listed in FE_ORIGINS on the BFF.
  // IPv4 host: by default Vite may bind only ::1, which Chrome can fail to reach on Windows
  server: { host: "127.0.0.1", port: 5173, strictPort: true },
  // Two pages: the full web app and the compact desktop window
  build: { rollupOptions: { input: ["index.html", "desktop.html"] } },
  test: { environment: "node" },
});
