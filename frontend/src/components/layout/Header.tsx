'use client';

import React from 'react';
import Link from 'next/link';

const navLinks = [
  { href: '/', label: 'Dashboard' },
  { href: '/transparency', label: 'Transparency' },
  { href: '/election', label: 'Elections' },
  { href: '/directory', label: 'Entity Directory' },
  { href: '/submit', label: 'Report Form 34A' },
  { href: '/about', label: 'About UJUZIO' },
];

export default function Header() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  return (
    <header className="bg-green-900 text-white shadow-lg">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold">
              <span className="text-yellow-400">U</span>JUZIO
            </span>
            <span className="hidden sm:inline text-xs text-green-200">
              Kenya&apos;s Government Transparency Platform
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm font-medium hover:text-yellow-400 transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </div>

          <button
            className="md:hidden p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            ☰
          </button>
        </div>

        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="block py-2 text-sm font-medium hover:text-yellow-400"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </nav>
    </header>
  );
}
