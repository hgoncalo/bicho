'use client'
import { createContext, useContext, useState, useEffect } from 'react'
const ToastContext = createContext(null)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error("useToast tem de ser usado dentro de um <ToastProvider />")
  }
  return context
}

function ToastItem({ id, message, type, onRemove }) {
  const [isClosing, setIsClosing] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsClosing(true)
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (isClosing) {
      const animationTimer = setTimeout(() => {
        onRemove(id)
      }, 300)
      return () => clearTimeout(animationTimer)
    }
  }, [isClosing, id, onRemove])

  return (
    <div
      className={`relative w-80 bg-[#1a1a1a] border-l-4 ${
        type === 'success' ? 'border-green-500' : 'border-red-500'
      } text-white rounded shadow-lg overflow-hidden ${
        isClosing ? 'animate-slideOut' : 'animate-slideIn'
      }`}
    >
      <div className="p-4 flex items-center gap-3">
        <span className={`text-xl font-bold ${type === 'success' ? 'text-green-400' : 'text-red-400'}`}>
          {type === 'success' ? '✓' : '✕'}
        </span>
        <p className="text-sm font-medium">{message}</p>
      </div>
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-700">
         <div 
            className={`h-full ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} animate-progress`} 
         />
      </div>
    </div>
  )
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = ({ type = 'success', message }) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, type, message }])
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  return (
    <ToastContext.Provider value={{ addToast, toasts, removeToast }}>
      {children}
    </ToastContext.Provider>
  )
}

export function ToastRenderer() {
  const { toasts, removeToast } = useToast()

  if (toasts.length === 0) return null

  return (
    <>
      <div className="fixed top-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none">
        <div className="pointer-events-auto flex flex-col gap-2">
          {toasts.map(t => (
            <ToastItem 
              key={t.id} 
              {...t} 
              onRemove={removeToast} 
            />
          ))}
        </div>
      </div>

      <style jsx global>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
          from { transform: translateX(0); opacity: 1; }
          to { transform: translateX(100%); opacity: 0; }
        }
        @keyframes progress {
          from { width: 100%; }
          to { width: 0%; }
        }
        .animate-slideIn {
          animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        .animate-slideOut {
          animation: slideOut 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        .animate-progress {
          animation: progress 3s linear forwards;
        }
      `}</style>
    </>
  )
}