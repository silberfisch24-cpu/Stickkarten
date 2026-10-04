const {chromium}=require('/opt/node-tools/node_modules/playwright');
const fs=require('fs');
const P='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/png/';
(async()=>{
 const out=process.argv[2], names=process.argv.slice(3);
 const html='<body style="margin:0;background:#888;display:flex;gap:10px;align-items:flex-start">'+names.map(n=>`<img style="height:420px" src="file://${P}${n}.png">`).join('')+'</body>';
 fs.writeFileSync(P+'_m.html',html);
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
 const pg=await b.newPage({viewport:{width:200,height:200}}); await pg.goto('file://'+P+'_m.html'); await pg.waitForTimeout(300);
 await pg.screenshot({path:P+out+'.png',fullPage:true}); await b.close();
})();
