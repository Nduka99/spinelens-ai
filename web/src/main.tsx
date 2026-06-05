import React from "react";
import ReactDOM from "react-dom/client";
import { MotionConfig } from "framer-motion";

// Self-hosted variable fonts (zero external requests): Space Grotesk for display
// headings, Inter for UI/body. Loaded before styles so the stacks resolve.
import "@fontsource-variable/space-grotesk";
import "@fontsource-variable/inter";

import { App } from "./app/App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    {/* reducedMotion="user" makes every Framer animation honour the OS setting. */}
    <MotionConfig reducedMotion="user">
      <App />
    </MotionConfig>
  </React.StrictMode>,
);
