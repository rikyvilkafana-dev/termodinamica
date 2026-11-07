const registros = [];
let graficoMacro = null, graficoComidas = null;
const $ = id => document.getElementById(id);
const fmt = n => Number(n).toLocaleString("es-PE", {maximumFractionDigits:1});

function pintarTabla(){
  $("contador").textContent = `${registros.length} alimento(s)`;
  if(!registros.length){
    $("lista").innerHTML = '<tr><td colspan="6" class="empty">Aún no hay alimentos registrados ♡</td></tr>';
    return;
  }
  $("lista").innerHTML = registros.map((r,i)=>`<tr>
    <td>${r.comida}</td><td>${r.nombre}</td><td>${fmt(r.servido)} g</td>
    <td>${fmt(r.sobrante)} g</td><td><b>${fmt(r.servido-r.sobrante)} g</b></td>
    <td><button class="delete" data-del="${i}" type="button">Quitar</button></td></tr>`).join("");
}
$("agregar").addEventListener("click",()=>{
  const servido=Number($("servido").value), sobrante=Number($("sobrante").value);
  if(!$("servido").value || servido<=0 || sobrante<0 || sobrante>servido){
    $("mensaje").textContent="Ingresa gramos válidos: el sobrante no puede superar lo servido.";return;
  }
  registros.push({comida:$("comida").value,nombre:$("alimento").value,servido,sobrante});
  $("servido").value="";$("sobrante").value="0";$("mensaje").textContent="";
  pintarTabla();
});
$("lista").addEventListener("click",e=>{
  const b=e.target.closest("[data-del]");if(!b)return;
  registros.splice(Number(b.dataset.del),1);pintarTabla();
});
$("limpiar").addEventListener("click",()=>{
  registros.length=0;pintarTabla();$("resultados").classList.add("hidden");$("mensaje").textContent="Registro limpiado.";
});
function graficar(data){
  if(graficoMacro)graficoMacro.destroy();if(graficoComidas)graficoComidas.destroy();
  graficoMacro=new Chart($("macroChart"),{type:"doughnut",data:{
    labels:["Proteínas (g)","Carbohidratos (g)","Lípidos (g)"],
    datasets:[{data:[data.total.proteinas,data.total.carbohidratos,data.total.lipidos],
    backgroundColor:["#d979a1","#f0b9cf","#9e6680"],borderColor:"#fff",borderWidth:3}]},
    options:{responsive:true,plugins:{legend:{position:"bottom"}}}});
  const comidas=data.por_comida||{};
  graficoComidas=new Chart($("mealChart"),{type:"bar",data:{
    labels:Object.keys(comidas),datasets:[{label:"Kcal",data:Object.values(comidas).map(x=>x.kcal),
    backgroundColor:"#df91b2",borderRadius:7}]},
    options:{responsive:true,scales:{y:{beginAtZero:true}},plugins:{legend:{display:false}}}});
}
$("calcular").addEventListener("click",async()=>{
  $("mensaje").textContent="";
  const payload={edad:$("edad").value,peso:$("peso").value,talla:$("talla").value,
    actividad:$("actividad").value,alimentos:registros};
  if(!payload.edad||!payload.peso||!payload.talla){$("mensaje").textContent="Completa edad, peso y talla.";return;}
  if(!registros.length){$("mensaje").textContent="Agrega al menos un alimento.";return;}
  const btn=$("calcular");btn.disabled=true;btn.textContent="Calculando…";
  try{
    const res=await fetch("/api/calcular",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data=await res.json();if(!res.ok)throw new Error(data.error||"Error de cálculo.");
    $("imc").textContent=fmt(data.imc);$("meta").textContent=fmt(data.meta_kcal);
    $("kcal").textContent=fmt(data.total.kcal);
    $("balance").textContent=(data.balance>0?"+":"")+fmt(data.balance);
    $("estado").textContent=data.estado;$("proteinas").textContent=fmt(data.total.proteinas);
    $("carbohidratos").textContent=fmt(data.total.carbohidratos);
    $("lipidos").textContent=fmt(data.total.lipidos);$("adecuacion").textContent=fmt(data.adecuacion)+"%";
    graficar(data);$("resultados").classList.remove("hidden");
    $("resultados").scrollIntoView({behavior:"smooth"});
  }catch(err){$("mensaje").textContent=err.message;}
  finally{btn.disabled=false;btn.innerHTML='Calcular balance nutricional <b>♡</b>';}
});
pintarTabla();
