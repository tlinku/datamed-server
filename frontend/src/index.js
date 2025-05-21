import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PrescriptionsPage from "./prescriptions/PrescriptionsPage";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import Notes from "./notes/notes";
import Profile from "./profile/profile";
import KeycloakTestPage from "./tests/KeycloakTestPage";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/prescriptions" element={<PrescriptionsPage />} />
      <Route path="/notes" element={<Notes />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/keycloak-test" element={<KeycloakTestPage />} />
    </Routes>
  </BrowserRouter>
);
