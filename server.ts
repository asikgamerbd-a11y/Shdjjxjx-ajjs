import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import fs from "fs";
import "./src/bot.ts";

// Global error handlers
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception thrown:', err);
});

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Simple API to check bot status
  app.get("/api/status", (req, res) => {
    console.log(`[API] Status requested from ${req.ip}`);
    try {
      const dataDir = path.join(process.cwd(), 'data');
      
      const safeRead = (file: string) => {
        const filePath = path.join(dataDir, file);
        if (!fs.existsSync(filePath)) return [];
        try {
          const content = fs.readFileSync(filePath, 'utf-8').trim();
          if (!content) return [];
          return JSON.parse(content);
        } catch (e) {
          console.error(`Error parsing ${file}:`, e);
          return [];
        }
      };

      const users = safeRead('users.json');
      const numbers = safeRead('numbers.json');
      
      res.json({
        status: "running",
        users: Array.isArray(users) ? users.length : 0,
        totalNumbers: Array.isArray(numbers) ? numbers.length : 0,
        availableNumbers: Array.isArray(numbers) ? numbers.filter((n: any) => n && !n.used).length : 0
      });
    } catch (err) {
      console.error("Status API root error:", err);
      res.status(500).json({ status: "error", message: "Internal Server Error" });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer().catch(console.error);
