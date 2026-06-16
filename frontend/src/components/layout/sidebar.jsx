import { Link, useLocation } from "react-router-dom";

const navItems = [
  { label: "Dashboard", icon: "dashboard", href: "/dashboard" },
  { label: "Upload", icon: "cloud_upload", href: "/upload" },
  { label: "Analytics", icon: "monitoring", href: "/insights" },
  { label: "Forecast", icon: "trending_up", href: "/forecast" },
  { label: "Segmentation", icon: "pie_chart", href: "/segmentation" },
  { label: "Reports", icon: "description", href: "/insights" },
  { label: "Team", icon: "group", href: "#" },
];

const bottomItems = [
  { label: "Support", icon: "support_agent", href: "#" },
  { label: "Feedback", icon: "rate_review", href: "#" },
];

export default function Sidebar() {
  const location = useLocation();

  const isActive = (href) =>
    href !== "#" && location.pathname === href;

  return (
    <aside className="hidden md:flex flex-col h-full py-md px-sm bg-surface border-r border-outline-variant w-64 fixed left-0 top-16 bottom-0 overflow-y-auto">
      {/* Main nav */}
      <div className="flex flex-col gap-xs mb-lg flex-1">
        {navItems.map((item) => (
          <Link
            key={item.href + item.label}
            to={item.href}
            className={
              isActive(item.href)
                ? "bg-secondary-container text-on-secondary-container flex items-center gap-sm px-sm py-2 rounded-lg font-bold scale-95 transition-transform"
                : "text-on-surface-variant hover:bg-surface-container-high flex items-center gap-sm px-sm py-2 rounded-lg transition-all"
            }
          >
            <span
              className="material-symbols-outlined text-[20px]"
              style={
                isActive(item.href)
                  ? { fontVariationSettings: "'FILL' 1" }
                  : {}
              }
            >
              {item.icon}
            </span>
            <span className="font-label-md text-label-md">{item.label}</span>
          </Link>
        ))}
      </div>

      {/* Bottom section */}
      <div className="mt-auto flex flex-col gap-xs pt-md border-t border-outline-variant">
        <Link
          to="/upload"
          className="bg-primary text-on-primary font-bold py-2 rounded-xl shadow-lg hover:opacity-90 transition-all mb-md text-center text-sm"
        >
          New Analysis
        </Link>
        {bottomItems.map((item) => (
          <a
            key={item.label}
            href={item.href}
            className="text-on-surface-variant hover:bg-surface-container-high flex items-center gap-sm px-sm py-2 rounded-lg transition-all"
          >
            <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
            <span className="font-label-md text-label-md">{item.label}</span>
          </a>
        ))}

        {/* User profile pill */}
        <div className="flex items-center gap-sm mt-sm px-sm py-2">
          <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-sm shrink-0">
            A
          </div>
          <div className="overflow-hidden">
            <p className="font-label-md text-label-md text-on-surface truncate leading-tight">Alex Chen</p>
            <p className="text-[10px] text-on-surface-variant uppercase tracking-tight">Pro Analyst</p>
          </div>
        </div>
      </div>
    </aside>
  );
}