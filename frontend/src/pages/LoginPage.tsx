import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Mail, Lock, ArrowLeft, ArrowRight, AlertCircle, RefreshCw } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/app'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!email || !password) {
      setError('Please provide both email and password.')
      return
    }

    setIsSubmitting(true)
    try {
      await login({ email, password })
      navigate(from, { replace: true })
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed. Please check your credentials.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-background-secondary/60 flex flex-col justify-between py-12 px-6">
      {/* Top Bar with Return Link */}
      <div className="max-w-md w-full mx-auto">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs font-semibold text-foreground-secondary hover:text-coral transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to KNIT Home
        </Link>
      </div>

      {/* Main Login Card */}
      <div className="max-w-md w-full mx-auto">
        <Card className="p-8 sm:p-10 shadow-soft bg-white border border-border">
          {/* Logo & Header */}
          <div className="text-center mb-8 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-coral flex items-center justify-center text-white shadow-coral-sm mx-auto">
              <Mail className="w-6 h-6" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
              Sign in to KNIT
            </h1>
            <p className="text-xs sm:text-sm text-foreground-secondary">
              Connect. Understand. Act. &bull; Secure Email Intelligence
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 rounded-xl bg-red-50 border border-red-200 p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-red-700 font-medium leading-relaxed">
                {error}
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-foreground mb-1.5 uppercase tracking-wider">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-foreground-secondary/70">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@university.edu or work email"
                  className="w-full bg-white border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-foreground placeholder:text-foreground-secondary/50 focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral transition-all"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-bold text-foreground uppercase tracking-wider">
                  Password
                </label>
                <span className="text-xs text-foreground-secondary/70">
                  Min 6 characters
                </span>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-foreground-secondary/70">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full bg-white border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-foreground placeholder:text-foreground-secondary/50 focus:outline-none focus:ring-2 focus:ring-coral/20 focus:border-coral transition-all"
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={isSubmitting}
              className="w-full justify-center mt-2"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                  Signing In...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </Button>
          </form>

          {/* Footer Navigation */}
          <div className="mt-8 pt-6 border-t border-border text-center text-xs text-foreground-secondary">
            Don&apos;t have an account yet?{' '}
            <Link
              to="/register"
              className="font-bold text-coral hover:text-coral-hover transition-colors"
            >
              Create free account
            </Link>
          </div>
        </Card>
      </div>

      {/* Security Footer */}
      <div className="text-center text-xs text-foreground-secondary">
        KNIT &bull; Industry-Standard Salted Bcrypt & JWT Session Protection
      </div>
    </div>
  )
}
