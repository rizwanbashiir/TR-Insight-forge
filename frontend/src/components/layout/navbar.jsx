import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();

  const navLinks = [
    { label: "Dashboard", href: "/dashboard" },
    { label: "Analytics", href: "/insights" },
    { label: "Reports", href: "/forecast" },
  ];

  return (
    <header className="bg-surface shadow-sm fixed top-0 left-0 right-0 z-50 flex justify-between items-center w-full px-margin-desktop h-16 border-b border-outline-variant">
      {/* Left: Logo + Nav links */}
      <div className="flex items-center gap-xl">
        <Link to="/" className="font-headline-md text-headline-md font-bold text-primary">
          InsightForge
        </Link>
        <nav className="hidden md:flex gap-md">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={
                location.pathname === link.href
                  ? "text-primary font-bold border-b-2 border-primary py-xs"
                  : "text-on-surface-variant hover:bg-surface-container-low transition-colors py-xs px-xs rounded"
              }
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* Right: Search + icons + avatar */}
      <div className="flex items-center gap-md">
        <div className="hidden md:flex items-center bg-surface-container-low px-sm py-xs rounded-lg border border-outline-variant">
          <span className="material-symbols-outlined text-on-surface-variant text-[20px]">search</span>
          <input
            type="text"
            placeholder="Search insights..."
            className="bg-transparent border-none focus:ring-0 font-body-sm text-on-surface placeholder:text-on-surface-variant w-48 outline-none px-2"
          />
        </div>
        <button className="material-symbols-outlined text-on-surface-variant p-xs hover:bg-surface-container-low rounded-full transition-colors relative">
          notifications
          <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-error rounded-full"></span>
        </button>
        <button className="material-symbols-outlined text-on-surface-variant p-xs hover:bg-surface-container-low rounded-full transition-colors">
          settings
        </button>
        <div className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant bg-primary-fixed flex items-center justify-center text-primary font-bold text-sm">
          A
        </div>
      </div>
    </header>
  );
}