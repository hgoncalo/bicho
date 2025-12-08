'use client'
import { useEffect, useState } from 'react'
import { Loader2, AlertCircle, BarChart2 } from 'lucide-react'
import Link from 'next/link' 
import { useToast } from '@/components/Toast'

const TEAM_LOGOS = {
  'Guimaraes': '/teams/Guimaraes.png',
  'AVS': '/teams/AVS.png',
  'Casa Pia': '/teams/CasaPia.png',
  'Alverca': '/teams/Alverca.png',
  'Famalicao': '/teams/Famalicao.png',
  'Tondela': '/teams/Tondela.png',
  'Sp Lisbon': '/teams/SpLisbon.png',
  'Estrela': '/teams/Estrela.png',
  'Porto': '/teams/Porto.png',
  'Estoril': '/teams/Estoril.png',
  'Arouca': '/teams/Arouca.png',
  'Sp Braga': '/teams/SpBraga.png',
  'Benfica': '/teams/Benfica.png',
  'Gil Vicente': '/teams/GilVicente.png',
  'Rio Ave': '/teams/RioAve.png',
  'Santa Clara': '/teams/SantaClara.png',
  'Moreirense': '/teams/Moreirense.png',
  'Nacional': '/teams/Nacional.png'
}

export default function GamesPage() {
  const [games, setGames] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { addToast } = useToast()

  const fetchGames = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:5000/predictions')
      if (!res.ok) throw new Error('Falha ao carregar jogos')
      const data = await res.json()
      setGames(data)
    } catch (err) {
      console.error(err)
      setError('Não foi possível carregar a lista de jogos.')
      addToast({ type: 'error', message: 'Erro de ligação à API' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGames()
  }, [])

  const getTeamLogo = (name) => {
    if (TEAM_LOGOS[name]) return TEAM_LOGOS[name]
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=27272a&color=fff&size=128&bold=true&length=2`
  }

  const generateGameLink = (home, away) => {
    const slug = `${encodeURIComponent(home)}-${encodeURIComponent(away)}`
    return `/dashboard/games/${slug}`
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold text-white tracking-tight">Jogos Disponíveis</h2>
        <p className="text-zinc-500">Previsões e análises para a próxima jornada.</p>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-20 border border-dashed border-zinc-800 rounded-xl bg-zinc-900/20">
          <Loader2 className="animate-spin text-primary mb-4" size={32} />
          <p className="text-zinc-500 text-sm font-medium">A analisar dados...</p>
        </div>
      )}

      {!loading && error && (
        <div className="p-6 border border-red-900/50 bg-red-900/10 rounded-xl flex items-center gap-4 text-red-400">
          <AlertCircle size={24} />
          <p>{error}</p>
        </div>
      )}

      {!loading && games.length > 0 && (
        <div className="flex flex-col gap-4">
          {games.map((game, index) => {
            const home = game.matchInfo?.homeTeam || 'Casa'
            const away = game.matchInfo?.awayTeam || 'Fora'
            const gameLink = generateGameLink(home, away)

            return (
              <div key={index} className="group w-full flex flex-col md:flex-row items-stretch gap-0 md:hover:gap-4 my-2 transition-all duration-300 ease-out">
                <div className="flex-1 bg-[#111] border border-zinc-900 rounded-xl p-5 md:p-6 flex flex-col items-center justify-center relative z-10 hover:border-zinc-700 transition-colors shadow-sm">
                  <div className="flex flex-col md:flex-row items-center justify-center w-full">
                    <span className="hidden md:block flex-1 text-right font-bold text-white text-lg pr-4 truncate">
                      {home}
                    </span>
                    
                    <div className="flex items-center justify-center gap-4 md:gap-2 shrink-0">
                      <img src={getTeamLogo(home)} alt={home} className="w-16 h-16 md:w-14 md:h-14 object-contain drop-shadow-lg" />
                      <span className="text-zinc-600 font-mono text-xs uppercase font-bold mx-1">VS</span>
                      <img src={getTeamLogo(away)} alt={away} className="w-16 h-16 md:w-14 md:h-14 object-contain drop-shadow-lg" />
                    </div>

                    <span className="hidden md:block flex-1 text-left font-bold text-white text-lg pl-4 truncate">
                      {away}
                    </span>

                    <div className="md:hidden grid grid-cols-2 gap-4 w-full mt-4">
                       <div className="flex items-start justify-center">
                         <span className="text-white font-bold text-base text-center leading-tight">{home}</span>
                       </div>
                       <div className="flex items-start justify-center">
                         <span className="text-white font-bold text-base text-center leading-tight">{away}</span>
                       </div>
                    </div>
                  </div>

                <div className="mt-6 w-full md:hidden">
                    <Link 
                      href={gameLink}
                      className="w-full py-3 bg-white text-black font-medium rounded-lg flex items-center justify-center gap-2 hover:bg-zinc-200 transition-colors"
                    >
                      <BarChart2 size={18} />
                      Ver Análise
                    </Link>
                  </div>
                </div>

                <div className="hidden md:flex w-0 opacity-0 group-hover:w-44 group-hover:opacity-100 transition-all duration-300 ease-out flex-col">
                    <Link 
                      href={gameLink}
                      className="cursor-pointer h-full w-full bg-white text-black font-bold rounded-xl flex flex-col items-center justify-center gap-2 hover:bg-zinc-200 transition-colors shadow-lg hover:shadow-white/10 whitespace-nowrap"
                    >
                        <BarChart2 size={24} className="text-zinc-900" />
                        <span>Ver Análise</span>
                    </Link>
                </div>
            </div>
            )
          })}
        </div>
      )}
    </div>
  )
}