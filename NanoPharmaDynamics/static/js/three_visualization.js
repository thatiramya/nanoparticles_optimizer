class ThreeVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        
        this.molecule = null;
        this.nanoparticle = null;
        this.interactions = null;
        
        this.init();
    }
    
    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0xf0f0f0);
        this.container.appendChild(this.renderer.domElement);
        
        // Setup camera
        this.camera.position.z = 5;
        
        // Setup controls
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Add lights
        const ambientLight = new THREE.AmbientLight(0x404040);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(ambientLight, directionalLight);
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Start animation loop
        this.animate();
    }
    
    loadMolecule(data) {
        // Clear existing molecule
        if (this.molecule) {
            this.scene.remove(this.molecule);
        }
        
        // Create molecule group
        this.molecule = new THREE.Group();
        
        // Add atoms
        data.atoms.forEach(atom => {
            const geometry = new THREE.SphereGeometry(atom.radius, 32, 32);
            const material = new THREE.MeshPhongMaterial({ color: atom.color });
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(...atom.position);
            this.molecule.add(sphere);
        });
        
        // Add bonds
        data.bonds.forEach(bond => {
            const atom1 = data.atoms[bond.atom1];
            const atom2 = data.atoms[bond.atom2];
            
            const start = new THREE.Vector3(...atom1.position);
            const end = new THREE.Vector3(...atom2.position);
            const distance = start.distanceTo(end);
            
            const geometry = new THREE.CylinderGeometry(0.1, 0.1, distance, 8);
            const material = new THREE.MeshPhongMaterial({ color: 0x808080 });
            const cylinder = new THREE.Mesh(geometry, material);
            
            // Position and rotate cylinder
            cylinder.position.copy(start).add(end).multiplyScalar(0.5);
            cylinder.lookAt(end);
            cylinder.rotateX(Math.PI / 2);
            
            this.molecule.add(cylinder);
        });
        
        this.scene.add(this.molecule);
    }
    
    loadNanoparticle(data) {
        // Clear existing nanoparticle
        if (this.nanoparticle) {
            this.scene.remove(this.nanoparticle);
        }
        
        // Create nanoparticle
        const geometry = new THREE.SphereGeometry(data.radius, 64, 64);
        const material = new THREE.MeshPhongMaterial({
            color: 0x888888,
            transparent: true,
            opacity: 0.8,
            ...data.surface_properties.texture
        });
        
        this.nanoparticle = new THREE.Mesh(geometry, material);
        this.nanoparticle.position.set(...data.center);
        
        this.scene.add(this.nanoparticle);
    }
    
    showInteractions(data) {
        // Clear existing interactions
        if (this.interactions) {
            this.scene.remove(this.interactions);
        }
        
        // Create interactions group
        this.interactions = new THREE.Group();
        
        data.points.forEach(point => {
            const atom = this.molecule.children[point.atom_index];
            const npPoint = this.nanoparticle.geometry.attributes.position.array.slice(
                point.nanoparticle_point * 3,
                (point.nanoparticle_point + 1) * 3
            );
            
            // Create interaction line
            const geometry = new THREE.BufferGeometry();
            const material = new THREE.LineBasicMaterial({ color: 0xff0000 });
            
            const positions = new Float32Array([
                atom.position.x, atom.position.y, atom.position.z,
                npPoint[0], npPoint[1], npPoint[2]
            ]);
            
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            const line = new THREE.Line(geometry, material);
            
            this.interactions.add(line);
        });
        
        this.scene.add(this.interactions);
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

// Export for use in other files
window.ThreeVisualizer = ThreeVisualizer; 