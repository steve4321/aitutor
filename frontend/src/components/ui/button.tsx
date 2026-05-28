import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-600 rounded-full shadow-sm',
        secondary: 'bg-emerald-600 text-white hover:bg-emerald-700 focus-visible:ring-emerald-600 rounded-full shadow-sm',
        outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white focus-visible:ring-blue-600 rounded-full',
        ghost: 'text-gray-700 hover:bg-gray-100 focus-visible:ring-blue-600 rounded-full',
        destructive: 'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600 rounded-full shadow-sm',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
