import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

export default function HeroScene() {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0b1119, 0.045);

    const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0.2, 0.4, 6.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    mount.appendChild(renderer.domElement);

    // Environnement pour de vrais reflets métalliques
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

    // Éclairage : key (haut-devant), rim (bas-arrière), top (au-dessus, pour les reflets/ombres du haut)
    scene.add(new THREE.AmbientLight(0x1a2530, 0.5));

    const key = new THREE.DirectionalLight(0xd99b3f, 3);
    key.position.set(3, 4, 3);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.camera.left = -4;
    key.shadow.camera.right = 4;
    key.shadow.camera.top = 4;
    key.shadow.camera.bottom = -4;
    key.shadow.bias = -0.0015;
    scene.add(key);

    const top = new THREE.PointLight(0xffffff, 5, 9);
    top.position.set(0, 4.5, 1.5);
    scene.add(top);

    const rim = new THREE.PointLight(0x4f9bd9, 5, 10);
    rim.position.set(-3, -1.5, -2);
    scene.add(rim);

    // Groupe : sphère de connaissances facettée
    const knowledgeGroup = new THREE.Group();

    const icoGeo = new THREE.IcosahedronGeometry(1.5, 2);
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0xb9c2cc,
      flatShading: true,
      roughness: 0.18,
      metalness: 1,
      clearcoat: 0.4,
      clearcoatRoughness: 0.25,
      envMapIntensity: 1.6,
    });
    const coreMesh = new THREE.Mesh(icoGeo, coreMat);
    coreMesh.castShadow = true;
    coreMesh.receiveShadow = true;
    knowledgeGroup.add(coreMesh);

    // Fines arêtes sombres entre facettes, pour le look "cage" de la référence
    const edgesGeo = new THREE.EdgesGeometry(icoGeo);
    const edgesMat = new THREE.LineBasicMaterial({ color: 0x0b1119, transparent: true, opacity: 0.5 });
    knowledgeGroup.add(new THREE.LineSegments(edgesGeo, edgesMat));

    const vertGeo = new THREE.IcosahedronGeometry(1.5, 1);
    const positionsAttr = vertGeo.attributes.position;
    const vertices = [];
    for (let i = 0; i < positionsAttr.count; i += 3) {
      vertices.push(new THREE.Vector3(positionsAttr.getX(i), positionsAttr.getY(i), positionsAttr.getZ(i)));
    }

    const nodeGeo = new THREE.SphereGeometry(0.05, 16, 16);
    const nodes = [];
    vertices.forEach((v) => {
      const nodeMat = new THREE.MeshPhysicalMaterial({
        color: 0xd99b3f,
        emissive: 0xd99b3f,
        emissiveIntensity: 1.4,
        roughness: 0.2,
        metalness: 0.3,
        clearcoat: 1,
      });
      const node = new THREE.Mesh(nodeGeo, nodeMat);
      node.position.copy(v).multiplyScalar(1.02);
      node.castShadow = true;
      knowledgeGroup.add(node);
      nodes.push(node);
    });

    const linkMat = new THREE.MeshBasicMaterial({ color: 0xd99b3f, transparent: true, opacity: 0.3 });
    for (let i = 0; i < 10; i++) {
      const a = vertices[Math.floor(Math.random() * vertices.length)];
      const b = vertices[Math.floor(Math.random() * vertices.length)];
      if (a === b) continue;
      const mid = a.clone().add(b).multiplyScalar(0.5).multiplyScalar(1.4);
      const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
      const geo = new THREE.TubeGeometry(curve, 24, 0.005, 6, false);
      knowledgeGroup.add(new THREE.Mesh(geo, linkMat));
    }

    knowledgeGroup.position.set(0.6, 0.25, -1.3);
    scene.add(knowledgeGroup);

    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(20, 20),
      new THREE.ShadowMaterial({ opacity: 0.35 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -1.8;
    ground.receiveShadow = true;
    scene.add(ground);

    const particleCount = 90;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 12;
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

    const scrollState = { opacity: 1 };
    function updateScrollFade() {
      const heroHeight = window.innerHeight;
      const fade = 1 - Math.min(window.scrollY / (heroHeight * 0.7), 1);
      scrollState.opacity = fade;
    }
    window.addEventListener('scroll', updateScrollFade, { passive: true });
    updateScrollFade();

    let frameId;
    const clock = new THREE.Clock();
    const mouse = { x: 0, y: 0 };
    const handleMouseMove = (e) => {
      mouse.x = (e.clientX / window.innerWidth - 0.5) * 2;
      mouse.y = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    function animate() {
      const t = clock.getElapsedTime();
      if (!prefersReducedMotion) {
        knowledgeGroup.rotation.y = t * 0.18;
        knowledgeGroup.rotation.x = t * 0.1;
        nodes.forEach((node, i) => {
          const pulse = 1 + Math.sin(t * 2 + i) * 0.25;
          node.scale.setScalar(pulse);
        });
        particles.rotation.y = t * 0.015;
        camera.position.x = 0.2 + mouse.x * 0.3;
        camera.position.y = 0.4 - mouse.y * 0.2;
        camera.lookAt(0.6, 0.1, -1.3);
      }
      knowledgeGroup.visible = scrollState.opacity > 0.02;
      renderer.domElement.style.opacity = scrollState.opacity;
      renderer.render(scene, camera);
      frameId = requestAnimationFrame(animate);
    }
    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', updateScrollFade);
      pmrem.dispose();
      renderer.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={mountRef} className="hero-scene-fixed" />;
}