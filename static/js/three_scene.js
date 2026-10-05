/**
 * 3D Interactive Campus Placement Arena & Career Galaxy
 * Built with Three.js WebGL & Raycasting
 */

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('three-hero-canvas');
  if (!container) return;

  // Scene, Camera, Renderer
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0b0f19, 0.015);

  const width = container.clientWidth;
  const height = container.clientHeight || 480;

  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 18, 38);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  container.appendChild(renderer.domElement);

  // Tooltip Element
  const tooltip = document.getElementById('three-tooltip') || createTooltip(container);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambientLight);

  const pointLight = new THREE.PointLight(0x6366f1, 2.5, 80);
  pointLight.position.set(0, 12, 0);
  scene.add(pointLight);

  const cyanLight = new THREE.PointLight(0x06b6d4, 2, 70);
  cyanLight.position.set(-15, -5, 10);
  scene.add(cyanLight);

  // Central Placement Hub 2026 Core
  const coreGroup = new THREE.Group();
  scene.add(coreGroup);

  const coreGeometry = new THREE.IcosahedronGeometry(3.6, 2);
  const coreMaterial = new THREE.MeshPhongMaterial({
    color: 0x4f46e5,
    emissive: 0x221370,
    wireframe: true,
    transparent: true,
    opacity: 0.85
  });
  const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
  coreGroup.add(coreMesh);

  // Inner glowing core
  const innerGeo = new THREE.SphereGeometry(2.4, 24, 24);
  const innerMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    wireframe: false,
    transparent: true,
    opacity: 0.6
  });
  const innerCore = new THREE.Mesh(innerGeo, innerMat);
  coreGroup.add(innerCore);

  // Surrounding Particle Dust Field
  const particleCount = 750;
  const particlesGeo = new THREE.BufferGeometry();
  const particlePositions = new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount * 3; i += 3) {
    particlePositions[i] = (Math.random() - 0.5) * 80;
    particlePositions[i + 1] = (Math.random() - 0.5) * 45;
    particlePositions[i + 2] = (Math.random() - 0.5) * 80;
  }
  particlesGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

  const particlesMat = new THREE.PointsMaterial({
    size: 0.35,
    color: 0x818cf8,
    transparent: true,
    opacity: 0.65,
    blending: THREE.AdditiveBlending
  });
  const starField = new THREE.Points(particlesGeo, particlesMat);
  scene.add(starField);

  // Orbit Rings & Company Satellite Nodes
  const nodesGroup = new THREE.Group();
  scene.add(nodesGroup);
  const interactiveNodes = [];

  // Fetch live company data from backend API
  fetch('/api/3d-arena-data')
    .then(res => res.json())
    .then(data => {
      buildCompanySatellites(data.nodes || []);
    })
    .catch(() => {
      // Fallback local nodes if API unavailable
      buildCompanySatellites([
        { name: 'Google', code: 'GOOGL', tier: 'Super Dream', maxPackage: 44.5, color: '#8b5cf6', position: { x: 14, y: 1.5, z: 0 } },
        { name: 'Microsoft', code: 'MSFT', tier: 'Super Dream', maxPackage: 42.0, color: '#8b5cf6', position: { x: 0, y: -2, z: 15 } },
        { name: 'Amazon', code: 'AMZN', tier: 'Super Dream', maxPackage: 38.0, color: '#8b5cf6', position: { x: -14, y: 2, z: 0 } },
        { name: 'Cisco Systems', code: 'CSCO', tier: 'Dream', maxPackage: 18.5, color: '#3b82f6', position: { x: 0, y: 3, z: -15 } },
        { name: 'Deloitte USI', code: 'DLTE', tier: 'Dream', maxPackage: 12.0, color: '#3b82f6', position: { x: 10, y: -1.5, z: 10 } },
        { name: 'TCS Prime', code: 'TCS', tier: 'Core', maxPackage: 9.0, color: '#10b981', position: { x: -10, y: 1.8, z: -10 } }
      ]);
    });

  function buildCompanySatellites(companies) {
    // Clear previous
    while (nodesGroup.children.length > 0) {
      nodesGroup.remove(nodesGroup.children[0]);
    }
    interactiveNodes.length = 0;

    companies.forEach((comp, idx) => {
      const nodeObj = new THREE.Group();
      
      // Node Sphere
      const size = comp.tier === 'Super Dream' ? 1.4 : comp.tier === 'Dream' ? 1.15 : 0.95;
      const geo = new THREE.SphereGeometry(size, 20, 20);
      const colorHex = parseInt(comp.color.replace('#', '0x')) || 0x6366f1;
      
      const mat = new THREE.MeshStandardMaterial({
        color: colorHex,
        emissive: colorHex,
        emissiveIntensity: 0.45,
        roughness: 0.3,
        metalness: 0.7
      });

      const sphere = new THREE.Mesh(geo, mat);
      sphere.userData = comp;
      nodeObj.add(sphere);

      // Outer Pulsing Orbit Ring for node
      const ringGeo = new THREE.RingGeometry(size * 1.3, size * 1.45, 24);
      const ringMat = new THREE.MeshBasicMaterial({
        color: colorHex,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.45
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      nodeObj.add(ring);

      nodeObj.position.set(comp.position.x, comp.position.y, comp.position.z);
      nodesGroup.add(nodeObj);
      interactiveNodes.push(sphere);

      // Draw dashed trajectory orbit connecting to center
      const radius = Math.sqrt(comp.position.x * comp.position.x + comp.position.z * comp.position.z);
      const orbitLineGeo = new THREE.BufferGeometry();
      const points = [];
      for (let theta = 0; theta <= Math.PI * 2; theta += 0.1) {
        points.push(new THREE.Vector3(Math.cos(theta) * radius, comp.position.y * 0.3, Math.sin(theta) * radius));
      }
      orbitLineGeo.setFromPoints(points);
      const orbitLineMat = new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.25 });
      const orbitLine = new THREE.Line(orbitLineGeo, orbitLineMat);
      scene.add(orbitLine);
    });
  }

  // Mouse Raycaster Setup
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let hoveredNode = null;

  function onMouseMove(event) {
    const rect = container.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(interactiveNodes);

    if (intersects.length > 0) {
      const target = intersects[0].object;
      if (hoveredNode !== target) {
        if (hoveredNode) hoveredNode.scale.set(1, 1, 1);
        hoveredNode = target;
        hoveredNode.scale.set(1.35, 1.35, 1.35);
      }
      container.style.cursor = 'pointer';
      showTooltip(event, target.userData);
    } else {
      if (hoveredNode) {
        hoveredNode.scale.set(1, 1, 1);
        hoveredNode = null;
      }
      container.style.cursor = 'default';
      hideTooltip();
    }
  }

  container.addEventListener('mousemove', onMouseMove);
  container.addEventListener('mouseleave', () => {
    hideTooltip();
    if (hoveredNode) {
      hoveredNode.scale.set(1, 1, 1);
      hoveredNode = null;
    }
  });

  function createTooltip(parent) {
    const tt = document.createElement('div');
    tt.id = 'three-tooltip';
    tt.className = 'three-tooltip';
    parent.appendChild(tt);
    return tt;
  }

  function showTooltip(event, data) {
    const rect = container.getBoundingClientRect();
    tooltip.style.display = 'block';
    tooltip.style.left = `${event.clientX - rect.left + 15}px`;
    tooltip.style.top = `${event.clientY - rect.top + 15}px`;
    tooltip.innerHTML = `
      <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-bottom: 2px;">
        ${data.name} <span style="font-size: 0.75rem; color: #38bdf8;">[${data.code || ''}]</span>
      </div>
      <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px;">Tier: <span style="color: #cbd5e1; font-weight: 600;">${data.tier}</span></div>
      <div style="font-size: 0.8rem; color: #34d399; font-weight: 700;">Top CTC: ${data.maxPackage} LPA</div>
      <div style="font-size: 0.75rem; color: #818cf8; margin-top: 4px;">Click to explore recruitment profile</div>
    `;
  }

  function hideTooltip() {
    tooltip.style.display = 'none';
  }

  // Animation Loop
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime();

    // Central Core Pulse & Rotation
    coreMesh.rotation.y = elapsedTime * 0.35;
    coreMesh.rotation.x = elapsedTime * 0.2;
    innerCore.rotation.y = -elapsedTime * 0.5;

    // Orbit nodes rotation
    nodesGroup.rotation.y = elapsedTime * 0.08;

    // Starfield subtle drift
    starField.rotation.y = -elapsedTime * 0.02;

    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }

  animate();

  // Responsive Resize
  window.addEventListener('resize', () => {
    if (!container) return;
    const newWidth = container.clientWidth;
    const newHeight = container.clientHeight || 480;
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(newWidth, newHeight);
  });
});
