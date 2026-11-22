import React from 'react'

export interface BadgeProps {
  variant?: 'coral' | 'pink' | 'neutral' | 'success' | 'warning'
  size?: 'sm' | 'md'
  icon?: React.ReactNode
  children: React.ReactNode
  className?: string
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'pink',
  size = 'md',
  icon,
  children,
  className = '',
}) => {
  const baseStyles = 'inline-flex items-center font-medium tracking-tight whitespace-nowrap'

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 rounded-md gap-1',
    md: 'text-xs px-2.5 py-1 rounded-full gap-1.5',
  }

  const variantStyles = {
    coral: 'bg-coral text-white font-semibold shadow-xs',
    pink: 'bg-pink-surface text-coral font-semibold border border-border/80',
    neutral: 'bg-background-secondary text-foreground-secondary border border-border',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200/80',
    warning: 'bg-amber-50 text-amber-700 border border-amber-200/80',
  }

  return (
    <span className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}>
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </span>
  )
}
