'use client'

import { useState } from 'react'
import { Calculator, Info, DollarSign, Percent, TrendingUp, AlertTriangle, Wallet, Zap, Trophy, Flame, Plus, Minus } from 'lucide-react'
import { useToast } from '@/components/Toast'

const NumberInput = ({ label, value, onChange, step, min = 0, icon: Icon, placeholder, suffix }) => {
  
  const handleIncrement = () => {
    let current = parseFloat(value.toString().replace(',', '.')) || 0
    let next = current + step
    if (step < 1) next = parseFloat(next.toFixed(2))
    onChange(String(next))
  }

  const handleDecrement = () => {
    let current = parseFloat(value.toString().replace(',', '.')) || 0
    let next = current - step
    if (next < min) next = min
    if (step < 1) next = parseFloat(next.toFixed(2))
    onChange(String(next))
  }

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-zinc-400 ml-1 flex justify-between">
        {label}
        {suffix && <span className="text-xs text-zinc-600 font-mono self-end">{suffix}</span>}
      </label>
      
      <div className="flex items-center bg-zinc-900/50 border border-zinc-700 rounded-xl overflow-hidden focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/50 transition-all">
        <button 
          onClick={handleDecrement}
          className="p-4 hover:bg-zinc-800 text-zinc-500 hover:text-white transition-colors active:scale-95 border-r border-zinc-800"
        >
          <Minus size={18} />
        </button>

        <div className="relative flex-1">
          <Icon className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600 pointer-events-none" size={16} />
          <input 
            type="text" 
            inputMode="decimal"
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full bg-transparent text-white text-center font-mono py-3 focus:outline-none"
          />
        </div>

        <button 
          onClick={handleIncrement}
          className="p-4 hover:bg-zinc-800 text-zinc-500 hover:text-white transition-colors active:scale-95 border-l border-zinc-800"
        >
          <Plus size={18} />
        </button>
      </div>
    </div>
  )
}

export default function KellyPage() {
  const [odd, setOdd] = useState('')
  const [prob, setProb] = useState('')
  const [bankroll, setBankroll] = useState('')
  const [result, setResult] = useState(null)
  const { addToast } = useToast()

  const calculateKelly = () => {
    if (!odd || !prob || !bankroll) {
      addToast({ type: 'error', message: 'Preenche todos os campos.' })
      return
    }

    const oddVal = parseFloat(odd.toString().replace(',', '.'))
    const probVal = parseFloat(prob.toString().replace(',', '.'))
    const bankVal = parseFloat(bankroll.toString().replace(',', '.'))

    if (isNaN(oddVal) || isNaN(probVal) || isNaN(bankVal)) {
      addToast({ type: 'error', message: 'Valores inválidos.' })
      return
    }

    if (oddVal <= 1) {
      addToast({ type: 'error', message: 'Odd deve ser > 1.00' })
      return
    }

    if (probVal <= 0 || probVal > 100) {
      addToast({ type: 'error', message: 'Probabilidade entre 0 e 100.' })
      return
    }

    const decimalProb = probVal / 100
    const b = oddVal - 1 
    const p = decimalProb 
    const q = 1 - p 

    const kellyFraction = (b * p - q) / b
    
    const percentage = kellyFraction * 100
    const amount = bankVal * kellyFraction

    let status = ''
    let colorClass = ''
    let bgClass = ''
    let icon = null

    if (percentage <= 0) {
      status = 'EV Negativo (Mau Valor)'
      colorClass = 'text-red-500'
      bgClass = 'bg-red-500/10 border-red-500/20'
      icon = <AlertTriangle className="text-red-500" />
      
    } else if (percentage < 5) {
      status = 'Valor Marginal'
      colorClass = 'text-yellow-500'
      bgClass = 'bg-yellow-500/10 border-yellow-500/20'
      icon = <TrendingUp className="text-yellow-500" />

    } else if (percentage < 15) {
      status = 'Valor Sólido'
      colorClass = 'text-emerald-500'
      bgClass = 'bg-emerald-500/10 border-emerald-500/20'
      icon = <Zap className="text-emerald-500" />

    } else if (percentage < 32.5) {
      status = 'Valor Elevado'
      colorClass = 'text-blue-500'
      bgClass = 'bg-blue-500/10 border-blue-500/20'
      icon = <Trophy className="text-blue-500" />

    } else {
      status = 'Valor Extremo'
      colorClass = 'text-purple-500'
      bgClass = 'bg-purple-500/10 border-purple-500/20'
      icon = <Flame className="text-purple-500" />
    }

    setResult({
      pct: percentage.toFixed(2), 
      amount: amount.toFixed(2),  
      status,
      colorClass,
      bgClass,
      icon
    })
  }

  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-6 md:py-10 space-y-8 pb-24">
      
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <Calculator className="text-primary" />
          Calculadora de Kelly Criterion
        </h1>
        <p className="text-zinc-500 text-sm md:text-base">
          Gestão de banca baseada em Valor Esperado (EV)
        </p>
        <p className="text-zinc-500 text-sm md:text-base">
          Calcula o stake ideal para apostas de Value-Betting com base na tua avaliação de probabilidade
        </p>
      </div>

      <div className="bg-[#111] border border-zinc-800 rounded-xl p-6 relative overflow-hidden shadow-lg">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
          <Info size={120} className="text-white" />
        </div>
        
        <h3 className="text-zinc-200 font-bold mb-4 flex items-center gap-2 relative z-10">
          <Info size={18} className="text-blue-400" />
          Como usar a Calculadora
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-sm text-zinc-400 relative z-10">
          <div className="flex flex-col gap-2">
            <span className="bg-zinc-800 text-white w-8 h-8 flex items-center justify-center rounded-lg text-sm font-bold border border-zinc-700">1</span>
            <p>Insere a <strong className="text-zinc-300">Odd da Casa</strong> de Apostas.</p>
          </div>
          <div className="flex flex-col gap-2">
            <span className="bg-zinc-800 text-white w-8 h-8 flex items-center justify-center rounded-lg text-sm font-bold border border-zinc-700">2</span>
            <p>Insere a <strong className="text-zinc-300">Probabilidade (%)</strong> que atribuis ao evento.</p>
          </div>
          <div className="flex flex-col gap-2">
            <span className="bg-zinc-800 text-white w-8 h-8 flex items-center justify-center rounded-lg text-sm font-bold border border-zinc-700">3</span>
            <p>Define o valor total da tua <strong className="text-zinc-300">Banca</strong>.</p>
          </div>
          <div className="flex flex-col gap-2">
            <span className="bg-zinc-800 text-white w-8 h-8 flex items-center justify-center rounded-lg text-sm font-bold border border-zinc-700">4</span>
            <p>Resultados <span className="text-red-400 font-bold">Negativos</span> indicam quanto "perdes" em valor teórico.</p>
          </div>
        </div>
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-[#111] border border-zinc-800 rounded-xl p-6 md:p-8 space-y-8 shadow-xl">
            
            <NumberInput 
              label="Odd da Casa" 
              suffix="Decimal"
              value={odd} 
              onChange={setOdd} 
              step={0.05} 
              min={1.01}
              icon={TrendingUp} 
              placeholder="2.10" 
            />

            <NumberInput 
              label="Probabilidade Real" 
              suffix="%"
              value={prob} 
              onChange={setProb} 
              step={1} 
              min={0}
              icon={Percent} 
              placeholder="55" 
            />

            <NumberInput 
              label="Banca Total" 
              suffix="€"
              value={bankroll} 
              onChange={setBankroll} 
              step={10} 
              min={0}
              icon={Wallet} 
              placeholder="1000" 
            />

            <button 
              onClick={calculateKelly}
              className="w-full bg-white text-black font-bold py-4 rounded-xl hover:bg-zinc-200 active:scale-[0.98] transition-all shadow-lg shadow-white/5 mt-4 flex items-center justify-center gap-2"
            >
              <Calculator size={20} />
              Calcular
            </button>
          </div>
        </div>

        <div className="lg:col-span-5 flex flex-col gap-4">
          {!result ? (
            <div className="h-full min-h-[300px] border border-dashed border-zinc-800 rounded-xl flex flex-col items-center justify-center text-zinc-600 gap-4 p-8 text-center bg-zinc-900/20">
              <DollarSign size={48} className="opacity-20" />
              <p className="text-sm">Preenche os dados para ver o cálculo.</p>
            </div>
          ) : (
            <div className={`rounded-xl border p-6 md:p-8 flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 ${result.bgClass}`}>
              
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-lg bg-black/20 ${result.colorClass} shadow-inner`}>
                  {result.icon}
                </div>
                <div>
                  <p className="text-zinc-400 text-[10px] md:text-xs uppercase font-bold tracking-wider">Status</p>
                  <h3 className={`text-lg md:text-xl font-bold ${result.colorClass}`}>{result.status}</h3>
                </div>
              </div>

              <div className="h-px w-full bg-black/10 dark:bg-white/10" />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-black/20 rounded-lg p-4 flex flex-col items-center justify-center text-center">
                  <p className="text-zinc-400 text-[10px] uppercase font-bold mb-1">Stake %</p>
                  <p className={`text-2xl md:text-xl font-mono font-bold ${result.colorClass}`}>
                    {result.pct}%
                  </p>
                </div>
                <div className="bg-black/20 rounded-lg p-4 flex flex-col items-center justify-center text-center">
                  <p className="text-zinc-400 text-[10px] uppercase font-bold mb-1">Valor</p>
                  <p className={`text-2xl md:text-xl font-mono font-bold ${parseFloat(result.pct) <= 0 ? 'text-red-400' : 'text-white'}`}>
                    {result.amount}€
                  </p>
                </div>
              </div>

              <div className="bg-black/20 rounded-lg p-4 text-xs md:text-sm text-zinc-300 leading-relaxed border border-white/5">
                {parseFloat(result.pct) > 0 ? (
                  <>Recomenda-se investir <strong>{result.amount}€</strong> da tua banca nesta aposta.</>
                ) : (
                  <>
                    Valor Esperado Negativo. A odd oferecida ({odd}) está abaixo do preço justo. 
                    <br/><span className="text-red-400 font-bold block mt-2">NÃO APOSTAR.</span>
                  </>
                )}
              </div>

            </div>
          )}
        </div>

      </div>
    </div>
  )
}