'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { ArrowLeft, TrendingUp, Target, Loader2, ShieldCheck, BarChart3, Activity } from 'lucide-react'
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

const getTeamLogo = (name) => {
  if (TEAM_LOGOS[name]) return TEAM_LOGOS[name]
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name || 'T')}&background=27272a&color=fff&size=128&bold=true&length=2`
}

const parsePct = (val) => {
  if (!val) return 0
  return parseFloat(val.replace('%', ''))
}

const calculateTeamLines = (teamData) => {
  if (!teamData) return []
  const p0 = parsePct(teamData.prob_0_goals)
  const p1 = parsePct(teamData.prob_1_goal)
  const p2 = parsePct(teamData.prob_2_goals)
  const p3plus = parsePct(teamData.prob_3_plus_goals)
  
  return [
    { line: '0.5', over: (100 - p0).toFixed(1), under: p0.toFixed(1) },
    { line: '1.5', over: (100 - (p0 + p1)).toFixed(1), under: (p0 + p1).toFixed(1) },
    { line: '2.5', over: p3plus.toFixed(1), under: (p0 + p1 + p2).toFixed(1) }
  ]
}

const DualProgressBar = ({ primaryPercent, secondaryPercent, colorClass, height = "h-3" }) => (
  <div className={`${height} w-full bg-zinc-800 rounded-full overflow-hidden mt-2 relative`}>
    {secondaryPercent && (
      <div 
        className="absolute top-0 left-0 h-full bg-cyan-500/40 z-10 transition-all duration-700 ease-out border-r-2 border-cyan-500/50"
        style={{ width: `${Math.min(Math.max(parseFloat(secondaryPercent), 0), 100)}%` }} 
      />
    )}
    <div 
      className={`absolute top-0 left-0 h-full ${colorClass} z-20 transition-all duration-700 ease-out shadow-[2px_0_5px_rgba(0,0,0,0.3)]`} 
      style={{ width: `${Math.min(Math.max(parseFloat(primaryPercent), 0), 100)}%` }} 
    />
  </div>
)

const ProgressBar = ({ percent, colorClass = "bg-white", height = "h-2" }) => (
  <div className={`${height} w-full bg-zinc-800 rounded-full overflow-hidden mt-2`}>
    <div 
      className={`h-full ${colorClass} transition-all duration-700 ease-out`} 
      style={{ width: `${Math.min(Math.max(parseFloat(percent), 0), 100)}%` }} 
    />
  </div>
)

export default function GameDetailsPage() {
  const params = useParams()
  const { id } = params 
  const { addToast } = useToast()

  const [game, setGame] = useState(null)
  const [loading, setLoading] = useState(true)
  const [goalTab, setGoalTab] = useState('total') 

  const handleScrollTo = (targetId) => {
    const element = document.getElementById(targetId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  useEffect(() => {
    const fetchGame = async () => {
      setLoading(true)
      try {
        const res = await fetch('http://localhost:5000/predictions')
        if (!res.ok) throw new Error('Erro API')
        const allGames = await res.json()

        const decodedId = decodeURIComponent(id)
        const [urlHome, urlAway] = decodedId.split('-')

        const foundGame = allGames.find(g => 
          g.matchInfo.homeTeam === urlHome && 
          g.matchInfo.awayTeam === urlAway
        )

        if (!foundGame) throw new Error('Jogo não encontrado')
        
        const processedGame = 
        {
          home: foundGame.matchInfo.homeTeam,
          away: foundGame.matchInfo.awayTeam,
          stats: {
            matchWinner: 
            [
              { 
                label: foundGame.matchInfo.homeTeam, 
                percent: parsePct(foundGame.matchPredictions.team_A.win_prob).toFixed(1), 
                doubleChance: parsePct(foundGame.matchPredictions.team_A.win_or_draw_prob).toFixed(1),
                type: 'home' 
              },
              { 
                label: 'Empate', 
                percent: parsePct(foundGame.matchPredictions.match_odds.draw_prob).toFixed(1), 
                type: 'draw' 
              },
              { 
                label: foundGame.matchInfo.awayTeam, 
                percent: parsePct(foundGame.matchPredictions.team_B.win_prob).toFixed(1), 
                doubleChance: parsePct(foundGame.matchPredictions.team_B.win_or_draw_prob).toFixed(1),
                type: 'away' 
              }
            ],
            btts: 
            {
              yes: parsePct(foundGame.matchPredictions.match_odds.btts_prob).toFixed(1),
              no: (100 - parsePct(foundGame.matchPredictions.match_odds.btts_prob)).toFixed(1)
            },
            goals: 
            {
              total: Object.entries(foundGame.matchPredictions.total_goals_lines).map(([line, val]) => ({
                line: line,
                over: parsePct(val.over).toFixed(1),
                under: parsePct(val.under).toFixed(1)
              })),
              home: {
                lines: calculateTeamLines(foundGame.matchPredictions.team_A),
                xg: foundGame.matchPredictions.team_A.expected_goals || '0.0'
              },
              away: {
                lines: calculateTeamLines(foundGame.matchPredictions.team_B),
                xg: foundGame.matchPredictions.team_B.expected_goals || '0.0'
              }
            }
          }
        }
        setGame(processedGame)
      } 
      catch (err) 
      {
        console.error(err)
        addToast({ type: 'error', message: 'Erro ao carregar jogo.' })
      } 
      finally 
      {
        setLoading(false)
      }
    }

    if (id) fetchGame()

    }, [id, addToast])

    if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="animate-spin text-zinc-500" /></div>
    if (!game) return <div className="p-8 text-white">Jogo não encontrado.</div>

    let currentGoalStats = []
    let currentXG = null

    if (goalTab === 'total') {
      currentGoalStats = game.stats.goals.total
    } else {
      currentGoalStats = game.stats.goals[goalTab].lines
      currentXG = game.stats.goals[goalTab].xg
    }

    return (
    <div className="w-full max-w-7xl mx-auto px-4 pb-20 space-y-8">
      <div className="pt-6">
        <Link href="/dashboard/games" className="inline-flex items-center gap-2 text-zinc-400 hover:text-white transition-colors text-sm font-medium bg-zinc-900/50 px-3 py-2 rounded-lg">
          <ArrowLeft size={16} />
          Voltar à lista
        </Link>
      </div>

      <div className="bg-[#111] border border-zinc-800 rounded-2xl p-6 md:p-10 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-center gap-8 md:gap-20">
          <div className="flex flex-col items-center gap-4 flex-1">
            <img src={getTeamLogo(game.home)} alt={game.home} className="w-20 h-20 md:w-28 md:h-28 object-contain drop-shadow-2xl" />
            <h1 className="text-xl md:text-3xl font-bold text-white tracking-tight text-center leading-tight">{game.home}</h1>
          </div>
          <div className="flex flex-col items-center shrink-0">
            <span className="text-3xl md:text-5xl font-black text-zinc-800 tracking-widest select-none">VS</span>
          </div>
          <div className="flex flex-col items-center gap-4 flex-1">
            <img src={getTeamLogo(game.away)} alt={game.away} className="w-20 h-20 md:w-28 md:h-28 object-contain drop-shadow-2xl" />
            <h1 className="text-xl md:text-3xl font-bold text-white tracking-tight text-center leading-tight">{game.away}</h1>
          </div>
        </div>
      </div>

      <div className="flex justify-center mb-8 mt-4">
        <div className="bg-zinc-900/90 backdrop-blur-md border border-zinc-700/50 p-1.5 rounded-full shadow-2xl flex items-center gap-2">
          <button 
            type="button"
            onClick={() => handleScrollTo('resultados')}
            className="cursor-pointer flex items-center gap-2 px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-full text-sm font-bold transition-all hover:scale-105 active:scale-95 shadow-lg border border-zinc-700"
          >
            <BarChart3 size={16} className="text-emerald-400" />
            Resultados
          </button>
          <button 
            type="button"
            onClick={() => handleScrollTo('golos')}
            className="cursor-pointer flex items-center gap-2 px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-full text-sm font-bold transition-all hover:scale-105 active:scale-95 shadow-lg border border-zinc-700"
          >
            <Target size={16} className="text-blue-400" />
            Golos
          </button>
        </div>
      </div>

      <section id="resultados" className="space-y-6 scroll-mt-8">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-lg"><TrendingUp className="text-emerald-500" size={20} /></div>
          <h2 className="text-xl font-bold text-white">Vencedor do Encontro</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {game.stats.matchWinner.map((item, idx) => 
          {
            let colorBar = 'bg-zinc-500'; 
            let borderColor = 'hover:border-zinc-500/50'

            if (item.type === 'home') { colorBar = 'bg-emerald-500'; borderColor = 'hover:border-emerald-500/50' }
            if (item.type === 'away') { colorBar = 'bg-red-500'; borderColor = 'hover:border-red-500/50' }

            return (
              <div key={idx} className={`bg-[#111] border border-zinc-800 p-6 rounded-xl flex flex-col justify-between transition-colors ${borderColor} group`}>
                <div className="flex justify-between items-start mb-3">
                  <span className="text-zinc-400 font-medium text-sm uppercase tracking-wide truncate pr-2 mt-1">{item.label}</span>
                  
                  <div className="flex flex-col items-end">
                    <span className="text-3xl font-bold text-white tabular-nums leading-none">
                      {item.percent}<span className="text-lg text-zinc-600">%</span>
                    </span>
                    {item.doubleChance && (
                      <span className="text-[10px] text-cyan-400 font-bold mt-1 uppercase tracking-wider">
                        1X/X2: {item.doubleChance}%
                      </span>
                    )}
                  </div>
                </div>

                {item.type === 'draw' ? (
                   <ProgressBar percent={item.percent} colorClass={colorBar} height="h-3" />
                ) : (
                   <DualProgressBar 
                      primaryPercent={item.percent} 
                      secondaryPercent={item.doubleChance} 
                      colorClass={colorBar} 
                      height="h-3" 
                   />
                )}
              </div>
            )
          })}
        </div>
      </section>

      <div className="h-px bg-zinc-800/50 w-full" />

      <section id="golos" className="space-y-8 scroll-mt-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg"><Target className="text-blue-500" size={20} /></div>
            <h2 className="text-xl font-bold text-white">Mercado de Golos</h2>
          </div>

          <div className="bg-zinc-900 p-1.5 rounded-lg flex gap-1 self-start md:self-auto overflow-x-auto max-w-full">
            {
            [
              { id: 'total', label: 'Total Jogo' },
              { id: 'home', label: game.home },
              { id: 'away', label: game.away }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setGoalTab(tab.id)}
                className={`cursor-pointer px-4 py-2 rounded-md text-xs md:text-sm font-bold whitespace-nowrap transition-all ${
                  goalTab === tab.id ? 'bg-zinc-700 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className={`grid grid-cols-1 ${goalTab === 'total' ? 'lg:grid-cols-3' : 'lg:grid-cols-1'} gap-6`}>
          {
          goalTab === 'total' ? 
          (
            <div className="lg:col-span-1 bg-[#111] border border-zinc-800 rounded-xl p-6 flex flex-col h-full animate-in fade-in duration-500">
              <div className="flex items-center gap-2 mb-6">
                <ShieldCheck className="text-purple-500" size={18} />
                <h3 className="text-zinc-200 font-bold">Ambas Marcam (BTTS)</h3>
              </div>
              <div className="flex-1 flex flex-col justify-center gap-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-zinc-400 font-medium">Sim</span>
                    <span className="text-white font-bold">{game.stats.btts.yes}%</span>
                  </div>
                  <ProgressBar percent={game.stats.btts.yes} colorClass="bg-purple-500" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-zinc-400 font-medium">Não</span>
                    <span className="text-white font-bold">{game.stats.btts.no}%</span>
                  </div>
                  <ProgressBar percent={game.stats.btts.no} colorClass="bg-zinc-600" />
                </div>
              </div>
            </div>
          )
          :
          (
            <div className="lg:col-span-1 bg-[#111] border border-zinc-800 rounded-xl p-6 flex flex-col h-full animate-in fade-in duration-500">
              <div className="flex items-center gap-2 mb-6">
                <Activity className="text-cyan-400" size={18} />
                <h3 className="text-zinc-200 font-bold">Expected Goals (xG)</h3>
              </div>
              <div className="flex-1 flex flex-col justify-center">
                 <div className="flex justify-between items-end mb-3">
                    <span className="text-zinc-400 font-medium text-sm">Golos Esperados</span>
                    <span className="text-3xl font-bold text-white tabular-nums">{currentXG}</span>
                 </div>
                 {/* Escala assumida de 3.5 para preencher 100% da barra para visualização */}
                 <ProgressBar percent={(parseFloat(currentXG) / 3.5) * 100} colorClass="bg-cyan-400" height="h-4" />
              </div>
            </div>
          )
          }

          <div className={`bg-[#111] border border-zinc-800 rounded-xl overflow-hidden flex flex-col ${goalTab === 'total' ? 'lg:col-span-2' : ''}`}>
            <div className="overflow-x-auto">
              <div className="min-w-[500px] md:min-w-0"> 
                <div className="grid grid-cols-[80px_1fr_1fr] bg-zinc-900/50 border-b border-zinc-800 p-4 gap-6 text-xs uppercase font-bold text-zinc-500 tracking-wider">
                  <div className="text-center">Linha</div>
                  <div>Over (Mais)</div>
                  <div>Under (Menos)</div>
                </div>

                <div className="divide-y divide-zinc-800/50">
                  {currentGoalStats.length > 0 ? (
                    currentGoalStats.map((stat, idx) => 
                    (
                      <div key={idx} className="grid grid-cols-[80px_1fr_1fr] p-4 gap-6 items-center hover:bg-zinc-900/20 transition-colors">
                        <div className="flex justify-center">
                          <span className="bg-zinc-800 text-zinc-300 px-3 py-1.5 rounded font-mono font-bold text-sm border border-zinc-700">
                            {stat.line}
                          </span>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs md:text-sm mb-1.5">
                            <span className="text-zinc-500 font-medium">Mais de {stat.line}</span>
                            <span className="text-white font-bold">{stat.over}%</span>
                          </div>
                          <ProgressBar percent={stat.over} colorClass="bg-blue-500" height="h-2" />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs md:text-sm mb-1.5">
                            <span className="text-zinc-500 font-medium">Menos de {stat.line}</span>
                            <span className="text-white font-bold">{stat.under}%</span>
                          </div>
                          <ProgressBar percent={stat.under} colorClass="bg-orange-500" height="h-2" />
                        </div>
                      </div>
                    )
                    )
                  ) 
                  :
                  (
                    <div className="p-8 text-center text-zinc-500">Sem dados.</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}