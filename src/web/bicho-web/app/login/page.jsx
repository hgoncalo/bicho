'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useToast } from '@/components/Toast'

export default function LoginPage() {
  const [form, setForm] = useState({ username: '', password: '' })
  const router = useRouter()
  const { addToast } = useToast()

  useEffect(() => {
    const msg = localStorage.getItem('registerSuccess')
    if (msg) {
      addToast({ type: 'success', message: msg })
      localStorage.removeItem('registerSuccess')
    }
  }, [addToast])

  const handleLogin = async (e) => {
    e.preventDefault()
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
    try {
      const res = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      const data = await res.json()
      if (res.ok) {
        localStorage.setItem('bichoToken', data.access_token)
        localStorage.setItem('bichoUser', data.username)
        router.push('/dashboard')
      } else {
        addToast({ type: 'error', message: data.error || 'Erro ao entrar' })
      }
    } catch {
      addToast({ type: 'error', message: 'Não foi possível ligar ao servidor' })
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0B0B] to-[#111] px-4">
      <div className="w-full max-w-md bg-[#0F0F0F]/70 backdrop-blur-lg border border-white/5 p-10 rounded-2xl flex flex-col items-center shadow-2xl">

        <div className="w-48 h-48 flex items-center justify-center overflow-hidden">
          <img src="/logo.png" alt="logo" className="w-full h-full object-contain block" />
        </div>

        <h1 className="text-3xl font-bold text-white tracking-tight mt-2 mb-6">
          LOGIN
        </h1>

        <form onSubmit={handleLogin} className="w-full flex flex-col gap-5">
          <div className="flex flex-col gap-1">
            <label className="text-gray-400 text-sm">Username</label>
            <input
              className="bg-black/40 text-white border border-white/10 rounded px-4 py-3 outline-none transition duration-300 focus:border-blue-500"
              onChange={e => setForm({ ...form, username: e.target.value })}
              placeholder="O teu @username"
              required
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-gray-400 text-sm">Password</label>
            <input
              type="password"
              className="bg-black/40 text-white border border-white/10 rounded px-4 py-3 outline-none transition duration-300 focus:border-blue-500"
              onChange={e => setForm({ ...form, password: e.target.value })}
              placeholder="A tua password"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-white hover:bg-gray-200 text-black font-bold py-3 rounded-lg transition-transform hover:scale-[1.02] mt-2 active:scale-95"
          >
            Entrar
          </button>

          <div className="flex flex-col sm:flex-row items-center justify-center text-sm mt-2">
            <p className="text-gray-400 mr-1">Ainda não tens conta? </p>
            <Link href="/register" className="text-white hover:text-white hover:underline font-semibold transition">
              Regista-te aqui
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
