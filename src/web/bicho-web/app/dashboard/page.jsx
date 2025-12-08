'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link' // 💡 Usa Link em vez de <a> para ser mais rápido

export default function DashboardPage() {
  const [username, setUsername] = useState('')

  useEffect(() => {
    const storedUser = localStorage.getItem('bichoUser') || 'Apostador'
    setUsername(storedUser)
  }, [])

  return (
    // 1. Mudei h- para min-h- para permitir scroll em telemóveis muito pequenos
    // 2. Adicionei p-4 para não colar às bordas no telemóvel
    <div className='flex flex-col items-center justify-center text-center min-h-[calc(100vh-6rem)] p-4'>
        
        <div className="flex flex-col items-center justify-center gap-8 w-full max-w-2xl">
          <div className="space-y-4">
            <h2 className="text-4xl md:text-6xl font-bold text-white tracking-tight">
              Bem-vindo, <br className="md:hidden" /> {/* Quebra linha no mobile */}
              <span className="text-zinc-500">@{username}</span>
            </h2>
            <p className="text-zinc-400 text-lg md:text-xl">
              Eleva o nível das tuas apostas.
            </p>
          </div>

          {/* 👇 AQUI ESTÁ A MAGIA RESPONSIVA */}
          <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
            
            <Link 
              href="/dashboard/games" 
              className="w-full md:w-auto px-8 py-4 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-all active:scale-95 flex items-center justify-center"
            >
              Ver Próximos Jogos
            </Link>

            <Link 
              href="/dashboard/kelly" 
              className="w-full md:w-auto px-8 py-4 border border-zinc-800 text-zinc-400 font-bold rounded-xl hover:text-white hover:border-zinc-500 transition-all active:scale-95 flex items-center justify-center"
            >
              Calcular Value-Betting    
            </Link>
            
          </div>

        </div>
    </div>
  )
}