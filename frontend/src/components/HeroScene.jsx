import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function HeroScene() {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0b1119, 0.05);

    const camera = new THREE.PerspectiveCamera(45, mount.clientWidth / mount.clientHeight, 0.1, 100);
    camera.position.set(0, 0.3, 6);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    // Éclairage
    scene.add(new THREE.AmbientLight(0x1a2530, 1.4));
    const key = new THREE.PointLight(0xd99b3f, 8, 12);
    key.position.set(3, 2, 3);
    scene.add(key);
    const rim = new THREE.PointLight(0x4f9bd9, 4, 12);
    rim.position.set(-3, -1, -2);
    scene.add(rim);

    // Groupe principal : sphère de connaissances
    const knowledgeGroup = new THREE.Group();

    // Coeur en wireframe (icosaèdre)
    const icoGeo = new THREE.IcosahedronGeometry(1.6, 1);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x2f4054,
      wireframe: true,
      transparent: true,
      opacity: 0.5,
    });
    const wireMesh = new THREE.Mesh(icoGeo, wireMat);
    knowledgeGroup.add(wireMesh);

    // Coeur plein, léger, translucide
    const coreGeo = new THREE.IcosahedronGeometry(1.58, 1);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x17212b,
      roughness: 0.4,
      metalness: 0.3,
      transparent: true,
      opacity: 0.55,
    });
    knowledgeGroup.add(new THREE.Mesh(coreGeo, coreMat));

    // Noeuds lumineux aux sommets
    const positionsAttr = icoGeo.attributes.position;
    const vertices = [];
    for (let i = 0; i < positionsAttr.count; i += 3) {
      vertices.push(new THREE.Vector3(
        positionsAttr.getX(i), positionsAttr.getY(i), positionsAttr.getZ(i)
      ));
    }
    const nodeGeo = new THREE.SphereGeometry(0.045, 12, 12);
    const nodeMat = new THREE.MeshStandardMaterial({
      color: 0xd99b3f,
      emissive: 0xd99b3f,
      emissiveIntensity: 1.6,
      roughness: 0.3,
    });
    const nodes = [];
    vertices.forEach((v) => {
      const node = new THREE.Mesh(nodeGeo, nodeMat.clone());
      node.position.copy(v);
      knowledgeGroup.add(node);
      nodes.push(node);
    });

    // Arcs "requête → source" reliant des sommets non adjacents (effet graphe RAG)
    const linkMat = new THREE.LineBasicMaterial({ color: 0xd99b3f, transparent: true, opacity: 0.35 });
    const linkCount = 10;
    for (let i = 0; i < linkCount; i++) {
      const a = vertices[Math.floor(Math.random() * vertices.length)];
      const b = vertices[Math.floor(Math.random() * vertices.length)];
      if (a === b) continue;
      const mid = a.clone().add(b).multiplyScalar(0.5).multiplyScalar(1.35);
      const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
      const geo = new THREE.TubeGeometry(curve, 20, 0.004, 6, false);
      knowledgeGroup.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xd99b3f, transparent: true, opacity: 0.4 })));
    }

    scene.add(knowledgeGroup);

    // Poussière de données en arrière-plan
    const particleCount = 90;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 8;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 6 - 2;
    }
    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particles = new THREE.Points(
      particleGeo,
      new THREE.PointsMaterial({ color: 0x4f9bd9, size: 0.03, transparent: true, opacity: 0.4 })
    );
    scene.add(particles);

    let frameId;
    const clock = new THREE.Clock();
    const mouse = { x: 0, y: 0 };
    const handleMouseMove = (e) => {
      const rect = mount.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      mouse.y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    function animate() {
      const t = clock.getElapsedTime();
      if (!prefersReducedMotion) {
        knowledgeGroup.rotation.y = t * 0.18;
        knowledgeGroup.rotation.x = t * 0.12;
        nodes.forEach((node, i) => {
          const pulse = 1 + Math.sin(t * 2 + i) * 0.25;
          node.scale.setScalar(pulse);
        });
        particles.rotation.y = t * 0.015;
        camera.position.x = mouse.x * 0.5;
        camera.position.y = 0.3 - mouse.y * 0.3;
        camera.lookAt(0, 0, 0);
      }
      renderer.render(scene, camera);
      frameId = requestAnimationFrame(animate);
    }
    animate();

    const resizeObserver = new ResizeObserver(() => {
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    });
    resizeObserver.observe(mount);

    return () => {
      cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      window.removeEventListener('mousemove', handleMouseMove);
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={mountRef} className="hero-scene" />;
}