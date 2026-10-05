/**
 * 3D Student Skill Polyhedron & Holographic Mesh
 * Renders an interactive 3D crystal whose vertices deform based on student skill ratings.
 */

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('three-skill-canvas');
  if (!container) return;

  const studentId = container.getAttribute('data-student-id') || '1';

  const scene = new THREE.Scene();
  const width = container.clientWidth;
  const height = container.clientHeight || 280;

  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
  camera.position.set(0, 0, 9);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
  scene.add(ambientLight);

  const cyanLight = new THREE.PointLight(0x06b6d4, 2.5, 30);
  cyanLight.position.set(5, 5, 5);
  scene.add(cyanLight);

  const purpleLight = new THREE.PointLight(0x8b5cf6, 2, 30);
  purpleLight.position.set(-5, -5, 5);
  scene.add(purpleLight);

  // Skill Crystal Group
  const crystalGroup = new THREE.Group();
  scene.add(crystalGroup);

  // Create base icosahedron crystal
  const geo = new THREE.IcosahedronGeometry(2.4, 0);
  
  // Wireframe outer cage
  const wireMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    wireframe: true,
    transparent: true,
    opacity: 0.65
  });
  const wireMesh = new THREE.Mesh(geo, wireMat);
  crystalGroup.add(wireMesh);

  // Translucent inner jewel
  const innerMat = new THREE.MeshPhongMaterial({
    color: 0x6366f1,
    emissive: 0x1e1b4b,
    shininess: 90,
    transparent: true,
    opacity: 0.75,
    flatShading: true
  });
  const innerMesh = new THREE.Mesh(geo, innerMat);
  innerMesh.scale.set(0.92, 0.92, 0.92);
  crystalGroup.add(innerMesh);

  // Glowing vertices
  const vertexMat = new THREE.PointsMaterial({
    color: 0x22d3ee,
    size: 0.25,
    blending: THREE.AdditiveBlending
  });
  const vertexPoints = new THREE.Points(geo, vertexMat);
  crystalGroup.add(vertexPoints);

  // Fetch student skill vectors from API
  fetch(`/api/student-skills/${studentId}`)
    .then(res => res.json())
    .then(data => {
      if (data && data.skills_vector) {
        const v = data.skills_vector;
        const scaleX = (v.problem_solving || 80) / 75;
        const scaleY = (v.web_architecture || 80) / 75;
        const scaleZ = (v.database_systems || 80) / 75;
        crystalGroup.scale.set(scaleX, scaleY, scaleZ);
      }
    })
    .catch(() => {});

  // Animation Loop
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    crystalGroup.rotation.y = t * 0.45;
    crystalGroup.rotation.x = Math.sin(t * 0.3) * 0.35;
    crystalGroup.rotation.z = Math.cos(t * 0.25) * 0.2;

    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener('resize', () => {
    if (!container) return;
    const newW = container.clientWidth;
    const newH = container.clientHeight || 280;
    camera.aspect = newW / newH;
    camera.updateProjectionMatrix();
    renderer.setSize(newW, newH);
  });
});
