/**
 * 3D Holographic Placement Analytics Visualization
 * Visualizes department placement rates and salary distributions in 3D WebGL
 */

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('three-analytics-canvas');
  if (!container) return;

  const scene = new THREE.Scene();
  const width = container.clientWidth;
  const height = container.clientHeight || 360;

  const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
  camera.position.set(0, 14, 28);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // Lighting
  const ambient = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambient);

  const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.8);
  dirLight.position.set(10, 20, 15);
  scene.add(dirLight);

  const purpleLight = new THREE.PointLight(0xa855f7, 2, 50);
  purpleLight.position.set(-10, 5, -10);
  scene.add(purpleLight);

  // Grid Base Plane
  const gridHelper = new THREE.GridHelper(30, 20, 0x4f46e5, 0x1e293b);
  gridHelper.position.y = -0.05;
  scene.add(gridHelper);

  const barsGroup = new THREE.Group();
  scene.add(barsGroup);

  // Fetch Live Analytics Data
  fetch('/api/3d-analytics')
    .then(res => res.json())
    .then(data => {
      render3DCharts(data);
    })
    .catch(() => {
      // Fallback data
      render3DCharts({
        departments: [
          { department: 'CSE', placement_percentage: 96.5 },
          { department: 'IT', placement_percentage: 92.0 },
          { department: 'ECE', placement_percentage: 88.4 },
          { department: 'EEE', placement_percentage: 82.5 },
          { department: 'MECH', placement_percentage: 79.2 }
        ]
      });
    });

  function render3DCharts(data) {
    const depts = data.departments || [];
    const count = depts.length;
    const spacing = 4.2;
    const startX = -((count - 1) * spacing) / 2;

    const colors = [0x6366f1, 0x06b6d4, 0x10b981, 0x8b5cf6, 0xf59e0b];

    depts.forEach((item, idx) => {
      const height = (item.placement_percentage / 100) * 11;
      
      // Cylindrical 3D Bar
      const geo = new THREE.CylinderGeometry(1.2, 1.2, height, 28);
      const mat = new THREE.MeshStandardMaterial({
        color: colors[idx % colors.length],
        metalness: 0.6,
        roughness: 0.2,
        emissive: colors[idx % colors.length],
        emissiveIntensity: 0.35,
        transparent: true,
        opacity: 0.92
      });

      const cylinder = new THREE.Mesh(geo, mat);
      cylinder.position.set(startX + idx * spacing, height / 2, 0);
      barsGroup.add(cylinder);

      // Glowing top crown ring
      const topRingGeo = new THREE.TorusGeometry(1.25, 0.08, 16, 32);
      const topRingMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const topRing = new THREE.Mesh(topRingGeo, topRingMat);
      topRing.rotation.x = Math.PI / 2;
      topRing.position.set(startX + idx * spacing, height, 0);
      barsGroup.add(topRing);
    });
  }

  // Animation Loop
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // Gentle oscillation and slow rotation
    barsGroup.rotation.y = Math.sin(t * 0.4) * 0.25;
    camera.lookAt(0, 4, 0);
    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener('resize', () => {
    if (!container) return;
    const newW = container.clientWidth;
    const newH = container.clientHeight || 360;
    camera.aspect = newW / newH;
    camera.updateProjectionMatrix();
    renderer.setSize(newW, newH);
  });
});
