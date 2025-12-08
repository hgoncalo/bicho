'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useToast } from '@/components/Toast'
import { Gamepad2, Home, Calculator, LogOut, Loader2, Menu, X } from 'lucide-react'

export default function DashboardLayout({ children }) {
  const pathname = usePathname()
  const router = useRouter()
  const { addToast } = useToast()
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('bichoToken')
    if (!token) {
      addToast({ type: 'error', message: 'Acesso restrito. Por favor faz login.' })
      router.push('/login')
    } else {
      setIsAuthorized(true)
    }
  }, [router, addToast])

  const handleLogout = () => {
    localStorage.removeItem('bichoToken')
    localStorage.removeItem('bichoUser')
    addToast({ type: 'success', message: 'Sessão terminada.' })
    router.push('/')
  }

  const menuItems = [
    { name: 'Início', href: '/dashboard', icon: Home },
    { name: 'Jogos', href: '/dashboard/games', icon: Gamepad2 },
    { name: 'Value-Betting', href: '/dashboard/kelly', icon: Calculator },
  ]

  if (!isAuthorized) {
    return (
      <div className="h-screen w-full bg-black flex items-center justify-center">
        <Loader2 className="animate-spin text-zinc-500" size={40} />
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-black text-white selection:bg-zinc-800 overflow-hidden">
      <aside className="w-64 border-r border-zinc-900 flex-col hidden md:flex">
        <div className="p-8">
          <h1 className="text-xl font-bold tracking-widest text-white uppercase">Bicho</h1>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {menuItems.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 group ${
                  isActive 
                    ? 'bg-zinc-900 text-white font-medium' 
                    : 'text-zinc-500 hover:text-white hover:bg-zinc-950'
                }`}
              >
                <Icon size={18} strokeWidth={2} className={isActive ? 'text-white' : 'text-zinc-600 group-hover:text-white transition-colors'} />
                {item.name}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-zinc-900">
          <button 
            onClick={handleLogout} 
            className="flex items-center gap-3 px-4 py-3 w-full text-zinc-500 hover:text-white hover:bg-zinc-950 rounded-lg text-sm transition-colors group"
          >
            <LogOut size={18} className="text-zinc-600 group-hover:text-white transition-colors" />
            Sair
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col h-full relative">
        <header className="md:hidden h-16 border-b border-zinc-900 flex items-center justify-between px-6 bg-black z-20 shrink-0">
          <span className="text-lg font-bold tracking-widest text-white uppercase">Bicho</span>
          <button 
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 text-zinc-400 hover:text-white"
          >
            <Menu size={24} />
          </button>
        </header>

        {mobileMenuOpen && (
          <div className="absolute inset-0 z-50 bg-black flex flex-col p-6 animate-in fade-in slide-in-from-top-5 duration-200 md:hidden">
            <div className="flex items-center justify-between mb-8">
              <span className="text-xl font-bold tracking-widest text-white uppercase">Menu</span>
              <button 
                onClick={() => setMobileMenuOpen(false)}
                className="p-2 text-zinc-400 hover:text-white bg-zinc-900 rounded-full"
              >
                <X size={24} />
              </button>
            </div>

            <nav className="flex flex-col gap-2">
              {menuItems.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-4 px-4 py-4 rounded-xl text-lg transition-all ${
                      isActive 
                        ? 'bg-zinc-900 text-white font-medium' 
                        : 'text-zinc-500 hover:text-white hover:bg-zinc-950'
                    }`}
                  >
                    <Icon size={24} strokeWidth={2} />
                    {item.name}
                  </Link>
                )
              })}
              
              <div className="h-px bg-zinc-900 my-2 mx-4"></div>

              <button 
                onClick={handleLogout}
                className="flex items-center gap-4 px-4 py-4 text-zinc-500 hover:text-white hover:bg-zinc-950 rounded-xl text-lg transition-colors group"
              >
                <LogOut size={24} className="group-hover:text-white transition-colors" />
                Sair
              </button>
            </nav>
          </div>
        )}

        <main className="flex-1 overflow-y-auto bg-black">
          <div className="max-w-4xl mx-auto p-6 md:p-12">
            {children}
          </div>
        </main>

      </div>
    </div>
  )
}