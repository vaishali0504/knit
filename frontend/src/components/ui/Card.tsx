import React from 'react'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'pink' | 'interactive'
  children: React.ReactNode
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  className = '',
  children,
  ...props
}) => {
  const baseStyles = 'rounded-2xl transition-all duration-200'

  const variantStyles = {
    default: 'bg-white border border-border shadow-soft',
    pink: 'bg-pink-surface border border-border/80 shadow-soft',
    interactive: 'bg-white border border-border shadow-soft hover:border-coral/40 hover:shadow-md hover:-translate-y-0.5 cursor-pointer',
  }

  return (
    <div className={`${baseStyles} ${variantStyles[variant]} ${className}`} {...props}>
      {children}
    </div>
  )
}
