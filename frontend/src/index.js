import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PrescriptionsPage from "./prescriptions/PrescriptionsPage";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import Notes from "./notes/notes";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/prescriptions" element={<PrescriptionsPage />} />
      <Route path="/notes" element={<Notes />} />
    </Routes>
  </BrowserRouter>
);
reportWebVitals();
