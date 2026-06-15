export default function Footer() {
  const footerLinks = [
    { label: "Privacy Policy", href: "#" },
    { label: "Terms of Service", href: "#" },
    { label: "Help Center", href: "#" },
  ];

  return (
    <footer className="bg-surface-container-low border-t border-outline-variant flex flex-col sm:flex-row justify-between items-center w-full py-md px-margin-desktop gap-sm">
      <div className="flex items-center gap-md">
        <span className="font-label-md text-label-md font-bold text-on-surface">InsightForge</span>
        <p className="font-body-sm text-body-sm text-on-surface-variant">
          © 2024 InsightForge Inc.
        </p>
      </div>
      <div className="flex gap-lg">
        {footerLinks.map((link) => (
          <a
            key={link.label}
            href={link.href}
            className="font-body-sm text-body-sm text-on-surface-variant hover:text-primary transition-colors"
          >
            {link.label}
          </a>
        ))}
      </div>
    </footer>
  );
}