import React from 'react';

const ToggleSwitch = ({ 
  enabled, 
  onChange, 
  label, 
  description,
  disabled = false,
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: {
      switch: 'h-5 w-9',
      toggle: 'h-4 w-4',
      translate: 'translate-x-4'
    },
    md: {
      switch: 'h-6 w-11',
      toggle: 'h-5 w-5',
      translate: 'translate-x-5'
    },
    lg: {
      switch: 'h-7 w-14',
      toggle: 'h-6 w-6',
      translate: 'translate-x-7'
    }
  };

  const classes = sizeClasses[size];

  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        {label && (
          <label className="text-sm font-medium text-gray-700 block">
            {label}
          </label>
        )}
        {description && (
          <p className="text-xs text-gray-500 mt-1">
            {description}
          </p>
        )}
      </div>
      
      <button
        type="button"
        onClick={() => !disabled && onChange(!enabled)}
        disabled={disabled}
        className={`
          relative inline-flex flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent
          transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
          ${classes.switch}
          ${enabled 
            ? 'bg-primary-600' 
            : 'bg-gray-200'
          }
          ${disabled 
            ? 'opacity-50 cursor-not-allowed' 
            : 'hover:shadow-sm'
          }
        `}
        role="switch"
        aria-checked={enabled}
        aria-label={label || 'Toggle switch'}
      >
        <span className="sr-only">{label || 'Toggle'}</span>
        <span
          className={`
            pointer-events-none inline-block rounded-full bg-white shadow transform ring-0 
            transition ease-in-out duration-200
            ${classes.toggle}
            ${enabled 
              ? classes.translate 
              : 'translate-x-0'
            }
          `}
        />
      </button>
    </div>
  );
};

export default ToggleSwitch;