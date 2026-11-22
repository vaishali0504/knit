import React, { useState, useEffect } from 'react'
import { Mail, Menu, X, ArrowRight } from 'lucide-react'
import { Button } from '../ui/Button'

interface NavbarProps {
  onSignInClick?: () => void
  onGetStartedClick?: () => void
}

export const Navbar: React.FC<NavbarProps> = ({
  onSignInClick,
  onGetStartedClick,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'About', href: '#about' },
  ]

  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    setMobileMenuOpen(false)
    const target = document.querySelector(href)
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleLogoClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-200 ${
        isScrolled
          ? 'bg-white/90 backdrop-blur-md shadow-xs border-b border-border'
          : 'bg-white border-b border-border'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
        {/* KNIT Brand Logo */}
        <a
          href="#"
          onClick={handleLogoClick}
          className="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-coral/40 rounded-xl"
        >
          <div className="w-10 h-10 rounded-xl bg-coral flex items-center justify-center text-white shadow-coral-sm group-hover:bg-coral-hover transition-colors">
            <Mail className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-xl tracking-tight text-foreground">
              KNIT
            </span>
          </div>
        </a>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={(e) => handleLinkClick(e, link.href)}
              className="text-sm font-medium text-foreground-secondary hover:text-foreground hover:text-coral transition-colors"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Desktop Action Buttons */}
        <div className="hidden md:flex items-center gap-4">
          <Button
            variant="ghost"
            size="md"
            onClick={onSignInClick || (() => {
              const el = document.querySelector('#auth-notice')
              el?.scrollIntoView({ behavior: 'smooth' })
            })}
          >
            Sign in
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={onGetStartedClick || (() => {
              const el = document.querySelector('#features')
              el?.scrollIntoView({ behavior: 'smooth' })
            })}
          >
            Get Started
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </div>

        {/* Mobile Hamburger Button */}
        <div className="flex md:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-foreground-secondary hover:text-foreground hover:bg-background-secondary border border-border focus:outline-none"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown Sheet */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-border bg-white px-6 py-6 space-y-4 shadow-lg animate-in fade-in slide-in-from-top-2 duration-200">
          <nav className="flex flex-col space-y-3 pb-4 border-b border-border">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                className="text-base font-medium text-foreground hover:text-coral transition-colors py-1"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="flex flex-col gap-3 pt-2">
            <Button
              variant="secondary"
              size="md"
              className="w-full justify-center"
              onClick={() => {
                setMobileMenuOpen(false)
                onSignInClick?.()
              }}
            >
              Sign in
            </Button>
            <Button
              variant="primary"
              size="md"
              className="w-full justify-center"
              onClick={() => {
                setMobileMenuOpen(false)
                onGetStartedClick?.()
              }}
            >
              Get Started Free
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </header>
  )
}
