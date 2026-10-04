const {chromium}=require('/opt/node-tools/node_modules/playwright');
const fs=require('fs');
const P='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/';
(async()=>{
 fs.mkdirSync(P+'png',{recursive:true});
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
 for(const n of process.argv.slice(2)){
  let s=fs.readFileSync(P+'konzept1/project/'+n,'utf8');
  const m=s.match(/"width":(\d+),"height":(\d+)/); const w=+m[1],h=+m[2];
  s=s.replace(/<script[\s\S]*?<\/script>/g,'').replace(/<\/?helmet>|<\/?x-dc>/g,'');
  fs.writeFileSync(P+'png/_t.html',s);
  const pg=await b.newPage({viewport:{width:w,height:h}});
  await pg.goto('file://'+P+'png/_t.html'); await pg.waitForTimeout(150);
  await pg.screenshot({path:P+'png/'+n.replace('.dc.html','.png')}); await pg.close();
 }
 await b.close();
})();
