'use client'
import { useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Sphere } from '@react-three/drei'
import * as THREE from 'three'  

function AnimatedSphere(props) {
  const meshRef = useRef(null)
  const [hovered, setHover] = useState(false)
  const { viewport } = useThree()
  const currentSpeed = useRef(0.2) 

  useFrame((state, delta) => {
    if (meshRef.current) {
      const targetSpeed = hovered ? 3.0 : 0.2
      currentSpeed.current = THREE.MathUtils.lerp(currentSpeed.current, targetSpeed, 0.05)
      meshRef.current.rotation.x += delta * currentSpeed.current
      meshRef.current.rotation.y += delta * currentSpeed.current
    }
  })

  const responsiveScale = viewport.width < 5 ? viewport.width / 2.5 : 2.2

  return (
    <Sphere
      {...props}
      ref={meshRef}
      args={[1, 64, 64]} 
      scale={responsiveScale}
      onPointerOver={() => setHover(true)}
      onPointerOut={() => setHover(false)}
      onPointerDown={() => setHover(!hovered)}
    >
      <meshStandardMaterial
        color={"#ffffff"}
        wireframe={true} 
      />
    </Sphere>   
  )
}

export default function Hero3D() {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <Canvas>
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 2, 5]} />
        <AnimatedSphere />
      </Canvas>
    </div>
  )
}