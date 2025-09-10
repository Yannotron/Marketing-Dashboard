import React from "react";
import { Link, NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview";
import Topics from "./pages/Topics";
import Explorer from "./pages/Explorer";
import Drafts from "./pages/Drafts";
import { BarChart3, Search, FileText, Layers, Github } from "lucide-react";

function NavItem({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-3 py-2 rounded-md text-sm font-medium ${isActive ? "bg-accent" : "hover:bg-accent"}`
      }
    >
      {children}
    </NavLink>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b sticky top-0 z-10 bg-background/80 backdrop-blur">
        <div className="container flex h-14 items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <BarChart3 className="h-5 w-5" /> Reddit Dashboard
          </Link>
          <nav className="flex items-center gap-2">
            <NavItem to="/">Overview</NavItem>
            <NavItem to="/topics">Topics</NavItem>
            <NavItem to="/explorer">Explorer</NavItem>
            <NavItem to="/drafts">Drafts</NavItem>
            <a className="ml-3 opacity-70 hover:opacity-100" href="https://github.com/" target="_blank" rel="noreferrer">
              <Github className="h-4 w-4" />
            </a>
          </nav>
        </div>
      </header>
      <main className="container py-6">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/topics" element={<Topics />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/drafts" element={<Drafts />} />
        </Routes>
      </main>
    </div>
  );
}


