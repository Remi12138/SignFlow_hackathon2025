declare module "three.meshline" {
    export class MeshLine extends THREE.BufferGeometry {
        setGeometry(geometry: THREE.BufferGeometry | THREE.Vector3[]): void;
    }
    export class MeshLineMaterial extends THREE.Material {
        constructor(parameters?: { color?: THREE.Color | string | number; lineWidth?: number });
    }
}
