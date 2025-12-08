import Link from 'next/link'
import Hero3D from '@/components/ThreeBall'

export default function Home() 
{
  return (
    <main className="relative min-h-screen w-full bg-slate-950 overflow-hidden flex flex-col items-center justify-center">
      
      <div className="absolute inset-0 z-0 opacity-80">
        <Hero3D/>
      </div>

      <div className="z-10 text-center space-y-1 px-4">
        <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white drop-shadow-2xl">
          BICHO
        </h1> 
        <p className="text-slate-300 text-lg md:text-xl max-w-lg mx-auto font-light">
          Football made easy.
        </p>
        <div className="pt-4">
          <Link href="/login">
            <button className="cursor-pointer bg-white hover:bg-white-400 text-black font-bold py-4 px-10 rounded-full text-lg transition duration-300 shadow-white hover:shadow-[0_0_40px_rgba(34,197,94,0.8)]">
              Começar Já
            </button>
          </Link>
        </div>
      </div>

      <div className="absolute bottom-4 text-slate-600 text-xs z-10">
        made by  
        <a href='https://github.com/hgoncalo' className='underline ml-1' target='_blank' rel='noopener noreferrer'>
          @hgoncalo
        </a>
      </div>
    </main>
  )
}