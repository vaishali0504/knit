import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'icon'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none'

  const sizeStyles = {
    sm: 'text-xs px-3 py-1.5 rounded-lg gap-1.5',
    md: 'text-sm px-4 py-2 rounded-xl gap-2',
    lg: 'text-base px-6 py-3 rounded-xl gap-2.5',
  }

  const variantStyles = {
    primary: 'bg-coral text-white hover:bg-coral-hover shadow-coral-sm hover:shadow-coral-md active:scale-[0.98]',
    secondary: 'bg-white text-foreground border border-border hover:bg-background-secondary hover:border-border active:scale-[0.98]',
    ghost: 'text-foreground-secondary hover:text-foreground hover:bg-pink-surface active:scale-[0.98]',
    icon: 'p-2 rounded-xl border border-border text-foreground-secondary hover:text-coral hover:border-coral/30 hover:bg-pink-surface active:scale-[0.98]',
  }

  const combinedStyles = `${baseStyles} ${variant === 'icon' ? variantStyles.icon : `${sizeStyles[size]} ${variantStyles[variant]}`} ${className}`

  return (
    <button className={combinedStyles} {...props}>
      {children}
    </button>
  )
}
