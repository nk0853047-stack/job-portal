
document.addEventListener("DOMContentLoaded",()=> {
  document.querySelectorAll(".job-card").forEach((card,i)=>{
    card.style.opacity="0"; card.style.transform="translateY(10px)";
    setTimeout(()=>{card.style.transition="all .45s ease";card.style.opacity="1";card.style.transform="translateY(0)"},i*80);
  });
});
