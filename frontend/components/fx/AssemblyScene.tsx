"use client";

import { useEffect, useRef, type RefObject } from "react";
import * as THREE from "three";

/**
 * Scroll-driven voxel assembly: scattered cubes converge into a hollow
 * cube-shell "core" with a pulsing wireframe icosahedron inside.
 * Progress (0..1) comes from the scroll position of `wrapRef` (the tall
 * pinned hero wrapper). Renders into a full-bleed canvas.
 */
export default function AssemblyScene({
  wrapRef,
  onProgress,
}: {
  wrapRef: RefObject<HTMLElement | null>;
  onProgress?: (p: number) => void;
}) {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    const wrap = wrapRef.current;
    if (!mount || !wrap) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const small = window.innerWidth < 700;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x04060b, 0.028);

    const camera = new THREE.PerspectiveCamera(
      50,
      mount.clientWidth / mount.clientHeight,
      0.1,
      200
    );
    camera.position.set(0, 1.2, 17);

    scene.add(new THREE.AmbientLight(0x2a3a55, 1.6));
    const key = new THREE.DirectionalLight(0x9adfff, 2.2);
    key.position.set(6, 10, 8);
    scene.add(key);
    const rim = new THREE.PointLight(0x3ce8ff, 30, 40);
    rim.position.set(-8, -4, 6);
    scene.add(rim);

    const group = new THREE.Group();
    scene.add(group);

    // --- voxel shell targets: hollow N×N×N cube ---
    const N = small ? 6 : 8;
    const GAP = 1.06;
    const targets: THREE.Vector3[] = [];
    const half = ((N - 1) * GAP) / 2;
    for (let x = 0; x < N; x++)
      for (let y = 0; y < N; y++)
        for (let z = 0; z < N; z++) {
          const edge = x === 0 || y === 0 || z === 0 || x === N - 1 || y === N - 1 || z === N - 1;
          if (!edge) continue;
          targets.push(new THREE.Vector3(x * GAP - half, y * GAP - half, z * GAP - half));
        }
    const COUNT = targets.length;

    const rng = (seed => () => {
      // deterministic PRNG so SSR/CSR and re-mounts look identical
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    })(20260611);

    const starts: THREE.Vector3[] = [];
    const delays: number[] = [];
    const axes: THREE.Vector3[] = [];
    const spins: number[] = [];
    for (let i = 0; i < COUNT; i++) {
      const r = 13 + rng() * 9;
      const theta = rng() * Math.PI * 2;
      const phi = Math.acos(2 * rng() - 1);
      starts.push(
        new THREE.Vector3(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.sin(phi) * Math.sin(theta) * 0.7,
          r * Math.cos(phi) * 0.6 - 2
        )
      );
      delays.push(rng() * 0.55);
      axes.push(new THREE.Vector3(rng() - 0.5, rng() - 0.5, rng() - 0.5).normalize());
      spins.push((rng() - 0.5) * 9);
    }

    const box = new THREE.BoxGeometry(0.78, 0.78, 0.78);
    const mat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const cubes = new THREE.InstancedMesh(box, mat, COUNT);
    cubes.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    const cSteel = new THREE.Color(0x0d1b2e);
    const cCyan = new THREE.Color(0x2bd9f2);
    const cAmber = new THREE.Color(0xff9d3b);
    for (let i = 0; i < COUNT; i++) {
      const roll = rng();
      cubes.setColorAt(i, roll > 0.94 ? cAmber : roll > 0.82 ? cCyan : cSteel);
    }
    group.add(cubes);

    // --- inner core: wireframe icosahedron, appears late ---
    const coreGeo = new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(2.4, 1));
    const coreMat = new THREE.LineBasicMaterial({
      color: 0x3ce8ff,
      transparent: true,
      opacity: 0,
    });
    const core = new THREE.LineSegments(coreGeo, coreMat);
    group.add(core);

    // --- ambient particles ---
    const pCount = small ? 350 : 800;
    const pPos = new Float32Array(pCount * 3);
    for (let i = 0; i < pCount * 3; i++) pPos[i] = (rng() - 0.5) * 60;
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({
      color: 0x4db8d8,
      size: 0.05,
      transparent: true,
      opacity: 0.55,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    const points = new THREE.Points(pGeo, pMat);
    scene.add(points);

    // --- floor grid ---
    const grid = new THREE.GridHelper(80, 60, 0x123349, 0x0a1a28);
    (grid.material as THREE.Material).transparent = true;
    (grid.material as THREE.Material).opacity = 0.5;
    grid.position.y = -7.5;
    scene.add(grid);

    // --- scroll progress + mouse parallax ---
    let progress = reduced ? 1 : 0;
    let shown = -1;
    const readProgress = () => {
      const total = wrap.offsetHeight - window.innerHeight;
      if (total <= 0) return 1;
      const top = wrap.getBoundingClientRect().top;
      return Math.min(Math.max(-top / total, 0), 1);
    };

    let mx = 0;
    let my = 0;
    const onMouse = (e: MouseEvent) => {
      mx = (e.clientX / window.innerWidth - 0.5) * 2;
      my = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener("mousemove", onMouse, { passive: true });

    const ease = (t: number) => 1 - Math.pow(1 - t, 3);
    const dummy = new THREE.Object3D();
    const quat = new THREE.Quaternion();

    const layout = (p: number, t: number) => {
      for (let i = 0; i < COUNT; i++) {
        const lp = ease(Math.min(Math.max((p - delays[i]) / 0.45, 0), 1));
        dummy.position.lerpVectors(starts[i], targets[i], lp);
        // drift while unassembled
        const drift = (1 - lp) * 0.6;
        dummy.position.x += Math.sin(t * 0.5 + i) * drift;
        dummy.position.y += Math.cos(t * 0.4 + i * 1.7) * drift;
        quat.setFromAxisAngle(axes[i], spins[i] * (1 - lp));
        dummy.quaternion.copy(quat);
        const s = 0.55 + 0.45 * lp;
        dummy.scale.setScalar(s);
        dummy.updateMatrix();
        cubes.setMatrixAt(i, dummy.matrix);
      }
      cubes.instanceMatrix.needsUpdate = true;

      const cp = Math.min(Math.max((p - 0.62) / 0.38, 0), 1);
      coreMat.opacity = cp * 0.9;
      const pulse = 1 + Math.sin(t * 2.2) * 0.04 * cp;
      core.scale.setScalar((0.4 + 0.6 * cp) * pulse);
      core.rotation.y = t * 0.4;
      core.rotation.x = t * 0.23;
    };

    let raf = 0;
    let running = true;
    const clock = new THREE.Clock();

    const frame = () => {
      if (!running) return;
      raf = requestAnimationFrame(frame);
      const t = clock.getElapsedTime();
      if (!reduced) progress = readProgress();
      if (Math.abs(progress - shown) > 0.001) {
        shown = progress;
        onProgress?.(progress);
      }
      layout(progress, t);
      group.rotation.y = t * 0.08 + progress * Math.PI * 0.6;
      group.rotation.x = Math.sin(t * 0.15) * 0.05 + progress * 0.12;
      points.rotation.y = t * 0.012;
      camera.position.x += (mx * 1.4 - camera.position.x) * 0.04;
      camera.position.y += (1.2 - my * 1.1 - camera.position.y) * 0.04;
      camera.position.z = 17 - progress * 3.5;
      camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
    };
    frame();

    // pause when the hero is fully out of view
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !running) {
        running = true;
        clock.start();
        frame();
      } else if (!entry.isIntersecting && running) {
        running = false;
        cancelAnimationFrame(raf);
      }
    });
    io.observe(wrap);

    const onResize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", onResize);

    return () => {
      running = false;
      cancelAnimationFrame(raf);
      io.disconnect();
      window.removeEventListener("resize", onResize);
      window.removeEventListener("mousemove", onMouse);
      box.dispose();
      mat.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      pGeo.dispose();
      pMat.dispose();
      (grid.material as THREE.Material).dispose();
      grid.geometry.dispose();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [wrapRef, onProgress]);

  return <div ref={mountRef} className="hero-canvas" aria-hidden="true" />;
}
