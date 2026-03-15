<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Renderer, Program, Mesh, Color, Triangle } from 'ogl'
import './Iridescence.css'

const vertexShader = `
attribute vec2 uv;
attribute vec2 position;

varying vec2 vUv;

void main() {
  vUv = uv;
  gl_Position = vec4(position, 0, 1);
}
`

const fragmentShader = `
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform vec3 uResolution;
uniform vec2 uMouse;
uniform float uAmplitude;
uniform float uSpeed;

varying vec2 vUv;

void main() {
  float mr = min(uResolution.x, uResolution.y);
  vec2 uv = (vUv.xy * 2.0 - 1.0) * uResolution.xy / mr;

  uv += (uMouse - vec2(0.5)) * uAmplitude;

  float d = -uTime * 0.5 * uSpeed;
  float a = 0.0;
  for (float i = 0.0; i < 8.0; ++i) {
    a += cos(i - d - a * uv.x);
    d += sin(uv.y * i + a);
  }
  d += uTime * 0.5 * uSpeed;
  vec3 col = vec3(cos(uv * vec2(d, a)) * 0.6 + 0.4, cos(a + d) * 0.5 + 0.5);
  col = cos(col * cos(vec3(d, a, 2.5)) * 0.5 + 0.5) * uColor;
  gl_FragColor = vec4(col, 1.0);
}
`

const props = defineProps({
  color: { type: Array, default: () => [0.5, 0.6, 0.8] },
  mouseReact: { type: Boolean, default: true },
  amplitude: { type: Number, default: 0.1 },
  speed: { type: Number, default: 1 },
})

const containerRef = ref(null)
let renderer = null
let gl = null
let program = null
let animateId = 0
let mountCtn = null
let handleResize = null
let handleMouseMove = null
const mousePos = { x: 0.5, y: 0.5 }

function getSize(ctn) {
  const w = ctn?.offsetWidth || 0
  const h = ctn?.offsetHeight || 0
  if (w > 0 && h > 0) return [w, h]
  return [window.innerWidth || 800, window.innerHeight || 600]
}

function resize(ctn) {
  if (!ctn || !renderer) return
  const [width, height] = getSize(ctn)
  renderer.setSize(width, height)
  if (program && gl?.canvas) {
    program.uniforms.uResolution.value = new Color(
      gl.canvas.width,
      gl.canvas.height,
      gl.canvas.width / gl.canvas.height
    )
  }
}

onMounted(() => {
  nextTick(() => {
    const ctn = containerRef.value
    if (!ctn) return
    mountCtn = ctn

    try {
      renderer = new Renderer()
      gl = renderer.gl
      gl.clearColor(1, 1, 1, 1)

      const [initW, initH] = getSize(ctn)
      const aspect = initW / initH

      const geometry = new Triangle(gl)
      program = new Program(gl, {
        vertex: vertexShader,
        fragment: fragmentShader,
        uniforms: {
          uTime: { value: 0 },
          uColor: { value: new Color(props.color) },
          uResolution: { value: new Color(initW, initH, aspect) },
          uMouse: { value: new Float32Array([mousePos.x, mousePos.y]) },
          uAmplitude: { value: props.amplitude },
          uSpeed: { value: props.speed },
        },
      })

      const mesh = new Mesh(gl, { geometry, program })
      ctn.appendChild(gl.canvas)
      gl.canvas.style.display = 'block'
      gl.canvas.style.width = '100%'
      gl.canvas.style.height = '100%'

      handleResize = () => resize(ctn)
      window.addEventListener('resize', handleResize)
      resize(ctn)

      const update = (t) => {
        animateId = requestAnimationFrame(update)
        if (!program) return
        program.uniforms.uTime.value = t * 0.001
        program.uniforms.uAmplitude.value = props.amplitude
        program.uniforms.uSpeed.value = props.speed
        program.uniforms.uColor.value = new Color(props.color)
        program.uniforms.uMouse.value[0] = mousePos.x
        program.uniforms.uMouse.value[1] = mousePos.y
        renderer.render({ scene: mesh })
      }
      animateId = requestAnimationFrame(update)

      if (props.mouseReact) {
        handleMouseMove = (e) => {
          const rect = ctn.getBoundingClientRect()
          mousePos.x = (e.clientX - rect.left) / rect.width
          mousePos.y = 1.0 - (e.clientY - rect.top) / rect.height
          if (program) {
            program.uniforms.uMouse.value[0] = mousePos.x
            program.uniforms.uMouse.value[1] = mousePos.y
          }
        }
        ctn.addEventListener('mousemove', handleMouseMove)
      }
    } catch (err) {
      console.error('[Iridescence] WebGL init failed:', err)
    }
  })
})

onUnmounted(() => {
  cancelAnimationFrame(animateId)
  if (handleResize) window.removeEventListener('resize', handleResize)
  if (props.mouseReact && mountCtn && handleMouseMove) {
    mountCtn.removeEventListener('mousemove', handleMouseMove)
  }
  if (mountCtn && gl?.canvas?.parentNode === mountCtn) {
    mountCtn.removeChild(gl.canvas)
  }
  gl?.getExtension('WEBGL_lose_context')?.loseContext()
})
</script>

<template>
  <div ref="containerRef" class="iridescence-container" />
</template>
