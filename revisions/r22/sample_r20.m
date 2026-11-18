root=fullfile('C:/Users/14694/Documents/Codex/D-drive-transfer/Codex Projects/SRT','engineering','tire-compound-refit-2026-10-01');
addpath(genpath(fullfile(root,'library-src')));
out=fullfile('C:/Users/14694/Documents/Codex/D-drive-transfer/Codex Projects/SRT','engineering','srt-assetto-corsa','release-r22');
file=fullfile(root,'R20_18x6_rim6','R20_18x6_rim6_refit.tir');
a=linspace(-12,12,4801)'*pi/180;k=linspace(-.2,.2,4001)';
loads=[200 400 600 656.86575694 718.98674306 800 1000 1200];
rows=[];
for fz=loads
 [fx,~]=magicformula(file,k,zeros(size(k)),fz,82737.09,0,10);
 [~,fy]=magicformula(file,zeros(size(a)),a,fz,82737.09,0,10);
 [px,ix]=max(abs(fx));[py,iy]=max(abs(fy));
 [~,fp]=magicformula(file,0,0.001,fz,82737.09,0,10);
 [~,fm]=magicformula(file,0,-0.001,fz,82737.09,0,10);
 [~,fycam]=magicformula(file,zeros(size(a)),a,fz,82737.09,2*pi/180,10);
 rows=[rows;fz px py abs(k(ix)) abs(a(iy))*180/pi abs(fp-fm)/.002 max(abs(fycam))];
end
writematrix(rows,fullfile(out,'r20-force-samples.csv'));
fid=fopen(fullfile(out,'sampling-complete.txt'),'w');fprintf(fid,'MF6.1 sweeps completed');fclose(fid);


