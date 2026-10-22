import * as THREE from 'https://esm.sh/three@0.164.1';
import {OrbitControls} from 'https://esm.sh/three@0.164.1/examples/jsm/controls/OrbitControls.js';
import {GLTFExporter} from 'https://esm.sh/three@0.164.1/examples/jsm/exporters/GLTFExporter.js';
const mount=document.querySelector('#scene'), status=document.querySelector('#status');
const scene=new THREE.Scene();scene.background=new THREE.Color('#101a2a');
const camera=new THREE.PerspectiveCamera(40,1,.1,100);camera.position.set(3,2.5,5.5);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));mount.append(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x39445a,2.6));
const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(3,7,5);scene.add(light);
const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,1,0);controls.enableDamping=true;controls.update();
const ground=new THREE.Mesh(new THREE.CircleGeometry(2.5,64),new THREE.MeshStandardMaterial({color:0x29384b,roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-.03;scene.add(ground);
let character;
function buildCharacter(shape='average'){
 if(character)scene.remove(character);
 character=new THREE.Group();character.name='Procedural human mannequin';
 const skin=new THREE.MeshStandardMaterial({color:0xb9876e,roughness:.8}),cloth=new THREE.MeshStandardMaterial({color:0x527e9b,roughness:.85}),pants=new THREE.MeshStandardMaterial({color:0x283a54,roughness:.9});
 const width=shape==='broad'?1.22:shape==='slim'?.82:1;
 function part(radius,length,x,y,z,mat,rx=0,rz=0){const mesh=new THREE.Mesh(new THREE.CapsuleGeometry(radius,Math.max(.01,length-2*radius),6,12),mat);mesh.position.set(x,y,z);mesh.rotation.set(rx,0,rz);character.add(mesh);return mesh;}
 part(.31*width,.8,0,1.48,0,cloth);
 part(.20,.40,0,2.16,0,skin);
 part(.105,.78,-.36*width,1.44,0,skin,0,0,-.12);
 part(.105,.78,.36*width,1.44,0,skin,0,0,.12);
 part(.15,.85,-.17,0.57,0,pants);
 part(.15,.85,.17,0.57,0,pants);
 part(.16,.32,-.17,.13,.12,pants,Math.PI/2);
 part(.16,.32,.17,.13,.12,pants,Math.PI/2);
 scene.add(character);
}
buildCharacter();
function resize(){const w=mount.clientWidth,h=mount.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}
new ResizeObserver(resize).observe(mount);resize();
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera)});
document.querySelector('#preview').onclick=()=>{buildCharacter(document.querySelector('#build').value);status.textContent='Procedural mannequin updated. Your prompt is a concept note only.'};
document.querySelector('#generate').onclick=()=>{status.textContent='AI generation is not connected. Configure and test an inference provider on the backend first.'};
document.querySelector('#export').onclick=async()=>{try{const exporter=new GLTFExporter();const data=await exporter.parseAsync(character,{binary:true});const url=URL.createObjectURL(new Blob([data],{type:'model/gltf-binary'}));const a=document.createElement('a');a.href=url;a.download='character-preview.glb';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Procedural GLB exported.'}catch(e){status.textContent='Export failed: '+e.message}};
